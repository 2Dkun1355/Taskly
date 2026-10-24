import json

import pytest

from infrastructure.persistence.json.json_storage import JsonStorage


def test_storage_saves_and_loads_unicode(tmp_path):
    storage = JsonStorage(tmp_path / "nested" / "tasks.json")
    data = [{"title": "Українське завдання"}]

    storage.save(data)

    assert storage.load() == data


def test_storage_returns_empty_list_for_missing_file(tmp_path):
    assert JsonStorage(tmp_path / "missing.json").load() == []


def test_storage_rejects_json_that_is_not_a_list(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text(json.dumps({"task": 1}), encoding="utf-8")

    with pytest.raises(ValueError, match="список"):
        JsonStorage(path).load()
