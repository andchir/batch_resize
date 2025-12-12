#!/usr/bin/env python3
"""
Batch Video Resize GUI - PyQt6 application
Provides a graphical interface for batch resizing videos using FFmpeg.
"""

import sys
import os
from pathlib import Path
from typing import Optional, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QSpinBox, QCheckBox, QFileDialog,
    QTextEdit, QProgressBar, QGroupBox, QMessageBox, QTabWidget, QComboBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont

from main import get_video_files, resize_video, create_thumbnail
from download import (
    read_file, get_filename_from_url, download_file
)
from rename import (
    get_files_in_folder, sort_files, rename_files
)


class VideoProcessorThread(QThread):
    """Background thread for processing videos to keep UI responsive."""

    progress = pyqtSignal(int)  # Progress percentage
    log = pyqtSignal(str)  # Log message
    finished = pyqtSignal(dict)  # Processing statistics

    def __init__(self, folder_path: Path, height: int, remove_audio: bool, create_thumbs: bool):
        super().__init__()
        self.folder_path = folder_path
        self.height = height
        self.remove_audio = remove_audio
        self.create_thumbs = create_thumbs
        self._is_running = True

    def stop(self):
        """Stop processing."""
        self._is_running = False

    def run(self):
        """Process videos in background thread."""
        try:
            # Get video files
            video_files = get_video_files(self.folder_path)

            if not video_files:
                self.log.emit(f"Видеофайлы не найдены в '{self.folder_path}'")
                self.finished.emit({
                    'successful': 0,
                    'failed': 0,
                    'total': 0,
                    'thumbs_created': 0,
                    'thumbs_failed': 0
                })
                return

            self.log.emit(f"Найдено {len(video_files)} видеофайл(ов) в '{self.folder_path}'")

            # Create output directory
            output_dir = self.folder_path / "output"
            output_dir.mkdir(exist_ok=True)
            self.log.emit(f"Папка для вывода: {output_dir}")

            # Create thumbs directory if needed
            thumbs_dir = None
            if self.create_thumbs:
                thumbs_dir = self.folder_path / "thumbs"
                thumbs_dir.mkdir(exist_ok=True)
                self.log.emit(f"Папка для миниатюр: {thumbs_dir}")

            # Process each video file
            successful = 0
            failed = 0
            thumbs_created = 0
            thumbs_failed = 0

            for idx, video_file in enumerate(video_files):
                if not self._is_running:
                    self.log.emit("Обработка остановлена пользователем")
                    break

                output_path = output_dir / video_file.name

                self.log.emit(f"Обработка: {video_file.name}")
                if resize_video(video_file, output_path, self.height, self.remove_audio):
                    successful += 1
                    self.log.emit(f"Завершено: {output_path.name}")
                else:
                    failed += 1
                    self.log.emit(f"Ошибка при обработке: {video_file.name}")

                # Create thumbnail if requested
                if self.create_thumbs and self._is_running:
                    thumb_path = thumbs_dir / f"{video_file.stem}.jpg"
                    self.log.emit(f"Создание миниатюры: {thumb_path.name}")
                    if create_thumbnail(output_path, thumb_path):
                        thumbs_created += 1
                        self.log.emit(f"Миниатюра создана: {thumb_path.name}")
                    else:
                        thumbs_failed += 1
                        self.log.emit(f"Ошибка создания миниатюры: {thumb_path.name}")

                # Update progress
                progress_percent = int((idx + 1) / len(video_files) * 100)
                self.progress.emit(progress_percent)

            # Emit final statistics
            self.finished.emit({
                'successful': successful,
                'failed': failed,
                'total': len(video_files),
                'thumbs_created': thumbs_created,
                'thumbs_failed': thumbs_failed
            })

        except Exception as e:
            self.log.emit(f"Критическая ошибка: {str(e)}")
            self.finished.emit({
                'successful': 0,
                'failed': 0,
                'total': 0,
                'thumbs_created': 0,
                'thumbs_failed': 0
            })


