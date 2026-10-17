"""Synthetic aapt output only; no real Android application is executed."""
import subprocess
import zipfile
from unittest.mock import patch

import pytest

from sales_pro_qa.apk import find_android_tool, inspect_apk, parse_badging, render_apk_report
from sales_pro_qa.cli import main

BADGING = """package: name='org.example.synthetic' versionCode='8' versionName='1.2'
sdkVersion:'23'
targetSdkVersion:'35'
application-label:'Synthetic QA'
uses-permission: name='android.permission.INTERNET'
uses-permission-sdk-23: name='android.permission.CAMERA'
uses-permission: name='android.permission.CAMERA'
"""


def test_parse_metadata_and_deduplicate_permissions():
    data = parse_badging(BADGING)
    assert data == {
        'package_name': 'org.example.synthetic', 'version_code': '8',
        'version_name': '1.2', 'min_sdk': '23', 'target_sdk': '35',
        'label': 'Synthetic QA',
        'permissions': ['android.permission.CAMERA', 'android.permission.INTERNET'],
    }


def test_missing_sdk_is_unknown():
    assert parse_badging("package: name='org.example.synthetic'")['target_sdk'] is None


def test_malformed_output_fails():
    with pytest.raises(ValueError, match='package'):
        parse_badging('not valid badging output')


def test_inspection_uses_read_only_tool_and_hashes_file(tmp_path):
    apk = tmp_path / 'synthetic.apk'
    with zipfile.ZipFile(apk, 'w') as z:
        z.writestr('AndroidManifest.xml', b'synthetic manifest')
    original = apk.read_bytes()
    with patch('sales_pro_qa.apk.find_android_tool', side_effect=['/tools/aapt', None]), patch('sales_pro_qa.apk.subprocess.run') as run:
        run.return_value = subprocess.CompletedProcess([], 0, BADGING, '')
        data = inspect_apk(apk)
        run.assert_called_once_with(
            ['/tools/aapt', 'dump', 'badging', str(apk.resolve())],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
        )
    assert data['filename'] == 'synthetic.apk'
    assert len(data['sha256']) == 64
    assert apk.read_bytes() == original
    report = render_apk_report(data)
    assert '\n\n## الصلاحيات المطلوبة\n\n' in report
    assert '\\n' not in report
    assert 'NOT_RUN' in report


@pytest.mark.parametrize('error, message', [
    (FileNotFoundError('missing tool'), 'ERROR'),
    (subprocess.TimeoutExpired('aapt', 60), '60 seconds'),

])
def test_tool_failure_is_explicit(tmp_path, error, message):
    apk = tmp_path / 'synthetic.apk'
    with zipfile.ZipFile(apk, 'w') as z:
        z.writestr('AndroidManifest.xml', b'synthetic manifest')
    with patch('sales_pro_qa.apk.find_android_tool', return_value='/tools/aapt'), patch('sales_pro_qa.apk.subprocess.run', side_effect=error):
        with pytest.raises(ValueError, match=message):
            inspect_apk(apk)


def test_cli_static_mode(tmp_path, monkeypatch):
    output = tmp_path / 'report.md'
    monkeypatch.setattr('sys.argv', ['sales-pro-qa', '--apk', 'synthetic.apk', '--output', str(output)])
    metadata = {'filename': 'synthetic.apk', **parse_badging(BADGING)}
    with patch('sales_pro_qa.cli.inspect_apk', return_value=metadata):
        main()
    assert 'org.example.synthetic' in output.read_text()


def test_missing_apk_fails(tmp_path):
    with pytest.raises(FileNotFoundError):
        inspect_apk(tmp_path / 'missing.apk')


def test_invalid_apk_never_runs_tool(tmp_path):
    apk = tmp_path / 'pointer.apk'
    apk.write_text('version https://git-lfs.github.com/spec/v1\n')
    with patch('sales_pro_qa.apk.subprocess.run') as run:
        with pytest.raises(ValueError, match='Invalid APK ZIP'):
            inspect_apk(apk)
    run.assert_not_called()


def test_sdk_tool_paths_with_spaces_and_versions(tmp_path, monkeypatch):
    sdk = tmp_path / 'Android SDK'
    for version in ['9.0.0', '36.0.0']:
        directory = sdk / 'build-tools' / version
        directory.mkdir(parents=True)
        (directory / 'aapt.exe').touch()
    monkeypatch.delenv('ANDROID_SDK_ROOT', raising=False)
    monkeypatch.delenv('ANDROID_HOME', raising=False)
    with patch('sales_pro_qa.apk.shutil.which', return_value=None):
        tool = find_android_tool('aapt', sdk_root=str(sdk))
    assert tool == str(sdk / 'build-tools' / '36.0.0' / 'aapt.exe')


