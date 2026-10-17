"""Isolated Android inspection fixtures; no SDK or actual application needed."""
import hashlib
from pathlib import Path
import subprocess
import zipfile
from unittest.mock import patch

import pytest

from sales_pro_qa.apk import find_android_tool, inspect_apk, parse_manifest, parse_signature, render_apk_report, run_tool
from sales_pro_qa.apk_cli import main, validate_output
from sales_pro_qa.apk_permissions import describe_permission

MANIFEST = '''<manifest xmlns:android="http://schemas.android.com/apk/res/android"
package="org.example.synthetic" android:versionName="1.0" android:versionCode="7">
<uses-sdk android:minSdkVersion="24" android:targetSdkVersion="36"/>
<uses-permission android:name="android.permission.CAMERA"/>
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="32"/>
<uses-permission-sdk-23 android:name="org.example.synthetic.CUSTOM"/>
<application android:label="Synthetic"/>
</manifest>'''
CERT = '''Verifies
Verified using v1 scheme (JAR signing): false
Verified using v2 scheme (APK Signature Scheme v2): true
Signer #1 certificate DN: C=US, O=Android, CN=Android Debug
Signer #1 certificate SHA-256 digest: ''' + 'ab' * 32 + '''
Signer #1 key algorithm: RSA
Signer #1 key size (bits): 2048
'''


@pytest.fixture
def apk(tmp_path):
    p = tmp_path / 'APK input' / 'synthetic.apk'
    p.parent.mkdir()
    with zipfile.ZipFile(p, 'w') as z:
        z.writestr('AndroidManifest.xml', 'synthetic binary manifest placeholder')
    return p


def test_manifest_all_fields_and_permission_constraints():
    data = parse_manifest(MANIFEST)
    assert (data['package_name'], data['version_name'], data['version_code']) == ('org.example.synthetic', '1.0', '7')
    assert (data['min_sdk'], data['target_sdk'], data['label']) == ('24', '36', 'Synthetic')
    assert len(data['permissions']) == 3
    assert any('maxSdkVersion=32' in c for c in data['permission_constraints'])
    assert any('SDK >= 23' in c for c in data['permission_constraints'])


@pytest.mark.parametrize('xml', ['not XML', '<manifest/>', '<wrong package="x"/>'])
def test_invalid_analyzer_output_rejected(xml):
    with pytest.raises(ValueError):
        parse_manifest(xml)


def test_debug_certificate_public_details_and_warning():
    result = parse_signature(CERT)
    cert = result['certificates'][0]
    assert cert == {'signer': '1', 'format': 'X.509', 'sha256': 'ab'*32, 'key_algorithm': 'RSA', 'key_size': '2048', 'debug': True}
    report = render_apk_report({'permissions': [], 'signature': {'status': 'PASS', **result}})
    assert 'Debug' in report and 'ليس دليلًا على برمجية خبيثة' in report
    assert 'CN=Android Debug' not in report


def test_non_debug_does_not_imply_trusted_release():
    assert not parse_signature(CERT.replace('Android Debug', 'Example Release'))['certificates'][0]['debug']


def test_multiple_signers_and_malformed_fingerprint():
    assert len(parse_signature(CERT + CERT.replace('#1', '#2'))['certificates']) == 2
    with pytest.raises(ValueError, match='fingerprint'):
        parse_signature(CERT.replace('ab'*32, 'invalid'))


def test_analyzer_executes_and_preserves_apk(apk):
    before = apk.read_bytes()
    with patch('sales_pro_qa.apk.find_android_tool', side_effect=['/sdk space/apkanalyzer.bat', None]), patch('sales_pro_qa.apk.subprocess.run', return_value=subprocess.CompletedProcess([], 0, MANIFEST, '')) as run:
        data = inspect_apk(apk, apkanalyzer='/sdk space/apkanalyzer.bat')
    assert run.call_args.args[0] == ['/sdk space/apkanalyzer.bat', 'manifest', 'print', str(apk)]
    assert data['sha256'] == hashlib.sha256(before).hexdigest()
    assert data['size_bytes'] == len(before)
    assert data['structure'] == 'PASS'
    assert data['signature']['status'] == 'NOT_RUN'
    assert apk.read_bytes() == before


def test_analyzer_fallback_when_aapt_missing(apk):
    with patch('sales_pro_qa.apk.find_android_tool', side_effect=[None, '/sdk/apkanalyzer', None]), patch('sales_pro_qa.apk.subprocess.run', return_value=subprocess.CompletedProcess([], 0, MANIFEST, '')):
        assert inspect_apk(apk)['backend'] == 'apkanalyzer'


def test_analyzer_discovered_in_sdk_cmdline_tools(tmp_path, monkeypatch):
    tool = tmp_path / 'Android SDK' / 'cmdline-tools' / 'latest' / 'bin' / 'apkanalyzer.bat'
    tool.parent.mkdir(parents=True)
    tool.touch()
    with patch('sales_pro_qa.apk.shutil.which', return_value=None):
        assert find_android_tool('apkanalyzer', sdk_root=str(tmp_path/'Android SDK')) == str(tool)


def test_no_sdk_is_not_a_pass(apk):
    with patch('sales_pro_qa.apk.find_android_tool', return_value=None):
        with pytest.raises(ValueError, match='unavailable'):
            inspect_apk(apk)


def test_corrupt_zip_crc_is_rejected_before_tool(apk):
    content = apk.read_bytes()
    apk.write_bytes(content.replace(b'synthetic binary', b'SYNTHETIC binary'))
    with patch('sales_pro_qa.apk.run_tool') as run:
        with pytest.raises(ValueError, match='ZIP|CRC'):
            inspect_apk(apk)
    run.assert_not_called()


