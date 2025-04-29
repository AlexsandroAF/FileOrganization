# src/db/database.py
import os
import sqlite3
import datetime
import threading
import queue


class Database:
    def __init__(self, db_file="app_data.db"):
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(os.path.abspath(db_file)), exist_ok=True)

        self.db_file = db_file
        self.thread_local = threading.local()
        self.lock = threading.Lock()

        # Fila para operações assíncronas
        self._queue = queue.Queue()
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()

        # Conecta no thread principal
        self.get_connection()
        self._create_tables()

    def get_connection(self):
        """Obtém uma conexão específica para cada thread."""
        if not hasattr(self.thread_local, "conn"):
            try:
                self.thread_local.conn = sqlite3.connect(self.db_file)
                self.thread_local.conn.row_factory = sqlite3.Row
            except sqlite3.Error as e:
                print(f"Erro ao conectar ao banco de dados: {e}")
                return None
        return self.thread_local.conn

    def _create_tables(self):
        """Cria as tabelas se não existirem."""
        conn = self.get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()

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

            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao criar tabelas: {e}")

    def _worker(self):
        """Thread worker para processar operações assíncronas."""
        while True:
            try:
                # Obtem um item da fila (bloqueia até que um item esteja disponível)
                func, args, kwargs, result_queue = self._queue.get()

                # Executa a função
                try:
                    result = func(*args, **kwargs)
                    result_queue.put((True, result))
                except Exception as e:
                    result_queue.put((False, str(e)))
                finally:
                    self._queue.task_done()
            except Exception as e:
                print(f"Erro no worker do banco de dados: {e}")

    def execute_async(self, func, *args, **kwargs):
        """Executa uma função no thread worker."""
        result_queue = queue.Queue()
        self._queue.put((func, args, kwargs, result_queue))
        success, result = result_queue.get()
        if success:
            return result
        else:
            raise Exception(f"Erro na execução assíncrona: {result}")

    def add_folder(self, path):
        """Adiciona uma pasta para monitoramento."""
        conn = self.get_connection()
        if not conn:
            return None

        try:
            with self.lock:
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO monitored_folders (path, active) VALUES (?, ?)",
                               (path, True))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar pasta: {e}")
            return None

    def remove_folder(self, folder_id):
        """Remove uma pasta do monitoramento."""
        conn = self.get_connection()
        if not conn:
            return False

        try:
            with self.lock:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM monitored_folders WHERE id = ?", (folder_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Erro ao remover pasta: {e}")
            return False

    def get_all_folders(self):
        """Retorna todas as pastas monitoradas."""
        conn = self.get_connection()
        if not conn:
            return []

        try:
            with self.lock:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM monitored_folders WHERE active = 1")
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao buscar pastas: {e}")
            return []

    def add_log(self, action, details):
        """Adiciona um registro de log (thread-safe)."""
        # Usa o método async para garantir que seja executado no thread worker
        try:
            def _add_log(action, details):
                conn = self.get_connection()
                if not conn:
                    return None

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO logs (timestamp, action, details) VALUES (?, ?, ?)",
                               (timestamp, action, details))
                conn.commit()
                return cursor.lastrowid

            # Adiciona o log de forma assíncrona
            return self.execute_async(_add_log, action, details)
        except Exception as e:
            print(f"Erro ao adicionar log (assíncrono): {e}")
            return None

    def get_logs(self, limit=100):
        """Retorna os logs mais recentes."""
        conn = self.get_connection()
        if not conn:
            return []

        try:
            with self.lock:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao buscar logs: {e}")
            return []

    def clear_logs(self):
        """Limpa todos os logs do banco de dados."""
        conn = self.get_connection()
        if not conn:
            return False

        try:
            with self.lock:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM logs")
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Erro ao limpar logs: {e}")
            return False

    def close(self):
        """Fecha a conexão com o banco de dados."""
        if hasattr(self.thread_local, "conn"):
            self.thread_local.conn.close()
            delattr(self.thread_local, "conn")