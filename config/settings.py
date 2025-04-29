# src/config/settings.py
import os
import json


class Settings:
    def __init__(self, settings_file="config.json"):
        self.settings_file = settings_file
        self.settings = self._load_settings()

    def _load_settings(self):
        """Carrega as configurações do arquivo ou cria padrão."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        # Configurações padrão
        return {
            "auto_start": True,
            "show_notifications": True,
            "auto_organize_on_start": True,
            "check_interval": 1.0,  # segundos
            "last_folders": []
        }

    def save(self):
        """Salva as configurações no arquivo."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception:
            return False

    def get(self, key, default=None):
        """Obtém uma configuração pelo nome."""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Define uma configuração."""
        self.settings[key] = value
        self.save()