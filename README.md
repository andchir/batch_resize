# Batch Video Resize

Набор скриптов для массовой обработки медиафайлов:
- `main.py` - массовое изменение размеров видео в папке с использованием FFmpeg
- `download.py` - скачивание файлов из URL-ссылок, найденных в XLS, XLSX или CSV файлах
- `rename.py` - массовое переименование файлов в папке с различными стратегиями сортировки и переименования

## Требования

- Python 3.7+
- FFmpeg (должен быть установлен в системе)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/andchir/batch_resize.git
cd batch_resize
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Убедитесь, что FFmpeg установлен в системе:
```bash
ffmpeg -version
```

Если FFmpeg не установлен, установите его:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Скачайте FFmpeg с [официального сайта](https://ffmpeg.org/download.html) и добавьте в PATH.

## Использование

Приложение можно использовать двумя способами: через графический интерфейс (GUI) или через командную строку (CLI).

### Графический интерфейс (GUI)

Для запуска GUI приложения:

```bash
python gui.py
```

Графический интерфейс предоставляет удобный способ настройки параметров и визуального отслеживания прогресса обработки.

**Функции GUI:**
- Выбор папки с видеофайлами через диалоговое окно
- Настройка целевой высоты видео
- Опции удаления звука и создания миниатюр
- Отображение прогресса обработки в реальном времени
- Журнал всех операций
- Возможность остановки обработки

### Командная строка (CLI)

#### Базовое использование

```bash
python main.py /путь/к/папке/с/видео <высота>
```

Где:
- `/путь/к/папке/с/видео` - путь к папке с видеофайлами
- `<высота>` - целевая высота кадра в пикселях (ширина будет рассчитана автоматически с сохранением пропорций)

### Примеры

Изменить размер всех видео до высоты 720p:
```bash
python main.py ~/Videos 720
```

Изменить размер до 1080p:
```bash
python main.py ~/Videos 1080
```

Изменить размер с удалением звуковой дорожки:
```bash
python main.py ~/Videos 720 --remove-audio
```

Создать миниатюры (thumbnails) из видео:
```bash
python main.py ~/Videos 720 --create-thumbs
```

### Параметры

- `folder` - путь к папке с видеофайлами (обязательный)
- `height` - целевая высота в пикселях (обязательный)
- `--remove-audio` - удалить звуковую дорожку из выходных видео (необязательный)
- `--create-thumbs` - создать JPG миниатюры в папке "thumbs" (один кадр из каждого видео) (необязательный)

### Поддерживаемые форматы

Скрипт обрабатывает следующие видеоформаты:
- .mp4
- .avi
- .mkv
- .mov
- .flv
- .wmv
- .webm
- .m4v
- .mpeg
- .mpg

## Вывод

Обработанные видео сохраняются в подпапке `output` внутри исходной папки с видео.

Например, если исходная папка `/home/user/Videos`, то обработанные видео будут в `/home/user/Videos/output`.

Если используется параметр `--create-thumbs`, миниатюры (JPG файлы) сохраняются в подпапке `thumbs` внутри исходной папки с видео.

Например, если исходная папка `/home/user/Videos`, то миниатюры будут в `/home/user/Videos/thumbs`.

## Настройки кодирования

Скрипт использует следующие настройки для кодирования:

- **Видео кодек:** H.264 (libx264)
- **Предустановка:** medium (баланс между скоростью и качеством)
- **CRF:** 23 (константа качества, 23 - хорошее качество)
- **Масштабирование:** Сохранение пропорций (ширина рассчитывается автоматически)
- **Аудио кодек:** AAC (если не используется --remove-audio)
- **Битрейт аудио:** 128 kbps

## Пример вывода

### Без создания миниатюр

```
Found 3 video file(s) in '/home/user/Videos'
Output directory: /home/user/Videos/output
Processing: video1.mp4
Completed: video1.mp4
Processing: video2.mkv
Completed: video2.mkv
Processing: video3.avi
Completed: video3.avi

==================================================
Processing complete!
Successful: 3
Failed: 0
Total: 3
==================================================
```

### С созданием миниатюр (--create-thumbs)

```
Found 3 video file(s) in '/home/user/Videos'
Output directory: /home/user/Videos/output
Thumbnails directory: /home/user/Videos/thumbs
Processing: video1.mp4
Completed: video1.mp4
Creating thumbnail: video1.jpg
Thumbnail created: video1.jpg
Processing: video2.mkv
Completed: video2.mkv
Creating thumbnail: video2.jpg
Thumbnail created: video2.jpg
Processing: video3.avi
Completed: video3.avi
Creating thumbnail: video3.jpg
Thumbnail created: video3.jpg

==================================================
Processing complete!
Successful: 3
Failed: 0
Total: 3
Thumbnails created: 3
Thumbnails failed: 0
==================================================
```

## Скрипт download.py

Скрипт для скачивания файлов из URL-ссылок, найденных в XLS, XLSX или CSV файлах.

### Использование download.py

```bash
python download.py <путь_к_файлу> <папка_для_сохранения>
```

Где:
- `<путь_к_файлу>` - путь к XLS, XLSX или CSV файлу с URL-ссылками
- `<папка_для_сохранения>` - папка, куда будут загружены файлы

### Примеры download.py

Скачать файлы из XLSX файла:
```bash
python download.py data.xlsx /path/to/downloads
```

Скачать файлы из CSV файла:
```bash
python download.py urls.csv ~/Downloads
```

Скачать файлы из XLS файла:
```bash
python download.py data.xls ./files
```

### Поддерживаемые форматы файлов

- `.csv` - CSV файлы (разделители - запятая)
- `.xlsx` - Excel файлы нового формата (требуется библиотека openpyxl)
- `.xls` - Excel файлы старого формата (требуется библиотека xlrd)

### Особенности работы download.py

- Скрипт читает все ячейки во всех листах файла
- Автоматически определяет и извлекает URL-ссылки (http:// и https://)
- Распознает как обычные URL в тексте, так и гиперссылки в Excel
- Извлекает имя файла из URL, если возможно
- Пропускает уже скачанные файлы
- Обрабатывает ошибки сети и недоступные URL
- Выводит подробный отчет о скачивании

### Пример вывода download.py

```
Output directory: /home/user/downloads
Reading file: /home/user/data.xlsx
Found 5 unique URL(s) in the file

[1/5] Processing: https://example.com/image.png
Downloaded: image.png

[2/5] Processing: https://example.com/file.pdf
Downloaded: file.pdf

[3/5] Processing: https://example.com/already-downloaded.jpg
Skipped (already exists): already-downloaded.jpg

[4/5] Processing: https://example.com/not-found.txt
Error downloading https://example.com/not-found.txt: HTTP Error 404: Not Found

[5/5] Processing: https://example.com/document.docx
Downloaded: document.docx

```

## Скрипт rename.py

Скрипт для массового переименования файлов в папке с различными стратегиями сортировки и переименования.

### Использование rename.py

```bash
python rename.py <путь_к_папке> <тип_сортировки> <тип_переименования> [--prefix ПРЕФИКС] [--suffix СУФФИКС] [--dry-run]
```

Где:
- `<путь_к_папке>` - путь к папке с файлами для переименования
- `<тип_сортировки>` - способ сортировки файлов перед переименованием:
  - `name` - сортировка по имени (алфавитная)
  - `number` - сортировка по числу в имени файла (текст игнорируется)
- `<тип_переименования>` - способ генерации новых имен:
  - `sequential` - последовательная нумерация (1, 2, 3, ...)
  - `numbers_only` - оставить только цифры из имени (удалить текст)
  - `text_only` - оставить только текст из имени (удалить цифры)
- `--prefix` - необязательный префикс для имен файлов
- `--suffix` - необязательный суффикс для имен файлов (добавляется перед расширением)
- `--dry-run` - предварительный просмотр изменений без фактического переименования

### Примеры rename.py

Переименовать файлы последовательно с префиксом:
```bash
python rename.py ~/Photos name sequential --prefix "photo_"
```

Сортировать по числу в имени и оставить только текст:
```bash
python rename.py ~/Documents number text_only --suffix "_edited"
```

Предварительный просмотр изменений (без переименования):
```bash
python rename.py ~/Files name sequential --dry-run
```

Комбинация префикса и суффикса:
```bash
python rename.py ~/Images number numbers_only --prefix "img_" --suffix "_final"
```

Переименовать файлы, отсортированные по числу:
```bash
python rename.py ~/Videos number sequential
```

### Типы сортировки

**`name` - Сортировка по имени:**
- Файлы сортируются в алфавитном порядке
- Пример: `a.txt`, `b.txt`, `c.txt`

**`number` - Сортировка по числу:**
- Извлекается первое число из имени файла
- Файлы сортируются по этому числу
- Если числа нет, файл помещается в начало
- Пример: `file1.txt` (1), `file10.txt` (10), `file2.txt` (2) → сортируется как 1, 2, 10

### Типы переименования

**`sequential` - Последовательная нумерация:**
- Файлы переименовываются в 1, 2, 3, ...
- Пример: `1.jpg`, `2.jpg`, `3.jpg`

**`numbers_only` - Только цифры:**
- Извлекает все цифры из имени файла
- Удаляет весь текст
- Если цифр нет, используется порядковый номер
- Пример: `photo_001.jpg` → `001.jpg`, `image100.png` → `100.png`

**`text_only` - Только текст:**
- Удаляет все цифры из имени файла
- Оставляет только текст и другие символы
- Пример: `photo_001.jpg` → `photo_.jpg`, `image100text.png` → `imagetext.png`

### Особенности работы rename.py

- Обрабатывает все файлы в указанной папке (не затрагивает подпапки)
- Сохраняет расширения файлов
- Автоматически обрабатывает дубликаты имен (добавляет счетчик)
- Режим `--dry-run` позволяет предварительно посмотреть результат
- Безопасно обрабатывает специальные символы в именах файлов
- Выводит подробный отчет о выполненных операциях

### Пример вывода rename.py

#### Обычный режим:
```
Configuration:
  Folder: /home/user/Photos
  Sort by: name
  Rename as: sequential
  Prefix: 'photo_'

Found 3 file(s) in '/home/user/Photos'
[1] Renamed: IMG_001.jpg -> photo_1.jpg
[2] Renamed: IMG_002.jpg -> photo_2.jpg
[3] Renamed: IMG_003.jpg -> photo_3.jpg

============================================================
Renaming complete!
Successful: 3
Failed: 0
Total: 3
============================================================
```

#### Режим dry-run:
```
Configuration:
  Folder: /home/user/Photos
  Sort by: number
  Rename as: numbers_only
  Mode: DRY RUN (no actual changes)

Found 3 file(s) in '/home/user/Photos'

Dry run mode - showing what would be renamed:
============================================================
[1] photo_001.jpg -> 001.jpg
[2] photo_002.jpg -> 002.jpg
[3] photo_010.jpg -> 010.jpg

============================================================
Dry run complete! No files were actually renamed.
Successful: 3
Failed: 0
Total: 3
============================================================
```

## Лицензия

MIT License