@pytest.mark.parametrize('timeout', [0, -1, float('inf'), float('nan')])
def test_invalid_timeout_rejected(apk, timeout):
    with pytest.raises(ValueError, match='Timeout'):
        inspect_apk(apk, timeout=timeout)


def test_report_does_not_persist_raw_output_or_private_paths():
    data = {'permissions': ['android.permission.CAMERA', 'org.example.CUSTOM'],
            'signature': {'status': 'ERROR', 'command': ['/private/alice/apksigner', 'verify', '/private/alice/input.apk'],
                          'returncode': 1, 'stdout': 'SECRET_TOKEN=synthetic', 'stderr': 'personal email and secret'}}
    report = render_apk_report(data)
    for secret in ['SECRET_TOKEN', 'personal email', '/private/alice']:
        assert secret not in report
    assert 'CAMERA' in report and 'صلاحية خاصة' in report
    assert '\n\n## ' in report and '\\n' not in report


@pytest.mark.parametrize('name', ['android.permission.CAMERA', 'android.permission.UNKNOWN_NEW', 'org.example.CUSTOM'])
def test_permission_meaning_and_limits(name):
    meaning, limits = describe_permission(name)
    assert meaning and limits


def test_report_cannot_overwrite_apk_or_hardlink(apk, tmp_path):
    with pytest.raises(ValueError, match='overwrite'):
        validate_output(str(apk), str(apk))
    link = tmp_path / 'alias.md'
    link.hardlink_to(apk)
    with pytest.raises(ValueError, match='overwrite'):
        validate_output(str(apk), str(link))


def test_standalone_cli_bad_manifest_does_not_write_report(apk, tmp_path, monkeypatch):
    report = tmp_path / 'report.md'
    monkeypatch.setattr('sys.argv', ['sales-pro-apk', '--apk', str(apk), '--output', str(report)])
    with patch('sales_pro_qa.apk.find_android_tool', return_value='/tools/aapt'), patch('sales_pro_qa.apk.subprocess.run', return_value=subprocess.CompletedProcess([], 0, 'not metadata', '')):
        with pytest.raises(SystemExit) as error:
            main()
    assert error.value.code != 0
    assert not report.exists()


def test_windows_batch_rejects_shell_expansion():
    with patch('sales_pro_qa.apk.os.name', 'nt'), patch('sales_pro_qa.apk.subprocess.run') as run:
        with pytest.raises(ValueError, match='shell characters'):
            run_tool(['C:\\Android\\apkanalyzer.bat', 'manifest', 'print', 'C:\\APK\\%SECRET%.apk'], 60)
    run.assert_not_called()


def test_zero_exit_without_certificate_is_error(apk):
    with patch('sales_pro_qa.apk.find_android_tool', side_effect=['/tools/apkanalyzer', '/tools/apksigner']), patch('sales_pro_qa.apk.subprocess.run') as run:
        run.side_effect = [subprocess.CompletedProcess([], 0, MANIFEST, ''), subprocess.CompletedProcess([], 0, '', '')]
        result = inspect_apk(apk, apkanalyzer='/tools/apkanalyzer')
    assert result['signature']['status'] == 'ERROR'
    assert result['signature']['error_kind'] == 'certificate_parse'


def test_standalone_cli_generates_arabic_report(apk, tmp_path, monkeypatch):
    output = tmp_path / 'report folder' / 'report.md'
    monkeypatch.setattr('sys.argv', ['sales-pro-apk', '--apk', str(apk), '--apkanalyzer', '/tools/apkanalyzer', '--output', str(output)])
    with patch('sales_pro_qa.apk.find_android_tool', side_effect=['/tools/apkanalyzer', None]), patch('sales_pro_qa.apk.subprocess.run', return_value=subprocess.CompletedProcess([], 0, MANIFEST, '')):
        main()
    report = output.read_text(encoding='utf-8')
    assert 'org.example.synthetic' in report
    assert 'NOT_RUN' in report
    assert '\n\n## ' in report


def test_render_without_tool_evidence_does_not_claim_manifest_success():
    report = render_apk_report({'permissions': []})
    assert 'نتيجة قراءة manifest: NOT_RUN' in report


@pytest.mark.parametrize('declaration', [
    '<!DOCTYPE manifest [<!ENTITY package "org.example.synthetic">]>',
    '<!DOCTYPE manifest SYSTEM "file:///nonexistent/synthetic.dtd">',
])
def test_manifest_rejects_dtd_and_entity_declarations(declaration):
    with pytest.raises(ValueError, match='DTD|entity'):
        parse_manifest(declaration + '<manifest package="org.example.synthetic"/>')


@pytest.mark.parametrize('entry', ['sales_pro_qa.cli', 'sales_pro_qa.apk_cli'])
def test_cli_output_write_error_is_readable(tmp_path, monkeypatch, entry):
    import importlib
    cli = importlib.import_module(entry)
    blocked = tmp_path / 'blocked'
    blocked.write_text('existing user file')
    monkeypatch.setattr('sys.argv', ['qa', '--apk', 'synthetic.apk', '--output', str(blocked/'report.md')])
    data = {'permissions': [], 'signature': {'status': 'NOT_RUN'}}
    with patch(entry + '.inspect_apk', return_value=data):
        with pytest.raises(SystemExit) as error:
            cli.main()
    assert error.value.code == 2
    assert blocked.read_text() == 'existing user file'
