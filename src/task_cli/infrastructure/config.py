import json
from abc import ABC
from pathlib import Path

from task_cli.infrastructure.enums import RepoType

class Config(ABC):
    def get(self, key: str, default=None):
        pass
    def change_config(self, key: str, value: str) -> None:
        pass

class ConfigJson(Config):
    default_values: dict = {
        "lang": "en",
        "style": "utf-8",
        "repo_type": RepoType.SQLITE.value,
        "current_user": "guest",
    }
    def __init__(self, path: Path) -> None:
        self.path = path
        self.configs = {}
        self._load()

    def _ensure_file(self) -> None:
        if not self.path.exists():
            self.path.write_text(json.dumps(self.default_values), encoding="utf-8")

    def _load(self):
        self._ensure_file()
        with open(self.path, 'r', encoding='utf-8') as file:
            self.configs = json.load(file)

    def _save(self):
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(self.configs, file, ensure_ascii=False, indent=4)

    def change_config(self, key: str, value: str) -> None:
        if key in self.configs:
            self.configs[key] = value
        else:
            raise ValueError("Eso no se puede poner acá")
        self._save()

    def get(self, key: str, default=None):
        if key in self.configs.keys():
            return self.configs.get(key, default)
        else:
            raise ValueError("Eso no está acá")