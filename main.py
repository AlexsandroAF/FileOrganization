# main.py
import os
import sys
from PyQt5.QtWidgets import QApplication

# Importações locais (sem usar 'src')
from db.database import Database
from core.logger import Logger
from core.file_organizer import FileOrganizer
from core.folder_watcher import FolderWatcher
from ui.main_window import MainWindow
from ui.tray_icon import SystemTrayIcon
from config.settings import Settings


def main():
    # Configura o diretório de trabalho
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Inicia a aplicação Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Organizador Automático de Pastas")
    app.setQuitOnLastWindowClosed(False)

    # Configurar diretórios
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)

    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    icon_path = os.path.join(assets_dir, "icons", "tray_icon.png")

    # Verifica se o ícone existe, se não, cria um diretório e um arquivo vazio
    if not os.path.exists(icon_path):
        os.makedirs(os.path.dirname(icon_path), exist_ok=True)
        with open(icon_path, 'w') as f:
            pass

    # Inicializar componentes
    db = Database(os.path.join(data_dir, "app_data.db"))
    logger = Logger(logs_dir, db)
    settings = Settings(os.path.join(data_dir, "config.json"))

    # Iniciar organizador e monitor
    file_organizer = FileOrganizer(logger)
    folder_watcher = FolderWatcher(file_organizer, logger)

    # Iniciar interface
    main_window = MainWindow(db, folder_watcher, logger)
    tray_icon = SystemTrayIcon(main_window, icon_path)

    # Iniciar monitoramento
    folder_watcher.start()

    # Mostra o ícone na bandeja
    tray_icon.show()

    # Se for a primeira execução, mostrar a janela
    if not settings.get("last_folders"):
        main_window.show()
        tray_icon.show_notification(
            "Organizador de Pastas",
            "Bem-vindo! Adicione pastas para começar a monitorar."
        )

    # Executa a aplicação
    exit_code = app.exec_()

    # Encerramento
    folder_watcher.stop()
    db.close()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())