class FileDownloaderThread(QThread):
    """Background thread for downloading files from URLs found in XLS/XLSX/CSV files."""

    progress = pyqtSignal(int)  # Progress percentage
    log = pyqtSignal(str)  # Log message
    finished = pyqtSignal(dict)  # Download statistics

    def __init__(self, file_path: Path, output_folder: Path):
        super().__init__()
        self.file_path = file_path
        self.output_folder = output_folder
        self._is_running = True

    def stop(self):
        """Stop downloading."""
        self._is_running = False

    def run(self):
        """Download files in background thread."""
        try:
            # Read file and extract URLs
            self.log.emit(f"Чтение файла: {self.file_path}")
            urls = read_file(self.file_path)

            # Remove duplicates while preserving order
            seen = set()
            unique_urls = []
            for url in urls:
                if url not in seen:
                    seen.add(url)
                    unique_urls.append(url)

            if not unique_urls:
                self.log.emit("В файле не найдено URL-ссылок")
                self.finished.emit({
                    'successful': 0,
                    'failed': 0,
                    'skipped': 0,
                    'total': 0
                })
                return

            self.log.emit(f"Найдено {len(unique_urls)} уникальных URL-ссылок")

            # Create output folder if it doesn't exist
            self.output_folder.mkdir(parents=True, exist_ok=True)
            self.log.emit(f"Папка для загрузки: {self.output_folder}")

            # Download each file
            successful = 0
            failed = 0
            skipped = 0

            for idx, url in enumerate(unique_urls):
                if not self._is_running:
                    self.log.emit("Загрузка остановлена пользователем")
                    break

                self.log.emit(f"\n[{idx + 1}/{len(unique_urls)}] Обработка: {url}")

                # Get filename from URL
                filename = get_filename_from_url(url)
                output_path = self.output_folder / filename

                # Check if file already exists
                if output_path.exists():
                    self.log.emit(f"Пропущено (файл существует): {filename}")
                    skipped += 1
                else:
                    # Download the file
                    if download_file(url, output_path):
                        self.log.emit(f"Загружено: {filename}")
                        successful += 1
                    else:
                        self.log.emit(f"Ошибка загрузки: {url}")
                        failed += 1

                # Update progress
                progress_percent = int((idx + 1) / len(unique_urls) * 100)
                self.progress.emit(progress_percent)

            # Emit final statistics
            self.finished.emit({
                'successful': successful,
                'failed': failed,
                'skipped': skipped,
                'total': len(unique_urls)
            })

        except Exception as e:
            self.log.emit(f"Критическая ошибка: {str(e)}")
            self.finished.emit({
                'successful': 0,
                'failed': 0,
                'skipped': 0,
                'total': 0
            })


