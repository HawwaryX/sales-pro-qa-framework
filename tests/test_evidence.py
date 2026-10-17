import pytest
from sales_pro_qa.evidence import build_manifest

def test_manifest_marks_missing_file(tmp_path):
    manifest = build_manifest([{"test_id": "T-1", "path": "missing.png"}], tmp_path)
    assert manifest["items"][0]["exists"] is False
    assert manifest["items"][0]["path"] == "missing.png"

def test_manifest_rejects_path_escape(tmp_path):
    with pytest.raises(ValueError, match="inside evidence root"):
        build_manifest([{"test_id": "T-1", "path": "../outside.png"}], tmp_path)
