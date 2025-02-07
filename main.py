import zipfile
from zipfile import ZipFile
import os
import re

# распаковываем архив
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

# удаляем все посты, которые не имееют тега для внешней публикации

def remove_unnecessary(root_dir):
    files = os.listdir(root_dir)
    for each_file in files:
        full_path = "%s/%s" % (root_dir, each_file)
        each_file_content = open(full_path, 'r', encoding="utf-8").read()
        if not any(word in each_file_content for word in words):
            os.unlink(full_path)

def remove_line_with_phrase(directory, phrase):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            with open(filepath, 'w', encoding='utf-8') as file:
                for line in lines:

                    # дата
                    if line.startswith("date:"): 
                        line = line[:16] + '\n'

                    # Вставляем "/wordpress/"
                    if "featured_image: " in line: 
                        before_featured = line.split("featured_image: ")[0]
                        after_featured = line.split("featured_image: ")[1]
                        line = f"{before_featured}featured_image: /wordpress{after_featured}"

                    # Вставляем нужное обрамление для картинок                              
                    if "wp-image" in line: 
                        after_featured1 = line.split("wp-image")[1]
                        after_featured2 = line.split("/wp-content/uploads")[1]              
                        after_featured3 = after_featured1[:5] + "](/wordpress/wp-content/uploads" + after_featured2
                        after_featured4 = after_featured3.split("\" alt=")[0] + ')' + '\n'
                        line = f"![wp-image{after_featured4}"
                    #if "wp-image" in line: 
                    #    before_featured2 = line[15:] + ']' # название картинки
                    #    after_featured3 = line.split("qpos.cryptosoft.ru/news/")[1]
                    #    line = f"{before_featured2}(/wordpress/{after_featured3}"

                
                    
                    # Удаление категории
                    if phrase not in line:
                        file.write(line)
                    

# распаковка
directory_path = 'hugo-export'
#convert_filename_encoding(directory_path)

#удаление ненужных заметок (оставлю задел для фильтрации)
words = ['Для внешней публикации']
directory_posts = 'hugo-export/posts'
#remove_unnecessary(directory_posts)

# Удаление 
# - категории Для внешней публикации
# - обрезание даты (для удаления метки о последнем изменении)
# Добавляем wordpress перед изображением в названии

phrase_to_remove = "- Для внешней публикации"
remove_line_with_phrase(directory_posts, phrase_to_remove)




