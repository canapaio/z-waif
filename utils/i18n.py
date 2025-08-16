# -*- coding: utf-8 -*-
"""
Sistema di Internazionalizzazione per Z-Waif

Modulo per gestire traduzioni multiple lingue con fallback automatico.
Supporta caricamento dinamico e configurazione flessibile.

Autore: Kael (Adattamento Italiano Z-Waif)
Data: 2025
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class I18nManager:
    """Gestore principale per l'internazionalizzazione."""
    
    def __init__(self, default_locale: str = 'en_US'):
        """Inizializza il gestore i18n.
        
        Args:
            default_locale: Lingua di default (es. 'en_US', 'it_IT')
        """
        self.default_locale = default_locale
        # Read locale from environment variable, fallback to default
        self.current_locale = os.getenv('UI_LANGUAGE', default_locale)
        self.fallback_locale = 'en_US'
        
        # Cache delle traduzioni caricate
        self.translations: Dict[str, Dict[str, Any]] = {}
        
        # Directory base per le traduzioni
        self.locales_dir = Path(__file__).parent.parent / 'locales'
        
        # Configurazione lingue disponibili
        self.locale_config = {}
        
        # Inizializzazione
        self._load_locale_config()
        self._load_translations()
    
    def _load_locale_config(self) -> None:
        """Carica la configurazione delle lingue disponibili."""
        config_path = self.locales_dir / 'locale_config.json'
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.locale_config = json.load(f)
                    
                # Aggiorna impostazioni da config
                self.fallback_locale = self.locale_config.get('fallback_locale', 'en_US')
                
            except (json.JSONDecodeError, IOError) as e:
                print(f"[i18n] Errore caricamento config lingue: {e}")
                # Fallback a configurazione di default
                self.locale_config = {
                    'default_locale': 'en_US',
                    'available_locales': {
                        'en_US': {'name': 'English (US)', 'native_name': 'English'},
                        'it_IT': {'name': 'Italian (Italy)', 'native_name': 'Italiano'},
                        'ru_RU': {'name': 'Russian (Russia)', 'native_name': 'Русский'}
                    },
                    'fallback_locale': 'en_US'
                }
    
    def _load_translations(self) -> None:
        """Carica le traduzioni per la lingua corrente."""
        self._load_locale_translations(self.current_locale)
        
        # Carica anche il fallback se diverso
        if self.current_locale != self.fallback_locale:
            self._load_locale_translations(self.fallback_locale)
    
    def _load_locale_translations(self, locale: str) -> None:
        """Carica le traduzioni per una specifica lingua.
        
        Args:
            locale: Codice lingua (es. 'it_IT')
        """
        locale_dir = self.locales_dir / locale
        
        if not locale_dir.exists():
            print(f"[i18n] Directory lingua non trovata: {locale_dir}")
            return
        
        # Inizializza dizionario per questa lingua
        if locale not in self.translations:
            self.translations[locale] = {}
        
        # Carica tutti i file JSON nella directory
        translation_files = ['ui.json', 'messages.json', 'config.json', 'rag.json']
        
        for filename in translation_files:
            file_path = locale_dir / filename
            category = filename.replace('.json', '')
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.translations[locale][category] = json.load(f)
                        
                except (json.JSONDecodeError, IOError) as e:
                    print(f"[i18n] Errore caricamento {file_path}: {e}")
            else:
                print(f"[i18n] File traduzione non trovato: {file_path}")
    
    def get_text(self, key: str, category: str = 'ui', locale: Optional[str] = None, **kwargs) -> str:
        """Recupera un testo tradotto.
        
        Args:
            key: Chiave del testo (supporta notazione punto es. 'buttons.send')
            category: Categoria del testo ('ui', 'messages', 'config', 'rag')
            locale: Lingua specifica (None = usa corrente)
            **kwargs: Variabili per interpolazione nel testo
            
        Returns:
            Testo tradotto o chiave originale se non trovato
        """
        target_locale = locale or self.current_locale
        
        # Prova prima con la lingua richiesta
        text = self._get_text_from_locale(key, category, target_locale)
        
        # Se non trovato, prova con fallback
        if text is None and target_locale != self.fallback_locale:
            text = self._get_text_from_locale(key, category, self.fallback_locale)
        
        # Se ancora non trovato, ritorna la chiave
        if text is None:
            print(f"[i18n] Traduzione non trovata: {category}.{key}")
            return key
        
        # Interpolazione variabili se presenti
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError) as e:
                print(f"[i18n] Errore interpolazione per {key}: {e}")
        
        return text
    
    def _get_text_from_locale(self, key: str, category: str, locale: str) -> Optional[str]:
        """Recupera testo da una specifica lingua.
        
        Args:
            key: Chiave del testo (supporta notazione punto)
            category: Categoria del testo
            locale: Codice lingua
            
        Returns:
            Testo trovato o None
        """
        if locale not in self.translations:
            return None
        
        if category not in self.translations[locale]:
            return None
        
        # Naviga la struttura usando la notazione punto
        data = self.translations[locale][category]
        keys = key.split('.')
        
        try:
            for k in keys:
                data = data[k]
            return str(data)
        except (KeyError, TypeError):
            return None
    
    def set_locale(self, locale: str) -> bool:
        """Cambia la lingua corrente.
        
        Args:
            locale: Nuovo codice lingua
            
        Returns:
            True se cambiamento riuscito, False altrimenti
        """
        if locale not in self.get_available_locales():
            print(f"[i18n] Lingua non disponibile: {locale}")
            return False
        
        old_locale = self.current_locale
        self.current_locale = locale
        
        # Carica traduzioni se non già caricate
        if locale not in self.translations:
            self._load_locale_translations(locale)
        
        print(f"[i18n] Lingua cambiata da {old_locale} a {locale}")
        return True
    
    def get_available_locales(self) -> Dict[str, Dict[str, str]]:
        """Ritorna le lingue disponibili.
        
        Returns:
            Dizionario con info sulle lingue disponibili
        """
        return self.locale_config.get('available_locales', {})
    
    def get_current_locale(self) -> str:
        """Ritorna la lingua corrente."""
        return self.current_locale
    
    def get_whisper_language_code(self, locale: Optional[str] = None) -> str:
        """Ritorna il codice lingua per Whisper.
        
        Args:
            locale: Lingua specifica (None = usa corrente)
            
        Returns:
            Codice lingua per Whisper (es. 'en', 'it')
        """
        target_locale = locale or self.current_locale
        available = self.get_available_locales()
        
        if target_locale in available:
            return available[target_locale].get('whisper_code', 'en')
        
        return 'en'  # Default fallback
    
    def reload_translations(self) -> None:
        """Ricarica tutte le traduzioni."""
        self.translations.clear()
        self._load_locale_config()
        self._load_translations()
        print(f"[i18n] Traduzioni ricaricate per {self.current_locale}")


