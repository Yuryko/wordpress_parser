# ООО НТП "Криптософт"
# скрипт формирует из экспорта wordpress файлы для генерации в hugo
# - удаляются все посты кроме категории "Для внешней публикации"
# - удаляется категрия "Для внешней публикации"
# - преобразуются изображения, соотвествующие шаблону hugo (пока частично)




import zipfile
from zipfile import ZipFile
import os
import re
import glob

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

def work_on_files(directory, phrase):
    
# обработка изображений в тексте 
    pattern_start = r'\[<img [^>]*wp-image-' # заменим начало 
    replacement_start = r'![wp-image-'
   
    pattern_png = r'png.*? />\]' # окончание стоки до png
    replacement_png = r'png)'

    pattern_png_2 = r'(wp-image-.{4}).*?(/wp-content/uploads)'
    
    pattern_wp_im = r'/wp-content/uploads'
    replacement_wp_im = r'](/wordpress/wp-content/uploads'

# обработка изображения в заголовке
    pattern_feautured = r'featured_image: '
    replacement_feautured = r'thumbnail:\n  src: "/wordpress'
    pattern_png_3 = r'png'
    replacement_png_3 = r'png"\n  visibility:\n    -list'

    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            with open(filepath, 'w', encoding='utf-8') as file:
                for line in lines:

                    # дата
                    if line.startswith("date:"): 
                        line = line[:16] + '\n'

                    # обработка изобржения в заголовке
                    if ("featured_image: " in line):
                        line = re.sub(pattern_feautured, replacement_feautured, line)
                        line = re.sub(pattern_png_3, replacement_png_3, line)

                    # обработка изображений в тексте
                    if "[<img" in line:
                        line = re.sub(pattern_start, replacement_start, line)
                        line = re.sub(pattern_png, replacement_png, line)
                        line = re.sub(pattern_png_2, r'\1\2', line)
                        line = re.sub(pattern_wp_im, replacement_wp_im, line)

                    # копирование используемых изображений
                    if ".png" in line:

                    
                    # Удаление категории
                    if phrase not in line:
                        file.write(line)

# удаление ненужных изображений и каталогов
"""
def find_image_paths(md_directory):
    image_paths = set()
    for root, _, files in os.walk(md_directory):
        for file in files:
            if file.endswith('.md'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Ищем пути к изображениям, начинающиеся с /wp-content
                    paths = re.findall(r'/wp-content[^\s)]+\.(?:png|jpg)', content)
                    image_paths.update(paths)
    print (image_paths)
    return image_paths

def delete_unused_images(wp_content_directory, used_image_paths):
    for root, dirs, files in os.walk(wp_content_directory, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, wp_content_directory)
            # Преобразуем относительный путь в формат, начинающийся с /wp-content
            formatted_path = '/' + os.path.join('wp-content', relative_path).replace('\\', '/')
            if formatted_path not in used_image_paths:
               # print(f"Deleting unused file: {file_path}")
                os.remove(file_path)
        # Удаляем пустые каталоги
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                #print(f"Deleting empty directory: {dir_path}")
                #os.rmdir(dir_path)

def delete_unref(md_directory, wp_content_directory):
    used_image_paths = find_image_paths(md_directory)
    delete_unused_images(wp_content_directory, used_image_paths)
"""

# распаковка
directory_path = 'hugo-export'
convert_filename_encoding(directory_path)

#удаление ненужных заметок (оставлю задел для фильтрации)
words = ['Для внешней публикации']
directory_posts = 'hugo-export/posts'
remove_unnecessary(directory_posts)

# Удаление 
# - категории Для внешней публикации
# - обрезание даты (для удаления метки о последнем изменении)
# Добавляем wordpress перед изображением в названии

phrase_to_remove = "- Для внешней публикации"
work_on_files(directory_posts, phrase_to_remove)

# Удаление неиспоьзуемых изображжений и пустых каталогов
#images_dir = "hugo-export"
#delete_unref(directory_posts, images_dir)


#md_directory = "path/to/your/md/files"  # Укажите путь к каталогу с .md файлами
#wp_content_directory = "path/to/wp-content"  # Укажите путь к каталогу /wp-content
#main(md_directory, wp_content_directory)



