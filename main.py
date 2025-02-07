import zipfile
from zipfile import ZipFile
import os

with zipfile.ZipFile('hugo-export.zip', 'r') as zip_ref:
    zip_ref.extractall()

# Переименовываем файлы
def convert_filename_encoding(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            try:
                # Декодируем имя файла из cp437 и кодируем в utf-8
                new_filename = filename.encode('cp437').decode('utf-8')
                old_file_path = os.path.join(dirpath, filename)
                new_file_path = os.path.join(dirpath, new_filename)
                
                # Переименовываем файл
                os.rename(old_file_path, new_file_path)
                print(f'Renamed: {old_file_path} -> {new_file_path}')
            except UnicodeError as e:
                print(f'Error renaming {filename}: {e}')

directory_path = 'hugo-export'
convert_filename_encoding(directory_path)

