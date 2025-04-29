# src/config/file_types.py
FILE_TYPES = {
    "images": {
        "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
        "folder_name": "Imagens"
    },
    "documents": {
        "extensions": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"],
        "folder_name": "Documentos"
    },
    "videos": {
        "extensions": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
        "folder_name": "Vídeos"
    },
    "audio": {
        "extensions": [".mp3", ".wav", ".ogg", ".flac", ".aac", ".wma"],
        "folder_name": "Áudios"
    },
    "compressed": {
        "extensions": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
        "folder_name": "Compactados"
    },
    "executables": {
        "extensions": [".exe", ".msi", ".bat", ".cmd", ".ps1"],
        "folder_name": "Executáveis"
    },
    "code": {
        "extensions": [".py", ".java", ".js", ".html", ".css", ".cpp", ".c", ".php", ".sql"],
        "folder_name": "Código"
    },
    "others": {
        "extensions": [],  # Qualquer outra extensão
        "folder_name": "Outros"
    }
}


def get_file_type(file_extension):
    """Retorna o tipo de arquivo com base na extensão."""
    file_extension = file_extension.lower()

    for file_type, data in FILE_TYPES.items():
        if file_extension in data["extensions"]:
            return file_type

    return "others"