class FileRenamerThread(QThread):
    """Background thread for renaming files to keep UI responsive."""

    progress = pyqtSignal(int)  # Progress percentage
    log = pyqtSignal(str)  # Log message
    finished = pyqtSignal(dict)  # Rename statistics

    def __init__(self, folder_path: Path, sort_type: str, rename_type: str,
                 prefix: str = "", suffix: str = "", dry_run: bool = False, zero_num: int = 0):
        super().__init__()
        self.folder_path = folder_path
        self.sort_type = sort_type
        self.rename_type = rename_type
        self.prefix = prefix
        self.suffix = suffix
        self.dry_run = dry_run
        self.zero_num = zero_num
        self._is_running = True

    def stop(self):
        """Stop renaming."""
        self._is_running = False

    def run(self):
        """Rename files in background thread."""
        try:
            # Get all files
            files = get_files_in_folder(self.folder_path)

            if not files:
                self.log.emit(f"Файлы не найдены в '{self.folder_path}'")
                self.finished.emit({
                    'successful': 0,
                    'failed': 0,
                    'total': 0
                })
                return

            self.log.emit(f"Найдено {len(files)} файл(ов) в '{self.folder_path}'")

            # Display configuration
            self.log.emit(f"Конфигурация:")
            self.log.emit(f"  Папка: {self.folder_path}")
            self.log.emit(f"  Сортировка: {self.sort_type}")
            self.log.emit(f"  Переименование: {self.rename_type}")
            if self.prefix:
                self.log.emit(f"  Префикс: '{self.prefix}'")
            if self.suffix:
                self.log.emit(f"  Суффикс: '{self.suffix}'")
            if self.zero_num > 0:
                self.log.emit(f"  Дополнение нулями: {self.zero_num}")
            if self.dry_run:
                self.log.emit(f"  Режим: Предварительный просмотр (без изменений)")
            self.log.emit("")

            # Sort files
            sorted_files = sort_files(files, self.sort_type)

            if self.dry_run:
                self.log.emit("Режим предварительного просмотра - показываются планируемые изменения:")
                self.log.emit("=" * 60)

            successful = 0
            failed = 0

            # Keep track of new names to avoid duplicates
            used_names = set()

            from rename import generate_new_filename

            for index, file_path in enumerate(sorted_files, start=1):
                if not self._is_running:
                    self.log.emit("Переименование остановлено пользователем")
                    break

                try:
                    # Generate new filename
                    new_filename = generate_new_filename(
                        file_path, index, self.rename_type, self.prefix, self.suffix, self.zero_num
                    )

                    # Handle duplicate names by adding a counter
                    original_new_filename = new_filename
                    counter = 1
                    while new_filename in used_names:
                        # Insert counter before extension
                        stem = Path(original_new_filename).stem
                        ext = Path(original_new_filename).suffix
                        new_filename = f"{stem}_{counter}{ext}"
                        counter += 1

                    used_names.add(new_filename)
                    new_path = file_path.parent / new_filename

                    # Check if target file already exists (and it's not the same file)
                    if new_path.exists() and new_path.resolve() != file_path.resolve():
                        self.log.emit(f"Ошибка: Целевой файл уже существует: {new_filename}")
                        failed += 1
                        continue

                    if self.dry_run:
                        self.log.emit(f"[{index}] {file_path.name} -> {new_filename}")
                    else:
                        # Perform the rename
                        file_path.rename(new_path)
                        self.log.emit(f"[{index}] Переименовано: {file_path.name} -> {new_filename}")

                    successful += 1

                except Exception as e:
                    self.log.emit(f"Ошибка при переименовании {file_path.name}: {str(e)}")
                    failed += 1

                # Update progress
                progress_percent = int((index) / len(sorted_files) * 100)
                self.progress.emit(progress_percent)

            # Emit final statistics
            self.finished.emit({
                'successful': successful,
                'failed': failed,
                'total': len(files)
            })

        except Exception as e:
            self.log.emit(f"Критическая ошибка: {str(e)}")
            self.finished.emit({
                'successful': 0,
                'failed': 0,
                'total': 0
            })


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.processor_thread: Optional[VideoProcessorThread] = None
        self.downloader_thread: Optional[FileDownloaderThread] = None
        self.renamer_thread: Optional[FileRenamerThread] = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Batch Media Tools")
        self.setMinimumSize(800, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_video_resize_tab()
        self.create_file_download_tab()
        self.create_file_rename_tab()

        # Status bar
        self.statusBar().showMessage("Готов к работе")

    def create_video_resize_tab(self):
        """Create the video resize tab."""
        video_tab = QWidget()
        tab_layout = QVBoxLayout(video_tab)

        # Title
        title_label = QLabel("Пакетное изменение размера видео")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab_layout.addWidget(title_label)

        # Input group
        input_group = QGroupBox("Настройки")
        input_layout = QVBoxLayout()

        # Folder selection
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Папка с видео:"))
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Выберите папку с видеофайлами...")
        folder_layout.addWidget(self.folder_input)
        self.browse_button = QPushButton("Обзор...")
        self.browse_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.browse_button)
        input_layout.addLayout(folder_layout)

        # Height setting
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Целевая высота (px):"))
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setMinimum(1)
        self.height_spinbox.setMaximum(8192)
        self.height_spinbox.setValue(720)
        self.height_spinbox.setSuffix(" px")
        height_layout.addWidget(self.height_spinbox)
        height_layout.addStretch()
        input_layout.addLayout(height_layout)

        # Options
        self.remove_audio_checkbox = QCheckBox("Удалить звуковую дорожку")
        input_layout.addWidget(self.remove_audio_checkbox)

        self.create_thumbs_checkbox = QCheckBox("Создать миниатюры (JPG)")
        input_layout.addWidget(self.create_thumbs_checkbox)

        input_group.setLayout(input_layout)
        tab_layout.addWidget(input_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        tab_layout.addWidget(self.progress_bar)

        # Log output
        log_group = QGroupBox("Журнал обработки")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        tab_layout.addWidget(log_group)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.start_button = QPushButton("Начать обработку")
        self.start_button.clicked.connect(self.start_processing)
        self.start_button.setMinimumWidth(150)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Остановить")
        self.stop_button.clicked.connect(self.stop_processing)
        self.stop_button.setEnabled(False)
        self.stop_button.setMinimumWidth(150)
        button_layout.addWidget(self.stop_button)

        button_layout.addStretch()
        tab_layout.addLayout(button_layout)

        # Add tab to tab widget
        self.tab_widget.addTab(video_tab, "Изменение размера видео")

    def create_file_download_tab(self):
        """Create the file download tab."""
        download_tab = QWidget()
        tab_layout = QVBoxLayout(download_tab)

        # Title
        title_label = QLabel("Загрузка файлов из URL-ссылок")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab_layout.addWidget(title_label)

        # Input group
        input_group = QGroupBox("Настройки")
        input_layout = QVBoxLayout()

        # Input file selection
        input_file_layout = QHBoxLayout()
        input_file_layout.addWidget(QLabel("Файл с URL (XLS/XLSX/CSV):"))
        self.download_file_input = QLineEdit()
        self.download_file_input.setPlaceholderText("Выберите файл с URL-ссылками...")
        input_file_layout.addWidget(self.download_file_input)
        self.download_browse_file_button = QPushButton("Обзор...")
        self.download_browse_file_button.clicked.connect(self.browse_download_file)
        input_file_layout.addWidget(self.download_browse_file_button)
        input_layout.addLayout(input_file_layout)

        # Output folder selection
        output_folder_layout = QHBoxLayout()
        output_folder_layout.addWidget(QLabel("Папка для загрузки:"))
        self.download_folder_input = QLineEdit()
        self.download_folder_input.setPlaceholderText("Выберите папку для сохранения файлов...")
        output_folder_layout.addWidget(self.download_folder_input)
        self.download_browse_folder_button = QPushButton("Обзор...")
        self.download_browse_folder_button.clicked.connect(self.browse_download_folder)
        output_folder_layout.addWidget(self.download_browse_folder_button)
        input_layout.addLayout(output_folder_layout)

        input_group.setLayout(input_layout)
        tab_layout.addWidget(input_group)

        # Progress bar
        self.download_progress_bar = QProgressBar()
        self.download_progress_bar.setValue(0)
        tab_layout.addWidget(self.download_progress_bar)

        # Log output
        log_group = QGroupBox("Журнал загрузки")
        log_layout = QVBoxLayout()
        self.download_log_text = QTextEdit()
        self.download_log_text.setReadOnly(True)
        self.download_log_text.setMaximumHeight(200)
        log_layout.addWidget(self.download_log_text)
        log_group.setLayout(log_layout)
        tab_layout.addWidget(log_group)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.download_start_button = QPushButton("Начать загрузку")
        self.download_start_button.clicked.connect(self.start_downloading)
        self.download_start_button.setMinimumWidth(150)
        button_layout.addWidget(self.download_start_button)

        self.download_stop_button = QPushButton("Остановить")
        self.download_stop_button.clicked.connect(self.stop_downloading)
        self.download_stop_button.setEnabled(False)
        self.download_stop_button.setMinimumWidth(150)
        button_layout.addWidget(self.download_stop_button)

        button_layout.addStretch()
        tab_layout.addLayout(button_layout)

        # Add tab to tab widget
        self.tab_widget.addTab(download_tab, "Загрузка файлов")

    def create_file_rename_tab(self):
        """Create the file rename tab."""
        rename_tab = QWidget()
        tab_layout = QVBoxLayout(rename_tab)

        # Title
        title_label = QLabel("Массовое переименование файлов")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab_layout.addWidget(title_label)

        # Input group
        input_group = QGroupBox("Настройки")
        input_layout = QVBoxLayout()

        # Folder selection
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Папка с файлами:"))
        self.rename_folder_input = QLineEdit()
        self.rename_folder_input.setPlaceholderText("Выберите папку с файлами для переименования...")
        folder_layout.addWidget(self.rename_folder_input)
        self.rename_browse_button = QPushButton("Обзор...")
        self.rename_browse_button.clicked.connect(self.browse_rename_folder)
        folder_layout.addWidget(self.rename_browse_button)
        input_layout.addLayout(folder_layout)

        # Sort type selection
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel("Сортировка:"))

        self.rename_sort_combo = QComboBox()
        self.rename_sort_combo.addItem("По имени (алфавитная)", "name")
        self.rename_sort_combo.addItem("По числу в имени", "number")
        sort_layout.addWidget(self.rename_sort_combo)
        sort_layout.addStretch()
        input_layout.addLayout(sort_layout)

        # Rename type selection
        rename_type_layout = QHBoxLayout()
        rename_type_layout.addWidget(QLabel("Тип переименования:"))
        self.rename_type_combo = QComboBox()
        self.rename_type_combo.addItem("Последовательная нумерация (1, 2, 3, ...)", "sequential")
        self.rename_type_combo.addItem("Только цифры из имени", "numbers_only")
        self.rename_type_combo.addItem("Только текст из имени", "text_only")
        self.rename_type_combo.addItem("Только число в конце имени", "numbers_only_at_end")
        rename_type_layout.addWidget(self.rename_type_combo)
        rename_type_layout.addStretch()
        input_layout.addLayout(rename_type_layout)

        # Prefix input
        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(QLabel("Префикс (необязательно):"))
        self.rename_prefix_input = QLineEdit()
        self.rename_prefix_input.setPlaceholderText("Например: photo_")
        prefix_layout.addWidget(self.rename_prefix_input)
        prefix_layout.addStretch()
        input_layout.addLayout(prefix_layout)

        # Suffix input
        suffix_layout = QHBoxLayout()
        suffix_layout.addWidget(QLabel("Суффикс (необязательно):"))
        self.rename_suffix_input = QLineEdit()
        self.rename_suffix_input.setPlaceholderText("Например: _edited")
        suffix_layout.addWidget(self.rename_suffix_input)
        suffix_layout.addStretch()
        input_layout.addLayout(suffix_layout)

        # Zero padding input
        zero_num_layout = QHBoxLayout()
        zero_num_layout.addWidget(QLabel("Дополнение нулями:"))
        self.rename_zero_num_spinbox = QSpinBox()
        self.rename_zero_num_spinbox.setMinimum(0)
        self.rename_zero_num_spinbox.setMaximum(10)
        self.rename_zero_num_spinbox.setValue(0)
        self.rename_zero_num_spinbox.setToolTip("Число нулей перед числом в названии файла (0 = не используется)")
        zero_num_layout.addWidget(self.rename_zero_num_spinbox)
        zero_num_layout.addWidget(QLabel("(0 = не используется, 1 = 09, 2 = 009)"))
        zero_num_layout.addStretch()
        input_layout.addLayout(zero_num_layout)

        # Dry run checkbox
        self.rename_dry_run_checkbox = QCheckBox("Предварительный просмотр (не переименовывать файлы)")
        self.rename_dry_run_checkbox.setChecked(True)  # Enable by default for safety
        input_layout.addWidget(self.rename_dry_run_checkbox)

        input_group.setLayout(input_layout)
        tab_layout.addWidget(input_group)

        # Progress bar
        self.rename_progress_bar = QProgressBar()
        self.rename_progress_bar.setValue(0)
        tab_layout.addWidget(self.rename_progress_bar)

        # Log output
        log_group = QGroupBox("Журнал переименования")
        log_layout = QVBoxLayout()
        self.rename_log_text = QTextEdit()
        self.rename_log_text.setReadOnly(True)
        self.rename_log_text.setMaximumHeight(200)
        log_layout.addWidget(self.rename_log_text)
        log_group.setLayout(log_layout)
        tab_layout.addWidget(log_group)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.rename_start_button = QPushButton("Начать переименование")
        self.rename_start_button.clicked.connect(self.start_renaming)
        self.rename_start_button.setMinimumWidth(150)
        button_layout.addWidget(self.rename_start_button)

        self.rename_stop_button = QPushButton("Остановить")
        self.rename_stop_button.clicked.connect(self.stop_renaming)
        self.rename_stop_button.setEnabled(False)
        self.rename_stop_button.setMinimumWidth(150)
        button_layout.addWidget(self.rename_stop_button)

        button_layout.addStretch()
        tab_layout.addLayout(button_layout)

        # Add tab to tab widget
        self.tab_widget.addTab(rename_tab, "Переименование файлов")

    def browse_folder(self):
        """Open folder browser dialog."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку с видеофайлами",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.folder_input.setText(folder)

    def browse_download_file(self):
        """Open file browser dialog for input file."""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл с URL-ссылками",
            "",
            "Spreadsheet Files (*.xls *.xlsx *.csv);;All Files (*)"
        )
        if file:
            self.download_file_input.setText(file)

    def browse_download_folder(self):
        """Open folder browser dialog for download folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для загрузки файлов",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.download_folder_input.setText(folder)

    def start_processing(self):
        """Start video processing."""
        # Validate input
        folder_path = self.folder_input.text().strip()
        if not folder_path:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Пожалуйста, выберите папку с видеофайлами"
            )
            return

        folder_path = Path(folder_path)
        if not folder_path.exists() or not folder_path.is_dir():
            QMessageBox.warning(
                self,
                "Ошибка",
                f"Папка '{folder_path}' не существует или не является директорией"
            )
            return

        # Clear log and reset progress
        self.log_text.clear()
        self.progress_bar.setValue(0)

        # Disable start button, enable stop button
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.browse_button.setEnabled(False)

        # Get settings
        height = self.height_spinbox.value()
        remove_audio = self.remove_audio_checkbox.isChecked()
        create_thumbs = self.create_thumbs_checkbox.isChecked()

        # Start processing thread
        self.processor_thread = VideoProcessorThread(
            folder_path,
            height,
            remove_audio,
            create_thumbs
        )
        self.processor_thread.progress.connect(self.update_progress)
        self.processor_thread.log.connect(self.add_log)
        self.processor_thread.finished.connect(self.processing_finished)
        self.processor_thread.start()

        self.statusBar().showMessage("Обработка...")

    def stop_processing(self):
        """Stop video processing."""
        if self.processor_thread and self.processor_thread.isRunning():
            self.processor_thread.stop()
            self.add_log("Остановка обработки...")
            self.stop_button.setEnabled(False)

    def update_progress(self, value: int):
        """Update progress bar."""
        self.progress_bar.setValue(value)

    def add_log(self, message: str):
        """Add message to log."""
        self.log_text.append(message)
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def processing_finished(self, stats: dict):
        """Handle processing completion."""
        # Re-enable buttons
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.browse_button.setEnabled(True)

        # Show summary
        self.add_log("\n" + "=" * 50)
        self.add_log("Обработка завершена!")
        self.add_log(f"Успешно: {stats['successful']}")
        self.add_log(f"Ошибок: {stats['failed']}")
        self.add_log(f"Всего: {stats['total']}")

        if self.create_thumbs_checkbox.isChecked():
            self.add_log(f"Миниатюр создано: {stats['thumbs_created']}")
            self.add_log(f"Ошибок миниатюр: {stats['thumbs_failed']}")

        self.add_log("=" * 50)

        self.statusBar().showMessage("Готов к работе")

        # Show completion message
        if stats['total'] > 0:
            QMessageBox.information(
                self,
                "Обработка завершена",
                f"Успешно обработано: {stats['successful']}/{stats['total']}"
            )

    def start_downloading(self):
        """Start file downloading."""
        # Validate input
        file_path = self.download_file_input.text().strip()
        if not file_path:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Пожалуйста, выберите файл с URL-ссылками"
            )
            return

        file_path = Path(file_path)
        if not file_path.exists() or not file_path.is_file():
            QMessageBox.warning(
                self,
                "Ошибка",
                f"Файл '{file_path}' не существует или не является файлом"
            )
            return

        # Check file extension
        if file_path.suffix.lower() not in ['.csv', '.xlsx', '.xls']:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Поддерживаются только файлы форматов: XLS, XLSX, CSV"
            )
            return

        # Validate output folder
        output_folder = self.download_folder_input.text().strip()
        if not output_folder:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Пожалуйста, выберите папку для загрузки файлов"
            )
            return

        output_folder = Path(output_folder)

        # Clear log and reset progress
        self.download_log_text.clear()
        self.download_progress_bar.setValue(0)

        # Disable start button, enable stop button
        self.download_start_button.setEnabled(False)
        self.download_stop_button.setEnabled(True)
        self.download_browse_file_button.setEnabled(False)
        self.download_browse_folder_button.setEnabled(False)

        # Start downloading thread
        self.downloader_thread = FileDownloaderThread(file_path, output_folder)
        self.downloader_thread.progress.connect(self.update_download_progress)
        self.downloader_thread.log.connect(self.add_download_log)
        self.downloader_thread.finished.connect(self.downloading_finished)
        self.downloader_thread.start()

        self.statusBar().showMessage("Загрузка...")

    def stop_downloading(self):
        """Stop file downloading."""
        if self.downloader_thread and self.downloader_thread.isRunning():
            self.downloader_thread.stop()
            self.add_download_log("Остановка загрузки...")
            self.download_stop_button.setEnabled(False)

    def update_download_progress(self, value: int):
        """Update download progress bar."""
        self.download_progress_bar.setValue(value)

    def add_download_log(self, message: str):
        """Add message to download log."""
        self.download_log_text.append(message)
        # Auto-scroll to bottom
        cursor = self.download_log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.download_log_text.setTextCursor(cursor)

    def downloading_finished(self, stats: dict):
        """Handle downloading completion."""
        # Re-enable buttons
        self.download_start_button.setEnabled(True)
        self.download_stop_button.setEnabled(False)
        self.download_browse_file_button.setEnabled(True)
        self.download_browse_folder_button.setEnabled(True)

        # Show summary
        self.add_download_log("\n" + "=" * 50)
        self.add_download_log("Загрузка завершена!")
        self.add_download_log(f"Успешно: {stats['successful']}")
        self.add_download_log(f"Ошибок: {stats['failed']}")
        self.add_download_log(f"Пропущено: {stats['skipped']}")
        self.add_download_log(f"Всего URL: {stats['total']}")
        self.add_download_log("=" * 50)

        self.statusBar().showMessage("Готов к работе")

        # Show completion message
        if stats['total'] > 0:
            QMessageBox.information(
                self,
                "Загрузка завершена",
                f"Успешно загружено: {stats['successful']}/{stats['total']}"
            )

    def browse_rename_folder(self):
        """Open folder browser dialog for rename folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку с файлами для переименования",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.rename_folder_input.setText(folder)

    def start_renaming(self):
        """Start file renaming."""
        # Validate input
        folder_path = self.rename_folder_input.text().strip()
        if not folder_path:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Пожалуйста, выберите папку с файлами"
            )
            return

        folder_path = Path(folder_path)
        if not folder_path.exists() or not folder_path.is_dir():
            QMessageBox.warning(
                self,
                "Ошибка",
                f"Папка '{folder_path}' не существует или не является директорией"
            )
            return

        # Clear log and reset progress
        self.rename_log_text.clear()
        self.rename_progress_bar.setValue(0)

        # Disable start button, enable stop button
        self.rename_start_button.setEnabled(False)
        self.rename_stop_button.setEnabled(True)
        self.rename_browse_button.setEnabled(False)

        # Get settings
        sort_type = self.rename_sort_combo.currentData()
        rename_type = self.rename_type_combo.currentData()
        prefix = self.rename_prefix_input.text()
        suffix = self.rename_suffix_input.text()
        dry_run = self.rename_dry_run_checkbox.isChecked()
        zero_num = self.rename_zero_num_spinbox.value()

        # Start renaming thread
        self.renamer_thread = FileRenamerThread(
            folder_path,
            sort_type,
            rename_type,
            prefix,
            suffix,
            dry_run,
            zero_num
        )
        self.renamer_thread.progress.connect(self.update_rename_progress)
        self.renamer_thread.log.connect(self.add_rename_log)
        self.renamer_thread.finished.connect(self.renaming_finished)
        self.renamer_thread.start()

        self.statusBar().showMessage("Переименование...")

    def stop_renaming(self):
        """Stop file renaming."""
        if self.renamer_thread and self.renamer_thread.isRunning():
            self.renamer_thread.stop()
            self.add_rename_log("Остановка переименования...")
            self.rename_stop_button.setEnabled(False)

    def update_rename_progress(self, value: int):
        """Update rename progress bar."""
        self.rename_progress_bar.setValue(value)

    def add_rename_log(self, message: str):
        """Add message to rename log."""
        self.rename_log_text.append(message)
        # Auto-scroll to bottom
        cursor = self.rename_log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.rename_log_text.setTextCursor(cursor)

    def renaming_finished(self, stats: dict):
        """Handle renaming completion."""
        # Re-enable buttons
        self.rename_start_button.setEnabled(True)
        self.rename_stop_button.setEnabled(False)
        self.rename_browse_button.setEnabled(True)

        # Show summary
        self.add_rename_log("\n" + "=" * 50)
        if self.rename_dry_run_checkbox.isChecked():
            self.add_rename_log("Предварительный просмотр завершен! Файлы не были переименованы.")
        else:
            self.add_rename_log("Переименование завершено!")
        self.add_rename_log(f"Успешно: {stats['successful']}")
        self.add_rename_log(f"Ошибок: {stats['failed']}")
        self.add_rename_log(f"Всего: {stats['total']}")
        self.add_rename_log("=" * 50)

        self.statusBar().showMessage("Готов к работе")

        # Show completion message
        if stats['total'] > 0:
            if self.rename_dry_run_checkbox.isChecked():
                QMessageBox.information(
                    self,
                    "Предварительный просмотр завершен",
                    f"Просмотрено: {stats['successful']}/{stats['total']} файлов\n\n"
                    "Снимите галочку 'Предварительный просмотр' для фактического переименования."
                )
            else:
                QMessageBox.information(
                    self,
                    "Переименование завершено",
                    f"Успешно переименовано: {stats['successful']}/{stats['total']}"
                )


def main():
    """Main entry point for GUI application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
