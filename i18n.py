import json
from pathlib import Path
from typing import Callable, Dict, List, Optional

_translations = {}
_default_lang = "en"

def load_translations(locales_dir: Path = Path("locales")):
    """Load all translation files from the locales directory."""
    global _translations
    if not locales_dir.exists() or not locales_dir.is_dir():
        print(f"Warning: Locales directory '{locales_dir}' not found.")
        return

    for lang_file in locales_dir.glob("*.json"):
        lang = lang_file.stem
        with open(lang_file, "r", encoding="utf-8") as f:
            _translations[lang] = json.load(f)
    
    if _translations:
        print(f"Loaded translations for: {list(_translations.keys())}")

def get_translator(lang: str) -> Callable[[str, ...], str]:
    """
    Returns a function that translates a key into the given language.
    Falls back to the default language if a key is not found.
    """
    def _(key: str, **kwargs) -> str:
        # Get the template string
        template = _translations.get(lang, {}).get(key)
        
        # Fallback to default language if key not in current language
        if template is None:
            template = _translations.get(_default_lang, {}).get(key, key)
            
        # Perform substitution
        return template.format(**kwargs)

    return _

def get_best_match_language(accept_language: Optional[str]) -> str:
    """
    Parses the Accept-Language header and returns the best-matching language.
    """
    if not accept_language or not _translations:
        return _default_lang

    available_langs = set(_translations.keys())
    
    # Example header: "fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5"
    langs = accept_language.split(",")
    for lang_entry in langs:
        lang_parts = lang_entry.strip().split(";")
        lang_code = lang_parts[0].split("-")[0] # 'fr-CH' -> 'fr'
        
        if lang_code in available_langs:
            return lang_code
            
    return _default_lang

# Initial load of translations
load_translations()