@pytest.mark.parametrize('code, output, expected', [
    (0, 'Verifies\nVerified using v2 scheme: true\nSigner #1 certificate SHA-256 digest: ' + 'a' * 64, 'PASS'),
    (1, 'DOES NOT VERIFY', 'FAIL'),
])
def test_signature_outcome_retains_command_and_output(tmp_path, code, output, expected):
    apk = tmp_path / 'synthetic.apk'
    with zipfile.ZipFile(apk, 'w') as z:
        z.writestr('AndroidManifest.xml', b'synthetic manifest')
    with patch('sales_pro_qa.apk.find_android_tool', side_effect=['/tools/aapt', '/tools/apksigner']), patch('sales_pro_qa.apk.subprocess.run') as run:
        run.side_effect = [subprocess.CompletedProcess([], 0, BADGING, ''),
                           subprocess.CompletedProcess([], code, output, 'diagnostic')]
        data = inspect_apk(apk)
    assert data['signature']['status'] == expected
    assert data['signature']['returncode'] == code
    assert data['signature']['stdout'] == output
    assert data['signature']['command'] == ['/tools/apksigner', 'verify', '--verbose', '--print-certs', str(apk)]
    assert expected in render_apk_report(data)


@pytest.mark.parametrize('code, output', [(1, BADGING), (0, 'unparseable output')])
def test_bad_tool_result_cannot_pass(tmp_path, code, output):
    apk = tmp_path / 'synthetic.apk'
    with zipfile.ZipFile(apk, 'w') as z:
        z.writestr('AndroidManifest.xml', b'synthetic manifest')
    with patch('sales_pro_qa.apk.find_android_tool', return_value='/tools/aapt'), patch('sales_pro_qa.apk.subprocess.run', return_value=subprocess.CompletedProcess([], code, output, 'error')):
        with pytest.raises(ValueError):
            inspect_apk(apk)


def test_cli_signature_failure_writes_evidence_and_exits_nonzero(tmp_path, monkeypatch):
    output = tmp_path / 'failure.md'
    monkeypatch.setattr('sys.argv', ['sales-pro-qa', '--apk', 'fixture.apk', '--output', str(output)])
    data = {**parse_badging(BADGING), 'signature': {'status': 'FAIL', 'command': ['apksigner'], 'returncode': 1, 'stdout': '', 'stderr': 'DOES NOT VERIFY'}}
    with patch('sales_pro_qa.cli.inspect_apk', return_value=data):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 1
    assert 'FAIL' in output.read_text()
    assert 'DOES NOT VERIFY' not in output.read_text()


def test_signature_timeout_is_error_not_success(tmp_path):
    apk = tmp_path / 'synthetic.apk'
    with zipfile.ZipFile(apk, 'w') as z:
        z.writestr('AndroidManifest.xml', b'synthetic manifest')
    with patch('sales_pro_qa.apk.find_android_tool', side_effect=['/tools/aapt', '/tools/apksigner']), patch('sales_pro_qa.apk.subprocess.run') as run:
        run.side_effect = [subprocess.CompletedProcess([], 0, BADGING, ''),
                           subprocess.TimeoutExpired('apksigner', 1)]
        data = inspect_apk(apk, timeout=1)
    assert data['signature']['status'] == 'ERROR'
    assert data['signature']['returncode'] is None
    assert '1 seconds' in data['signature']['stderr']


def test_real_subprocess_exit_and_timeout():
    import sys
    from sales_pro_qa.apk import run_tool
    result = run_tool([sys.executable, '-c', 'import sys; print("synthetic"); sys.exit(3)'], 5)
    assert result['status'] == 'FAIL'
    assert result['returncode'] == 3
    assert result['stdout'].strip() == 'synthetic'
    timeout = run_tool([sys.executable, '-c', 'import time; time.sleep(10)'], 0.05)
    assert timeout['status'] == 'ERROR'
    assert timeout['returncode'] is None


def test_zip_without_manifest_is_rejected(tmp_path):
    apk = tmp_path / 'empty.apk'
    with zipfile.ZipFile(apk, 'w'):
        pass
    with pytest.raises(ValueError, match='AndroidManifest.xml'):
        inspect_apk(apk)
