import json

class Settings:
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self._load()

    def _load(self):
        with open(self.filename, "r") as f:
            data = json.load(f)
        for k, v in data.items():
            setattr(self, k, v) 