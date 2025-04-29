# src/db/database.py
import os
import sqlite3
import datetime


class Database:
    def __init__(self, db_file="app_data.db"):
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(os.path.abspath(db_file)), exist_ok=True)

        self.db_file = db_file
        self.conn = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Conecta ao banco de dados SQLite."""
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def _create_tables(self):
        """Cria as tabelas se não existirem."""
        try:
            cursor = self.conn.cursor()

            # Tabela de pastas monitoradas
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitored_folders (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE,
                active BOOLEAN
            )
            ''')

            # Tabela de logs
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                action TEXT,
                details TEXT
            )
            ''')

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao criar tabelas: {e}")

    def add_folder(self, path):
        """Adiciona uma pasta para monitoramento."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO monitored_folders (path, active) VALUES (?, ?)",
                           (path, True))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar pasta: {e}")
            return None

    def remove_folder(self, folder_id):
        """Remove uma pasta do monitoramento."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM monitored_folders WHERE id = ?", (folder_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao remover pasta: {e}")
            return False

    def get_all_folders(self):
        """Retorna todas as pastas monitoradas."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM monitored_folders WHERE active = 1")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao buscar pastas: {e}")
            return []

    def add_log(self, action, details):
        """Adiciona um registro de log."""
        try:
            cursor = self.conn.cursor()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO logs (timestamp, action, details) VALUES (?, ?, ?)",
                           (timestamp, action, details))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar log: {e}")
            return None

    def get_logs(self, limit=100):
        """Retorna os logs mais recentes."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao buscar logs: {e}")
            return []

    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()