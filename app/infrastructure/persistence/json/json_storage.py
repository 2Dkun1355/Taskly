import json
import os
from pathlib import Path


class JsonStorage:
    def __init__(self, path: Path):
        self._path = path

    def load(self) -> dict:
        if not self._path.exists():
            return {"tasks": {}}

        with self._path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        data.setdefault("tasks", {})
        return data

    def save(self, data: dict):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self._path.with_suffix(".tmp")

        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        os.replace(temp_path, self._path)