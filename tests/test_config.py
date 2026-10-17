import json
import pytest
from sales_pro_qa.config import load_config

def test_load_valid_config(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({
        "project_name": "Demo", "language": "ar", "evidence_root": "evidence"
    }), encoding="utf-8")
    assert load_config(path)["language"] == "ar"

def test_missing_required_key_fails(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"project_name":"Demo"}', encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required"):
        load_config(path)

def test_invalid_language_fails(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({
        "project_name": "Demo", "language": "fr", "evidence_root": "evidence"
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="language"):
        load_config(path)