# Istanza globale del gestore i18n
_i18n_manager = None


def init_i18n(locale: str = 'en_US') -> I18nManager:
    """Inizializza il sistema i18n.
    
    Args:
        locale: Lingua di default
        
    Returns:
        Istanza del gestore i18n
    """
    global _i18n_manager
    _i18n_manager = I18nManager(locale)
    return _i18n_manager


def get_i18n_manager() -> I18nManager:
    """Ritorna l'istanza corrente del gestore i18n."""
    global _i18n_manager
    if _i18n_manager is None:
        _i18n_manager = I18nManager()
    return _i18n_manager


def _(key: str, category: str = 'ui', **kwargs) -> str:
    """Funzione di convenienza per ottenere traduzioni.
    
    Args:
        key: Chiave del testo
        category: Categoria del testo
        **kwargs: Variabili per interpolazione
        
    Returns:
        Testo tradotto
    """
    return get_i18n_manager().get_text(key, category, **kwargs)


def set_language(locale: str) -> bool:
    """Funzione di convenienza per cambiare lingua.
    
    Args:
        locale: Nuovo codice lingua
        
    Returns:
        True se cambiamento riuscito
    """
    return get_i18n_manager().set_locale(locale)


def get_current_language() -> str:
    """Ritorna la lingua corrente."""
    return get_i18n_manager().get_current_locale()


def get_whisper_language() -> str:
    """Ritorna il codice lingua per Whisper."""
    return get_i18n_manager().get_whisper_language_code()


# Auto-inizializzazione con lingua da variabile ambiente
if __name__ != '__main__':
    import utils.settings
    
    # Prova a leggere lingua da settings
    try:
        default_lang = getattr(utils.settings, 'language', 'en_US')
    except:
        default_lang = 'en_US'
    
    init_i18n(default_lang)