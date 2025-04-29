# src/ui/main_window.py
import os
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QPushButton, QListWidget, QListWidgetItem, QLabel,
                             QFileDialog, QProgressBar, QMessageBox, QDialog,
                             QTextEdit, QTabWidget)
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self, db, folder_watcher, logger, parent=None):
        super().__init__(parent)

        self.db = db
        self.folder_watcher = folder_watcher
        self.logger = logger

        self.setWindowTitle("Organizador Automático de Pastas")
        self.setMinimumSize(800, 500)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)

        # Abas
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Tab de pastas
        self.folders_tab = QWidget()
        self.tabs.addTab(self.folders_tab, "Pastas Monitoradas")

        # Tab de estatísticas
        self.stats_tab = QWidget()
        self.tabs.addTab(self.stats_tab, "Estatísticas")

        # Configurar layout da tab de pastas
        self._setup_folders_tab()

        # Configurar layout da tab de estatísticas
        self._setup_stats_tab()

        # Carregar pastas monitoradas
        self.load_folders()

    def _setup_folders_tab(self):
        """Configura a aba de pastas monitoradas."""
        layout = QVBoxLayout(self.folders_tab)

        # Lista de pastas
        self.folders_list = QListWidget()
        self.folders_list.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.folders_list)

        # Botões
        buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Adicionar Pasta")
        self.add_button.clicked.connect(self.add_folder)
        buttons_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remover Pasta")
        self.remove_button.clicked.connect(self.remove_folder)
        buttons_layout.addWidget(self.remove_button)

        layout.addLayout(buttons_layout)

    def _setup_stats_tab(self):
        """Configura a aba de estatísticas."""
        layout = QVBoxLayout(self.stats_tab)

        # Informações gerais
        self.total_space_label = QLabel("Espaço Total Ocupado: 0 MB")
        layout.addWidget(self.total_space_label)

        # Barra de progresso
        self.space_progress = QProgressBar()
        self.space_progress.setTextVisible(True)
        layout.addWidget(self.space_progress)

        # Estatísticas por tipo
        layout.addWidget(QLabel("Espaço por Tipo de Arquivo:"))

        # Containers para estatísticas dinâmicas
        self.stats_container = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_container)
        layout.addWidget(self.stats_container)

        # Botão para atualizar estatísticas
        self.update_stats_button = QPushButton("Atualizar Estatísticas")
        self.update_stats_button.clicked.connect(self.update_statistics)
        layout.addWidget(self.update_stats_button)

        # Espaço flexível
        layout.addStretch(1)

    def load_folders(self):
        """Carrega a lista de pastas monitoradas do banco de dados."""
        self.folders_list.clear()

        folders = self.db.get_all_folders()
        for folder in folders:
            item = QListWidgetItem(folder['path'])
            item.setData(Qt.UserRole, folder['id'])
            self.folders_list.addItem(item)

            # Inicia o monitoramento
            self.folder_watcher.start_watching(folder['path'])

    def add_folder(self):
        """Abre um diálogo para adicionar uma pasta para monitoramento."""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta para Monitorar",
            os.path.expanduser("~"), QFileDialog.ShowDirsOnly
        )

        if folder_path:
            # Verifica se a pasta já está sendo monitorada
            for i in range(self.folders_list.count()):
                if self.folders_list.item(i).text() == folder_path:
                    QMessageBox.warning(
                        self, "Aviso",
                        "Esta pasta já está sendo monitorada!"
                    )
                    return

            # Adiciona ao banco de dados
            folder_id = self.db.add_folder(folder_path)

            if folder_id:
                # Adiciona à lista
                item = QListWidgetItem(folder_path)
                item.setData(Qt.UserRole, folder_id)
                self.folders_list.addItem(item)

                # Inicia o monitoramento
                self.folder_watcher.start_watching(folder_path)
                self.logger.info("Pasta adicionada", folder_path)

                # Atualiza estatísticas
                self.update_statistics()

    def remove_folder(self):
        """Remove uma pasta do monitoramento."""
        selected_items = self.folders_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Aviso",
                "Selecione uma pasta para remover!"
            )
            return

        item = selected_items[0]
        folder_path = item.text()
        folder_id = item.data(Qt.UserRole)

        # Confirmação
        reply = QMessageBox.question(
            self, "Confirmação",
            f"Tem certeza que deseja parar de monitorar a pasta:\n{folder_path}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Remove do banco de dados
            if self.db.remove_folder(folder_id):
                # Para o monitoramento
                self.folder_watcher.stop_watching(folder_path)

                # Remove da lista
                self.folders_list.takeItem(self.folders_list.row(item))
                self.logger.info("Pasta removida", folder_path)

                # Atualiza estatísticas
                self.update_statistics()

    def update_statistics(self):
        """Atualiza as estatísticas de espaço ocupado."""
        # Limpa as estatísticas anteriores
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        total_space = 0
        type_stats = {}

        # Para cada pasta monitorada
        for i in range(self.folders_list.count()):
            folder_path = self.folders_list.item(i).text()

            if os.path.exists(folder_path):
                # Calcula o espaço usado por cada tipo
                from config.file_types import FILE_TYPES

                for file_type, data in FILE_TYPES.items():
                    type_folder = os.path.join(folder_path, data["folder_name"])

                    if os.path.exists(type_folder):
                        size = self._get_folder_size(type_folder)
                        total_space += size

                        if file_type in type_stats:
                            type_stats[file_type] += size
                        else:
                            type_stats[file_type] = size

        # Atualiza o total
        total_mb = total_space / (1024 * 1024)  # Bytes para MB
        self.total_space_label.setText(f"Espaço Total Ocupado: {total_mb:.2f} MB")

        # Barra de progresso - ajusta para mostrar porcentagem em relação ao limite de 1GB
        limit_mb = 1024  # 1GB
        percentage = min(100, (total_mb / limit_mb) * 100)
        self.space_progress.setValue(int(percentage))
        self.space_progress.setFormat(f"{total_mb:.2f} MB / {limit_mb} MB")

        # Adiciona estatísticas por tipo
        for file_type, size in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
            size_mb = size / (1024 * 1024)  # Bytes para MB
            folder_name = FILE_TYPES[file_type]["folder_name"]

            label = QLabel(f"{folder_name}: {size_mb:.2f} MB")
            self.stats_layout.addWidget(label)

    def _get_folder_size(self, folder_path):
        """Retorna o tamanho total de uma pasta em bytes."""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size

    def show_logs(self):
        """Mostra uma janela com os logs recentes."""
        logs_dialog = QDialog(self)
        logs_dialog.setWindowTitle("Logs do Sistema")
        logs_dialog.setMinimumSize(700, 500)

        layout = QVBoxLayout(logs_dialog)

        # Widget de texto para os logs
        log_text = QTextEdit()
        log_text.setReadOnly(True)
        layout.addWidget(log_text)

        # Botão para fechar
        close_button = QPushButton("Fechar")
        close_button.clicked.connect(logs_dialog.accept)
        layout.addWidget(close_button)

        # Carrega os logs
        logs = self.db.get_logs(500)  # Últimos 500 logs
        log_content = ""

        for log in logs:
            log_content += f"[{log['timestamp']}] {log['action']}: {log['details']}\n"

        log_text.setText(log_content)

        logs_dialog.exec_()

    def closeEvent(self, event):
        """Manipula o evento de fechar a janela."""
        event.ignore()
        self.hide()  # Esconde a janela em vez de fechá-la