from task_cli.infrastructure.config import Config
from task_cli.ui.messages.commands import implemented_langs


class FakeConfig(Config):
    def __init__(self, lang: str):
        if lang not in implemented_langs: raise ValueError("Idioma inválido")
        self.data = {"lang": lang, "repo_type": "sqlite", "style": "ascii"}

    def get(self, key, default=None):
        if key in self.data.keys():
            return self.data.get(key, default)
        else:
            raise ValueError("Eso no está acá")

    def change_config(self, key, value):
        if key in self.data: self.data[key] = value
        else: raise ValueError("Eso no se puede poner acá")