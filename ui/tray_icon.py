# src/ui/tray_icon.py
import os
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QCoreApplication, Qt


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, main_window, icon_path, parent=None):
        # Criar um ícone padrão simples se o arquivo não existir
        if os.path.exists(icon_path) and os.path.getsize(icon_path) > 0:
            icon = QIcon(icon_path)
        else:
            # Cria um ícone simples - um quadrado amarelo
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.yellow)
            icon = QIcon(pixmap)

        super().__init__(icon, parent)

        self.main_window = main_window

        # Menu da bandeja
        self.menu = QMenu()

        # Ação Abrir
        self.open_action = QAction("Abrir", self)
        self.open_action.triggered.connect(self.show_main_window)
        self.menu.addAction(self.open_action)

        # Ação Adicionar Pasta
        self.add_folder_action = QAction("Adicionar Pasta", self)
        self.add_folder_action.triggered.connect(self.main_window.add_folder)
        self.menu.addAction(self.add_folder_action)

        # Separador
        self.menu.addSeparator()

        # Ação Ver Estatísticas
        self.stats_action = QAction("Ver Estatísticas", self)
        self.stats_action.triggered.connect(self.main_window.show_stats)
        self.menu.addAction(self.stats_action)

        # Ação Ver Logs
        self.logs_action = QAction("Ver Logs", self)
        self.logs_action.triggered.connect(self.main_window.show_logs)
        self.menu.addAction(self.logs_action)

        # Separador
        self.menu.addSeparator()

        # Ação Sair
        self.quit_action = QAction("Sair", self)
        self.quit_action.triggered.connect(self.quit_application)
        self.menu.addAction(self.quit_action)

        # Configura o menu
        self.setContextMenu(self.menu)

        # Conecta o evento de clique
        self.activated.connect(self.on_tray_icon_activated)

        # Configura as tooltips
        self.setToolTip("Organizador Automático de Pastas")

    def on_tray_icon_activated(self, reason):
        """Manipula a ativação do ícone da bandeja."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_main_window()
        elif reason == QSystemTrayIcon.Trigger:  # Clique único
            # Mostra uma mensagem de status
            self.showMessage(
                "Organizador de Pastas",
                "O organizador está em execução. Clique duplo para abrir.",
                QSystemTrayIcon.Information,
                2000
            )

    def show_main_window(self):
        """Mostra a janela principal."""
        self.main_window.show()
        self.main_window.setWindowState(self.main_window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.main_window.activateWindow()

    def quit_application(self):
        """Encerra a aplicação."""
        reply = QMessageBox.question(
            None,
            "Confirmação",
            "Tem certeza que deseja encerrar o Organizador de Pastas?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            QCoreApplication.quit()

    def show_notification(self, title, message):
        """Mostra uma notificação na bandeja."""
        self.showMessage(title, message, QSystemTrayIcon.Information, 5000)