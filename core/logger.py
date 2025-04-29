# src/core/logger.py
import os
import logging
from datetime import datetime


class Logger:
    def __init__(self, log_dir="logs", db=None):
        self.db = db

        # Configura o diretório de logs
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

        # Configura o logger do Python
        log_file = os.path.join(self.log_dir, "app.log")
        self.logger = logging.getLogger("OrganizadorDePastas")
        self.logger.setLevel(logging.INFO)

        # Evita duplicação de handlers
        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, action, details=""):
        """Registra uma ação informativa."""
        message = f"{action}: {details}"
        self.logger.info(message)

        if self.db:
            self.db.add_log(action, details)

    def error(self, action, details=""):
        """Registra um erro."""
        message = f"{action}: {details}"
        self.logger.error(message)

        if self.db:
            self.db.add_log(f"ERRO - {action}", details)

    def warning(self, action, details=""):
        """Registra um aviso."""
        message = f"{action}: {details}"
        self.logger.warning(message)

        if self.db:
            self.db.add_log(f"AVISO - {action}", details)