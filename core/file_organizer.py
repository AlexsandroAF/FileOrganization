# src/core/file_organizer.py
import os
import shutil
from config.file_types import get_file_type, FILE_TYPES


class FileOrganizer:
    def __init__(self, logger):
        self.logger = logger

    def organize_file(self, file_path):
        """Organiza um arquivo em sua pasta apropriada."""
        try:
            if not os.path.exists(file_path) or os.path.isdir(file_path):
                return False

            # Obtém diretório pai e extensão
            parent_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_name)[1]

            # Determina o tipo de arquivo
            file_type = get_file_type(file_extension)
            target_subfolder = FILE_TYPES[file_type]["folder_name"]

            # Cria o subdiretório se não existir
            target_dir = os.path.join(parent_dir, target_subfolder)
            os.makedirs(target_dir, exist_ok=True)

            # Move o arquivo
            target_path = os.path.join(target_dir, file_name)

            # Se já existir um arquivo com esse nome, adiciona um número
            if os.path.exists(target_path):
                base_name, ext = os.path.splitext(file_name)
                counter = 1
                while os.path.exists(target_path):
                    new_name = f"{base_name}_{counter}{ext}"
                    target_path = os.path.join(target_dir, new_name)
                    counter += 1

            shutil.move(file_path, target_path)
            self.logger.info("Arquivo movido", f"De {file_path} para {target_path}")
            return True

        except Exception as e:
            self.logger.error("Erro ao organizar arquivo", f"{file_path}: {str(e)}")
            return False

    def organize_directory(self, directory):
        """Organiza todos os arquivos em um diretório."""
        try:
            files = [os.path.join(directory, f) for f in os.listdir(directory)
                     if os.path.isfile(os.path.join(directory, f))]

            # Exclui arquivos dentro de subpastas já organizadas
            for file_type in FILE_TYPES.values():
                subfolder = os.path.join(directory, file_type["folder_name"])
                if subfolder in files:
                    files.remove(subfolder)

            # Organiza cada arquivo
            for file_path in files:
                self.organize_file(file_path)

            return True
        except Exception as e:
            self.logger.error("Erro ao organizar diretório", f"{directory}: {str(e)}")
            return False