import json
import os
from typing import Dict


class LocaleLoader:
    def __init__(self, locales_dir: str = "data/locales"):
        self.locales_dir = locales_dir
        self._locales = {}

    def load_locale(self, lang: str) -> Dict:
        """Load locale file for the specified language."""
        if lang in self._locales:
            return self._locales[lang]
        
        file_path = os.path.join(self.locales_dir, f"{lang}.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Locale file {file_path} not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            self._locales[lang] = json.load(f)
        
        return self._locales[lang]

    def load_error_locale(self) -> Dict:
        """Load error locale file."""
        file_path = os.path.join(self.locales_dir, "errors.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Error locale file {file_path} not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)