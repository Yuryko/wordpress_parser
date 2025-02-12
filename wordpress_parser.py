# ООО НТП "Криптософт"
# скрипт формирует из экспорта wordpress файлы для генерации в hugo
# - удаляются все посты кроме категории "Для внешней публикации"
# - удаляется категрия "Для внешней публикации"
# - преобразуются изображения, соотвествующие шаблону hugo


import zipfile
import os
import re
import shutil

import argparse

parser=argparse.ArgumentParser(
    description=''' ООО НТП "Криптософт". Cкрипт формирует из экспорта wordpress файлы для генерации в hugo''',
    epilog=""" В результате работы скрипта будут сформированы два каталога 
    posts  и  static. Переместите каталог posts  в каталог content, содержимое из static в каталог static
    генератора сайтов HUGO.""")
parser.add_argument('--d', type=str, default='wordpress', help='<каталог вебсервера>')
args=parser.parse_args()
dir_webserver = args.d

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

# обработка постов
def work_on_files(directory, phrase):
# создание каталога для используемых изображений 
    if not os.path.exists('static'):
        os.makedirs('static')
    
    directory_wp_content = re.sub('/posts','', directory)
# обработка изображений в тексте 
    pattern_start = r'\[<img [^>]*wp-image-' # заменим начало 
    replacement_start = r'![wp-image-'
   
    pattern_png = r'png.*? />\]' # окончание стоки до png
    replacement_png = r'png) '

    pattern_png_2 = r'(wp-image-.{4}).*?(/wp-content/uploads)'
    
    pattern_wp_im = r'/wp-content/uploads'
    replacement_wp_im = r'](/' + re.escape(dir_webserver)+ r'/wp-content/uploads'

# обработка изображения в заголовке
    pattern_feautured = r'featured_image: '
    replacement_feautured = r'thumbnail:\n  src: "/'+ re.escape(dir_webserver)
    pattern_png_3 = r'png'
    replacement_png_3 = r'png"\n  visibility:\n    -list'
# удаление ссылок на внвнутренние ресурсы
    pattern_source = r'\[\d\]:'
    pattern_source2 = r'\[\d\]'
    pattern_source3 = r'(http://qpos.cryptosoft.ru).*?(.png)'


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
                        image_paths = re.findall(r'/wp-content[^\s)]+\.(?:png|jpg)', line)
                        for image_path in image_paths:
                            full_image_path = os.path.join(directory_wp_content, image_path.lstrip('/'))
                            if os.path.exists(full_image_path):
                                relative_path = os.path.relpath(full_image_path, directory_wp_content)
                                dest_image_path = os.path.join('static', relative_path)
                                os.makedirs(os.path.dirname(dest_image_path), exist_ok=True)
                        # Копируем изображение
                                shutil.copy2(full_image_path, dest_image_path)
                                #print(f'Copied: {full_image_path} -> {dest_image_path}')
                            else:
                                print(f'File not found: {full_image_path}')

                    # Удаляем ссылки на ресурсы http://qpos.cryptosoft.ru  
                    if "[" in line:
                        line = re.sub(pattern_source, '', line)
                        line = re.sub(pattern_source2, '', line)

                    if "qpos.cryptosoft.ru" in line:
                        line = re.sub(pattern_source3, '', line)

                    # Удаляем категорию
                    if phrase not in line:
                        file.write(line)

# удаление ненужных и каталогов

def delete_dir(dirs): 
    print(f"Deleting directory: {dirs}")
    shutil.rmtree(dirs)
def del_config():
    if os.path.exists('hugo-export/config.yaml'):
        print(f"Deleting directory: hugo-export/config.yaml")    
        os.remove('hugo-export/config.yaml')

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
# Обработка изображений
# Копирование изображений в static

phrase_to_remove = "- Для внешней публикации"
work_on_files(directory_posts, phrase_to_remove)

# Удаляем неиспользуемые каталоги

delete_dir('hugo-export/wp-content')
delete_dir('hugo-export/sample-page')
delete_dir('hugo-export/╨╕╨╖╨▒╤Ç╨░╨╜╨╜╨╛╨╡')
delete_dir('hugo-export/╨┤╨╗╤Å-╤ç╨╡╨│╨╛-╨▓╤ü╨╡-╤ì╤é╨╛')
del_config()

print(dir_webserver)




