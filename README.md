# Batch Video Resize

Скрипт для массового изменения размеров видео в папке с использованием FFmpeg.

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

### Базовое использование

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
python main.py ~/Videos 720 --remove_audio
```

Создать миниатюры (thumbnails) из видео:
```bash
python main.py ~/Videos 720 --create_thumbs
```

### Параметры

- `folder` - путь к папке с видеофайлами (обязательный)
- `height` - целевая высота в пикселях (обязательный)
- `--remove_audio` - удалить звуковую дорожку из выходных видео (необязательный)
- `--create_thumbs` - создать JPG миниатюры в папке "thumbs" (один кадр из каждого видео) (необязательный)

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

Если используется параметр `--create_thumbs`, миниатюры (JPG файлы) сохраняются в подпапке `thumbs` внутри исходной папки с видео.

Например, если исходная папка `/home/user/Videos`, то миниатюры будут в `/home/user/Videos/thumbs`.

## Настройки кодирования

Скрипт использует следующие настройки для кодирования:

- **Видео кодек:** H.264 (libx264)
- **Предустановка:** medium (баланс между скоростью и качеством)
- **CRF:** 23 (константа качества, 23 - хорошее качество)
- **Масштабирование:** Сохранение пропорций (ширина рассчитывается автоматически)
- **Аудио кодек:** AAC (если не используется --remove_audio)
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

### С созданием миниатюр (--create_thumbs)

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

## Лицензия

MIT License
