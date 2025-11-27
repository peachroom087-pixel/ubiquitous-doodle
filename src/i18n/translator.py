from .loader import LocaleLoader
import sys


class Translator:
    def __init__(self, locale_loader: LocaleLoader):
        self.loader = locale_loader
        self._current_lang = None

    def set_language(self, lang: str):
        """Set the current language."""
        self._current_lang = lang

    def _(self, key: str, **kwargs) -> str:
        """Translate a key with optional formatting."""
        if self._current_lang is None:
            raise ValueError("Language not set")
        
        try:
            # First try to load from main locale files
            locale_data = self.loader.load_locale(self._current_lang)
            if key in locale_data:
                template = locale_data[key]
            else:
                # Try to load from error locale file
                error_locale_data = self.loader.load_error_locale()
                if key in error_locale_data:
                    template = error_locale_data[key]
                else:
                    raise KeyError(f"Translation key '{key}' not found in any locale files")
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1003)  # MISSING_LOCALE error code
        
        if kwargs:
            try:
                return template.format(**kwargs)
            except KeyError:
                raise KeyError(f"Missing formatting argument for key '{key}'")
        return template