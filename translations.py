#!/usr/bin/env python3
"""
Internationalization (i18n) module for Batch Media Tools GUI.
Provides translations for English (default) and Russian languages.
"""

from typing import Dict


class Translations:
    """Translation manager for the application."""

    # English translations (default)
    EN = {
        # Window and general
        "window_title": "Batch Media Tools",
        "ready": "Ready",
        "processing": "Processing...",
        "downloading": "Downloading...",
        "renaming": "Renaming...",
        "error": "Error",

        # Tabs
        "tab_video_resize": "Video Resize",
        "tab_file_download": "File Download",
        "tab_file_rename": "File Rename",

        # Video Resize Tab
        "video_title": "Batch Video Resize",
        "settings": "Settings",
        "folder_with_videos": "Video folder:",
        "select_video_folder": "Select folder with video files...",
        "browse": "Browse...",
        "select_video_folder_dialog": "Select folder with video files",
        "target_height": "Target height (px):",
        "remove_audio": "Remove audio track",
        "create_thumbs": "Create thumbnails (JPG)",
        "processing_log": "Processing Log",
        "start_processing": "Start Processing",
        "stop": "Stop",
        "processing_complete": "Processing complete",
        "processing_stopped": "Processing stopped by user",
        "videos_not_found": "No video files found in '{}'",
        "videos_found": "Found {} video file(s) in '{}'",
        "output_folder": "Output folder: {}",
        "thumbs_folder": "Thumbnails folder: {}",
        "processing_file": "Processing: {}",
        "completed": "Completed: {}",
        "error_processing": "Error processing: {}",
        "creating_thumb": "Creating thumbnail: {}",
        "thumb_created": "Thumbnail created: {}",
        "thumb_error": "Thumbnail creation error: {}",
        "stopping_processing": "Stopping processing...",
        "processing_complete_summary": "Processing complete!",
        "successful": "Successful: {}",
        "errors": "Errors: {}",
        "total": "Total: {}",
        "thumbs_created": "Thumbnails created: {}",
        "thumbs_errors": "Thumbnail errors: {}",
        "processing_complete_msg": "Successfully processed: {}/{}",
        "please_select_folder": "Please select a folder with video files",
        "folder_not_exists": "Folder '{}' does not exist or is not a directory",
        "critical_error": "Critical error: {}",

        # File Download Tab
        "download_title": "Download Files from URLs",
        "url_file": "URL file (XLS/XLSX/CSV):",
        "select_url_file": "Select file with URLs...",
        "select_url_file_dialog": "Select file with URLs",
        "download_folder": "Download folder:",
        "select_download_folder": "Select folder to save files...",
        "select_download_folder_dialog": "Select folder to download files",
        "download_log": "Download Log",
        "start_download": "Start Download",
        "download_complete": "Download complete",
        "reading_file": "Reading file: {}",
        "urls_not_found": "No URLs found in file",
        "urls_found": "Found {} unique URL(s)",
        "download_folder_created": "Download folder: {}",
        "processing_url": "\n[{}/{}] Processing: {}",
        "skipped_exists": "Skipped (file exists): {}",
        "downloaded": "Downloaded: {}",
        "download_error": "Download error: {}",
        "stopping_download": "Stopping download...",
        "download_complete_summary": "Download complete!",
        "skipped": "Skipped: {}",
        "total_urls": "Total URLs: {}",
        "download_complete_msg": "Successfully downloaded: {}/{}",
        "please_select_url_file": "Please select a file with URLs",
        "file_not_exists": "File '{}' does not exist or is not a file",
        "unsupported_format": "Only XLS, XLSX, CSV formats are supported",
        "please_select_download_folder": "Please select a folder to download files",
        "column_index_name": "Column index for filename:",
        "column_index_name_tooltip": "Column index (0-based) to use for custom filename. -1 = not used",
        "column_index_name_hint": "(-1 = not used, 0 = first column, 1 = second, etc.)",
        "not_used": "Not used",
        "renamed_existing": "Renamed existing file: {} -> {}",
        "downloaded_renamed": "Downloaded and renamed: {}",
        "downloaded_rename_failed": "Downloaded as {}, but failed to rename: {}",

        # File Rename Tab
        "rename_title": "Batch File Rename",
        "folder_with_files": "Files folder:",
        "select_files_folder": "Select folder with files to rename...",
        "select_files_folder_dialog": "Select folder with files to rename",
        "sort": "Sort:",
        "sort_name": "By name (alphabetical)",
        "sort_number": "By number in name",
        "rename_type": "Rename type:",
        "rename_sequential": "Sequential numbering (1, 2, 3, ...)",
        "rename_numbers_only": "Only digits from name",
        "rename_text_only": "Only text from name",
        "rename_numbers_only_at_end": "Only number at end of name",
        "prefix": "Prefix (optional):",
        "prefix_placeholder": "For example: photo_",
        "suffix": "Suffix (optional):",
        "suffix_placeholder": "For example: _edited",
        "zero_padding": "Zero padding:",
        "zero_padding_hint": "(0 = not used, 1 = 09, 2 = 009)",
        "zero_padding_tooltip": "Number of zeros before the number in the file name (0 = not used)",
        "dry_run": "Preview (do not rename files)",
        "rename_log": "Rename Log",
        "start_rename": "Start Rename",
        "rename_complete": "Rename complete",
        "files_not_found": "No files found in '{}'",
        "files_found": "Found {} file(s) in '{}'",
        "configuration": "Configuration:",
        "folder": "Folder: {}",
        "sort_type": "Sort: {}",
        "rename_type_label": "Rename: {}",
        "prefix_label": "Prefix: '{}'",
        "suffix_label": "Suffix: '{}'",
        "zero_padding_label": "Zero padding: {}",
        "mode": "Mode: Preview (no changes)",
        "preview_mode": "Preview mode - showing planned changes:",
        "stopping_rename": "Stopping rename...",
        "renamed": "[{}] Renamed: {} -> {}",
        "preview_renamed": "[{}] {} -> {}",
        "target_exists": "Error: Target file already exists: {}",
        "rename_error": "Error renaming {}: {}",
        "rename_complete_summary": "Rename complete!",
        "preview_complete": "Preview complete! Files were not renamed.",
        "rename_preview_complete": "Preview Complete",
        "rename_preview_msg": "Previewed: {}/{} files\n\nUncheck 'Preview' to actually rename files.",
        "rename_complete_msg": "Successfully renamed: {}/{}",
        "please_select_files_folder": "Please select a folder with files",

        # Language selector
        "language": "Language:",
        "language_en": "English",
        "language_ru": "Russian",
    }

    # Russian translations
    RU = {
        # Window and general
        "window_title": "Batch Media Tools",
        "ready": "Готов к работе",
        "processing": "Обработка...",
        "downloading": "Загрузка...",
        "renaming": "Переименование...",
        "error": "Ошибка",

        # Tabs
        "tab_video_resize": "Изменение размера видео",
        "tab_file_download": "Загрузка файлов",
        "tab_file_rename": "Переименование файлов",

        # Video Resize Tab
        "video_title": "Пакетное изменение размера видео",
        "settings": "Настройки",
        "folder_with_videos": "Папка с видео:",
        "select_video_folder": "Выберите папку с видеофайлами...",
        "browse": "Обзор...",
        "select_video_folder_dialog": "Выберите папку с видеофайлами",
        "target_height": "Целевая высота (px):",
        "remove_audio": "Удалить звуковую дорожку",
        "create_thumbs": "Создать миниатюры (JPG)",
        "processing_log": "Журнал обработки",
        "start_processing": "Начать обработку",
        "stop": "Остановить",
        "processing_complete": "Обработка завершена",
        "processing_stopped": "Обработка остановлена пользователем",
        "videos_not_found": "Видеофайлы не найдены в '{}'",
        "videos_found": "Найдено {} видеофайл(ов) в '{}'",
        "output_folder": "Папка для вывода: {}",
        "thumbs_folder": "Папка для миниатюр: {}",
        "processing_file": "Обработка: {}",
        "completed": "Завершено: {}",
        "error_processing": "Ошибка при обработке: {}",
        "creating_thumb": "Создание миниатюры: {}",
        "thumb_created": "Миниатюра создана: {}",
        "thumb_error": "Ошибка создания миниатюры: {}",
        "stopping_processing": "Остановка обработки...",
        "processing_complete_summary": "Обработка завершена!",
        "successful": "Успешно: {}",
        "errors": "Ошибок: {}",
        "total": "Всего: {}",
        "thumbs_created": "Миниатюр создано: {}",
        "thumbs_errors": "Ошибок миниатюр: {}",
        "processing_complete_msg": "Успешно обработано: {}/{}",
        "please_select_folder": "Пожалуйста, выберите папку с видеофайлами",
        "folder_not_exists": "Папка '{}' не существует или не является директорией",
        "critical_error": "Критическая ошибка: {}",

        # File Download Tab
        "download_title": "Загрузка файлов из URL-ссылок",
        "url_file": "Файл с URL (XLS/XLSX/CSV):",
        "select_url_file": "Выберите файл с URL-ссылками...",
        "select_url_file_dialog": "Выберите файл с URL-ссылками",
        "download_folder": "Папка для загрузки:",
        "select_download_folder": "Выберите папку для сохранения файлов...",
        "select_download_folder_dialog": "Выберите папку для загрузки файлов",
        "download_log": "Журнал загрузки",
        "start_download": "Начать загрузку",
        "download_complete": "Загрузка завершена",
        "reading_file": "Чтение файла: {}",
        "urls_not_found": "В файле не найдено URL-ссылок",
        "urls_found": "Найдено {} уникальных URL-ссылок",
        "download_folder_created": "Папка для загрузки: {}",
        "processing_url": "\n[{}/{}] Обработка: {}",
        "skipped_exists": "Пропущено (файл существует): {}",
        "downloaded": "Загружено: {}",
        "download_error": "Ошибка загрузки: {}",
        "stopping_download": "Остановка загрузки...",
        "download_complete_summary": "Загрузка завершена!",
        "skipped": "Пропущено: {}",
        "total_urls": "Всего URL: {}",
        "download_complete_msg": "Успешно загружено: {}/{}",
        "please_select_url_file": "Пожалуйста, выберите файл с URL-ссылками",
        "file_not_exists": "Файл '{}' не существует или не является файлом",
        "unsupported_format": "Поддерживаются только файлы форматов: XLS, XLSX, CSV",
        "please_select_download_folder": "Пожалуйста, выберите папку для загрузки файлов",
        "column_index_name": "Индекс колонки для имени файла:",
        "column_index_name_tooltip": "Индекс колонки (начиная с 0) для пользовательского имени файла. -1 = не используется",
        "column_index_name_hint": "(-1 = не используется, 0 = первая колонка, 1 = вторая и т.д.)",
        "not_used": "Не используется",
        "renamed_existing": "Переименован существующий файл: {} -> {}",
        "downloaded_renamed": "Загружено и переименовано: {}",
        "downloaded_rename_failed": "Загружено как {}, но не удалось переименовать: {}",

        # File Rename Tab
        "rename_title": "Массовое переименование файлов",
        "folder_with_files": "Папка с файлами:",
        "select_files_folder": "Выберите папку с файлами для переименования...",
        "select_files_folder_dialog": "Выберите папку с файлами для переименования",
        "sort": "Сортировка:",
        "sort_name": "По имени (алфавитная)",
        "sort_number": "По числу в имени",
        "rename_type": "Тип переименования:",
        "rename_sequential": "Последовательная нумерация (1, 2, 3, ...)",
        "rename_numbers_only": "Только цифры из имени",
        "rename_text_only": "Только текст из имени",
        "rename_numbers_only_at_end": "Только число в конце имени",
        "prefix": "Префикс (необязательно):",
        "prefix_placeholder": "Например: photo_",
        "suffix": "Суффикс (необязательно):",
        "suffix_placeholder": "Например: _edited",
        "zero_padding": "Дополнение нулями:",
        "zero_padding_hint": "(0 = не используется, 1 = 09, 2 = 009)",
        "zero_padding_tooltip": "Число нулей перед числом в названии файла (0 = не используется)",
        "dry_run": "Предварительный просмотр (не переименовывать файлы)",
        "rename_log": "Журнал переименования",
        "start_rename": "Начать переименование",
        "rename_complete": "Переименование завершено",
        "files_not_found": "Файлы не найдены в '{}'",
        "files_found": "Найдено {} файл(ов) в '{}'",
        "configuration": "Конфигурация:",
        "folder": "Папка: {}",
        "sort_type": "Сортировка: {}",
        "rename_type_label": "Переименование: {}",
        "prefix_label": "Префикс: '{}'",
        "suffix_label": "Суффикс: '{}'",
        "zero_padding_label": "Дополнение нулями: {}",
        "mode": "Режим: Предварительный просмотр (без изменений)",
        "preview_mode": "Режим предварительного просмотра - показываются планируемые изменения:",
        "stopping_rename": "Остановка переименования...",
        "renamed": "[{}] Переименовано: {} -> {}",
        "preview_renamed": "[{}] {} -> {}",
        "target_exists": "Ошибка: Целевой файл уже существует: {}",
        "rename_error": "Ошибка при переименовании {}: {}",
        "rename_complete_summary": "Переименование завершено!",
        "preview_complete": "Предварительный просмотр завершен! Файлы не были переименованы.",
        "rename_preview_complete": "Предварительный просмотр завершен",
        "rename_preview_msg": "Просмотрено: {}/{} файлов\n\nСнимите галочку 'Предварительный просмотр' для фактического переименования.",
        "rename_complete_msg": "Успешно переименовано: {}/{}",
        "please_select_files_folder": "Пожалуйста, выберите папку с файлами",

        # Language selector
        "language": "Язык:",
        "language_en": "English",
        "language_ru": "Русский",
    }

    def __init__(self, language: str = "en"):
        """
        Initialize translations manager.

        Args:
            language: Language code ('en' or 'ru')
        """
        self.language = language
        self._translations = self.EN if language == "en" else self.RU

    def get(self, key: str, *args) -> str:
        """
        Get translated string for the given key.

        Args:
            key: Translation key
            *args: Optional format arguments

        Returns:
            Translated string (formatted if args provided)
        """
        text = self._translations.get(key, key)
        if args:
            return text.format(*args)
        return text

    def set_language(self, language: str):
        """
        Change current language.

        Args:
            language: Language code ('en' or 'ru')
        """
        self.language = language
        self._translations = self.EN if language == "en" else self.RU

    def get_available_languages(self) -> Dict[str, str]:
        """
        Get available languages.

        Returns:
            Dictionary mapping language code to language name
        """
        return {
            "en": self.get("language_en"),
            "ru": self.get("language_ru")
        }


# Global instance
_translator = Translations("en")


def get_translator() -> Translations:
    """Get global translator instance."""
    return _translator


def set_language(language: str):
    """Set global language."""
    _translator.set_language(language)


def tr(key: str, *args) -> str:
    """
    Shorthand for getting translated text.

    Args:
        key: Translation key
        *args: Optional format arguments

    Returns:
        Translated string
    """
    return _translator.get(key, *args)
