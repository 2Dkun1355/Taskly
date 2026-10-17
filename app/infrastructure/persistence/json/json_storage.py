import json
from pathlib import Path


class JsonStorage:
    """Читає та записує JSON-дані."""

    def __init__(self, file_path: Path | str | None = None):
        project_root = Path(__file__).resolve().parents[4]
        self._file_path = (
            Path(file_path)
            if file_path is not None
            else project_root / "data" / "tasks.json"
        )

    def load(self) -> list[dict]:
        """Завантажує дані з файлу."""
        if not self._file_path.exists():
            return []

        with self._file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("JSON-файл повинен містити список")

        return data

    def save(self, data: list[dict]):
        """Безпечно записує дані у файл."""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self._file_path.with_suffix(
            self._file_path.suffix + ".tmp"
        )

        try:
            with temporary_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.write("\n")

            temporary_path.replace(self._file_path)
        finally:
            if temporary_path.exists():
                temporary_path.unlink()
