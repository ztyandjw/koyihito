import tomli
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_path = Path(__file__).parent.parent.parent / "config.toml"
        self.config = self._load_config()

    def _load_config(self):
        with open(self.config_path, "rb") as f:
            return tomli.load(f)

    @property
    def ollama_host(self):
        return self.config["ollama"]["host"]

config = ConfigManager()