# src/core/folder_watcher.py
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileHandler(FileSystemEventHandler):
    def __init__(self, organizer, logger):
        self.organizer = organizer
        self.logger = logger
        # Controle para evitar processamento duplicado
        self.processed_files = set()

    def on_created(self, event):
        """Chamado quando um arquivo é criado."""
        if not event.is_directory:
            # Espera um pouco para o arquivo "estabilizar" (evitar problemas de lock)
            time.sleep(0.5)
            self._process_file(event.src_path)

    def on_moved(self, event):
        """Chamado quando um arquivo é movido para a pasta monitorada."""
        if not event.is_directory and os.path.exists(event.dest_path):
            self._process_file(event.dest_path)

    def _process_file(self, file_path):
        """Processa um arquivo, evitando duplicações."""
        if file_path in self.processed_files:
            return

        # Adiciona à lista de processados
        self.processed_files.add(file_path)

        # Organiza o arquivo
        try:
            self.organizer.organize_file(file_path)
        except Exception as e:
            self.logger.error("Erro ao processar arquivo", f"{file_path}: {str(e)}")

        # Remove da lista após algum tempo (limpeza periódica)
        if len(self.processed_files) > 1000:
            self.processed_files.clear()


class FolderWatcher:
    def __init__(self, organizer, logger):
        self.organizer = organizer
        self.logger = logger
        self.observer = Observer()
        self.watched_folders = {}

    def start_watching(self, folder_path):
        """Inicia o monitoramento de uma pasta."""
        if folder_path in self.watched_folders:
            self.logger.warning("Pasta já monitorada", folder_path)
            return False

        try:
            if not os.path.exists(folder_path):
                self.logger.error("Pasta não existe", folder_path)
                return False

            # Cria um handler
            event_handler = FileHandler(self.organizer, self.logger)

            # Configura o observer com o handler
            watch = self.observer.schedule(event_handler, folder_path, recursive=False)
            self.watched_folders[folder_path] = watch

            self.logger.info("Iniciando monitoramento", folder_path)

            # Organiza arquivos existentes
            self.organizer.organize_directory(folder_path)

            return True
        except Exception as e:
            self.logger.error("Erro ao monitorar pasta", f"{folder_path}: {str(e)}")
            return False

    def stop_watching(self, folder_path):
        """Para o monitoramento de uma pasta."""
        if folder_path not in self.watched_folders:
            self.logger.warning("Pasta não está sendo monitorada", folder_path)
            return False

        try:
            watch = self.watched_folders.pop(folder_path)
            self.observer.unschedule(watch)
            self.logger.info("Monitoramento interrompido", folder_path)
            return True
        except Exception as e:
            self.logger.error("Erro ao parar monitoramento", f"{folder_path}: {str(e)}")
            return False

    def start(self):
        """Inicia o observador."""
        if not self.observer.is_alive():
            self.observer.start()
            self.logger.info("Observador iniciado", "")

    def stop(self):
        """Para o observador."""
        self.observer.stop()
        self.observer.join()
        self.logger.info("Observador parado", "")