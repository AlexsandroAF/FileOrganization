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
        self.log_file = os.path.join(self.log_dir, "app.log")
        self.logger = logging.getLogger("OrganizadorDePastas")
        self.logger.setLevel(logging.INFO)

        # Evita duplicação de handlers
        if not self.logger.handlers:
            # Remove handlers antigos se existirem
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)

            # Cria um novo handler
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
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

    def clear_log_file(self):
        """Limpa o arquivo de log (não afeta o banco de dados)."""
        try:
            # Fecha handlers existentes
            for handler in self.logger.handlers[:]:
                handler.close()
                self.logger.removeHandler(handler)

            # Limpa o arquivo
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write('')

            # Recria o handler
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            return True
        except Exception as e:
            print(f"Erro ao limpar arquivo de log: {e}")
            return False