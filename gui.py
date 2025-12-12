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
from translations import get_translator, tr


class VideoProcessorThread(QThread):
    """Background thread for processing videos to keep UI responsive."""

    progress = pyqtSignal(int)  # Progress percentage
    log = pyqtSignal(str)  # Log message
    finished = pyqtSignal(dict)  # Processing statistics

    def __init__(self, folder_path: Path, height: int, remove_audio: bool, create_thumbs: bool, translator):
        super().__init__()
        self.folder_path = folder_path
        self.height = height
        self.remove_audio = remove_audio
        self.create_thumbs = create_thumbs
        self.translator = translator
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
                self.log.emit(self.translator.get("videos_not_found", self.folder_path))
                self.finished.emit({
                    'successful': 0,
                    'failed': 0,
                    'total': 0,
                    'thumbs_created': 0,
                    'thumbs_failed': 0
                })
                return

            self.log.emit(self.translator.get("videos_found", len(video_files), self.folder_path))

            # Create output directory
            output_dir = self.folder_path / "output"
            output_dir.mkdir(exist_ok=True)
            self.log.emit(self.translator.get("output_folder", output_dir))

            # Create thumbs directory if needed
            thumbs_dir = None
            if self.create_thumbs:
                thumbs_dir = self.folder_path / "thumbs"
                thumbs_dir.mkdir(exist_ok=True)
                self.log.emit(self.translator.get("thumbs_folder", thumbs_dir))

            # Process each video file
            successful = 0
            failed = 0
            thumbs_created = 0
            thumbs_failed = 0

            for idx, video_file in enumerate(video_files):
                if not self._is_running:
                    self.log.emit(self.translator.get("processing_stopped"))
                    break

                output_path = output_dir / video_file.name

                self.log.emit(self.translator.get("processing_file", video_file.name))
                if resize_video(video_file, output_path, self.height, self.remove_audio):
                    successful += 1
                    self.log.emit(self.translator.get("completed", output_path.name))
                else:
                    failed += 1
                    self.log.emit(self.translator.get("error_processing", video_file.name))

                # Create thumbnail if requested
                if self.create_thumbs and self._is_running:
                    thumb_path = thumbs_dir / f"{video_file.stem}.jpg"
                    self.log.emit(self.translator.get("creating_thumb", thumb_path.name))
                    if create_thumbnail(output_path, thumb_path):
                        thumbs_created += 1
                        self.log.emit(self.translator.get("thumb_created", thumb_path.name))
                    else:
                        thumbs_failed += 1
                        self.log.emit(self.translator.get("thumb_error", thumb_path.name))

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
            self.log.emit(self.translator.get("critical_error", str(e)))
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

    def __init__(self, file_path: Path, output_folder: Path, column_index_name: int, translator):
        super().__init__()
        self.file_path = file_path
        self.output_folder = output_folder
        self.column_index_name = column_index_name
        self.translator = translator
        self._is_running = True

    def stop(self):
        """Stop downloading."""
        self._is_running = False

    def run(self):
        """Download files in background thread."""
        try:
            # Read file and extract URLs with custom filenames
            self.log.emit(self.translator.get("reading_file", self.file_path))
            url_data = read_file(self.file_path, self.column_index_name)

            # Remove duplicates while preserving order
            seen = set()
            unique_url_data = []
            for url, custom_name in url_data:
                if url not in seen:
                    seen.add(url)
                    unique_url_data.append((url, custom_name))

            if not unique_url_data:
                self.log.emit(self.translator.get("urls_not_found"))
                self.finished.emit({
                    'successful': 0,
                    'failed': 0,
                    'skipped': 0,
                    'renamed': 0,
                    'total': 0
                })
                return

            self.log.emit(self.translator.get("urls_found", len(unique_url_data)))

            # Create output folder if it doesn't exist
            self.output_folder.mkdir(parents=True, exist_ok=True)
            self.log.emit(self.translator.get("download_folder_created", self.output_folder))

            # Download each file
            successful = 0
            failed = 0
            skipped = 0
            renamed = 0

            for idx, (url, custom_name) in enumerate(unique_url_data):
                if not self._is_running:
                    self.log.emit(self.translator.get("processing_stopped"))
                    break

                self.log.emit(self.translator.get("processing_url", idx + 1, len(unique_url_data), url))

                # Get filename from URL
                original_filename = get_filename_from_url(url)
                original_path = self.output_folder / original_filename

                # Determine final filename
                final_filename = original_filename
                final_path = original_path

                if custom_name:
                    # Preserve file extension from original filename
                    original_ext = Path(original_filename).suffix
                    # If custom_name already has extension, use it as is, otherwise add original extension
                    if Path(custom_name).suffix:
                        final_filename = custom_name
                    else:
                        final_filename = custom_name + original_ext
                    final_path = self.output_folder / final_filename

                # Check if final file already exists
                if final_path.exists():
                    self.log.emit(self.translator.get("skipped_exists", final_filename))
                    skipped += 1
                    # Update progress
                    progress_percent = int((idx + 1) / len(unique_url_data) * 100)
                    self.progress.emit(progress_percent)
                    continue

                # Check if original file already exists
                if original_path.exists() and original_path != final_path:
                    # File with original name exists, and we have a custom name
                    if custom_name:
                        # Rename the existing file
                        try:
                            original_path.rename(final_path)
                            self.log.emit(self.translator.get("renamed_existing", original_filename, final_filename))
                            renamed += 1
                            skipped += 1
                        except Exception as e:
                            self.log.emit(self.translator.get("rename_error", original_filename, str(e)))
                            failed += 1
                    else:
                        # No custom name, file already exists
                        self.log.emit(self.translator.get("skipped_exists", original_filename))
                        skipped += 1

                    # Update progress
                    progress_percent = int((idx + 1) / len(unique_url_data) * 100)
                    self.progress.emit(progress_percent)
                    continue

                # Download the file to original path first
                if download_file(url, original_path):
                    # If we have a custom name and it's different from original, rename
                    if custom_name and final_path != original_path:
                        try:
                            original_path.rename(final_path)
                            self.log.emit(self.translator.get("downloaded_renamed", final_filename))
                            renamed += 1
                        except Exception as e:
                            self.log.emit(self.translator.get("downloaded_rename_failed", original_filename, str(e)))
                    else:
                        self.log.emit(self.translator.get("downloaded", original_filename))
                    successful += 1
                else:
                    self.log.emit(self.translator.get("download_error", url))
                    failed += 1

                # Update progress
                progress_percent = int((idx + 1) / len(unique_url_data) * 100)
                self.progress.emit(progress_percent)

            # Emit final statistics
            self.finished.emit({
                'successful': successful,
                'failed': failed,
                'skipped': skipped,
                'renamed': renamed,
                'total': len(unique_url_data)
            })

        except Exception as e:
            self.log.emit(self.translator.get("critical_error", str(e)))
            self.finished.emit({
                'successful': 0,
                'failed': 0,
                'skipped': 0,
                'renamed': 0,
                'total': 0
            })


class FileRenamerThread(QThread):
    """Background thread for renaming files to keep UI responsive."""

    progress = pyqtSignal(int)  # Progress percentage
    log = pyqtSignal(str)  # Log message
    finished = pyqtSignal(dict)  # Rename statistics

    def __init__(self, folder_path: Path, sort_type: str, rename_type: str,
                 prefix: str = "", suffix: str = "", dry_run: bool = False, zero_num: int = 0, translator=None):
        super().__init__()
        self.folder_path = folder_path
        self.sort_type = sort_type
        self.rename_type = rename_type
        self.prefix = prefix
        self.suffix = suffix
        self.dry_run = dry_run
        self.zero_num = zero_num
        self.translator = translator
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
                self.log.emit(self.translator.get("files_not_found", self.folder_path))
                self.finished.emit({
                    'successful': 0,
                    'failed': 0,
                    'total': 0
                })
                return

            self.log.emit(self.translator.get("files_found", len(files), self.folder_path))

            # Display configuration
            self.log.emit(self.translator.get("configuration"))
            self.log.emit(self.translator.get("folder", self.folder_path))
            self.log.emit(self.translator.get("sort_type", self.sort_type))
            self.log.emit(self.translator.get("rename_type_label", self.rename_type))
            if self.prefix:
                self.log.emit(self.translator.get("prefix_label", self.prefix))
            if self.suffix:
                self.log.emit(self.translator.get("suffix_label", self.suffix))
            if self.zero_num > 0:
                self.log.emit(self.translator.get("zero_padding_label", self.zero_num))
            if self.dry_run:
                self.log.emit(self.translator.get("mode"))
            self.log.emit("")

            # Sort files
            sorted_files = sort_files(files, self.sort_type)

            if self.dry_run:
                self.log.emit(self.translator.get("preview_mode"))
                self.log.emit("=" * 60)

            successful = 0
            failed = 0

            # Keep track of new names to avoid duplicates
            used_names = set()

            from rename import generate_new_filename

            for index, file_path in enumerate(sorted_files, start=1):
                if not self._is_running:
                    self.log.emit(self.translator.get("processing_stopped"))
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
                        self.log.emit(self.translator.get("target_exists", new_filename))
                        failed += 1
                        continue

                    if self.dry_run:
                        self.log.emit(self.translator.get("preview_renamed", index, file_path.name, new_filename))
                    else:
                        # Perform the rename
                        file_path.rename(new_path)
                        self.log.emit(self.translator.get("renamed", index, file_path.name, new_filename))

                    successful += 1

                except Exception as e:
                    self.log.emit(self.translator.get("rename_error", file_path.name, str(e)))
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
            self.log.emit(self.translator.get("critical_error", str(e)))
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
        self.translator = get_translator()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(self.translator.get("window_title"))
        self.setMinimumSize(800, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Language selector
        self.create_language_selector(main_layout)

        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_video_resize_tab()
        self.create_file_download_tab()
        self.create_file_rename_tab()

        # Status bar
        self.statusBar().showMessage(self.translator.get("ready"))

    def create_language_selector(self, layout: QVBoxLayout):
        """Create language selector widget."""
        lang_layout = QHBoxLayout()
        lang_layout.addStretch()

        self.lang_label = QLabel(self.translator.get("language"))
        lang_layout.addWidget(self.lang_label)

        self.language_combo = QComboBox()
        self.language_combo.addItem(self.translator.get("language_en"), "en")
        self.language_combo.addItem(self.translator.get("language_ru"), "ru")

        # Set current language
        current_lang = self.translator.language
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        lang_layout.addWidget(self.language_combo)

        layout.addLayout(lang_layout)

    def on_language_changed(self, index: int):
        """Handle language change."""
        new_language = self.language_combo.itemData(index)
        self.translator.set_language(new_language)

        # Update all UI elements with new translations
        self.update_ui_translations()

    def update_ui_translations(self):
        """Update all UI elements with current language translations."""
        # Window title
        self.setWindowTitle(self.translator.get("window_title"))

        # Language selector
        self.lang_label.setText(self.translator.get("language"))
        # Update combo box items without triggering the change event
        self.language_combo.blockSignals(True)
        self.language_combo.setItemText(0, self.translator.get("language_en"))
        self.language_combo.setItemText(1, self.translator.get("language_ru"))
        self.language_combo.blockSignals(False)

        # Update tab titles
        self.tab_widget.setTabText(0, self.translator.get("tab_video_resize"))
        self.tab_widget.setTabText(1, self.translator.get("tab_file_download"))
        self.tab_widget.setTabText(2, self.translator.get("tab_file_rename"))

        # Video Resize Tab
        self.video_title_label.setText(self.translator.get("video_title"))
        self.video_input_group.setTitle(self.translator.get("settings"))
        self.video_folder_label.setText(self.translator.get("folder_with_videos"))
        self.folder_input.setPlaceholderText(self.translator.get("select_video_folder"))
        self.browse_button.setText(self.translator.get("browse"))
        self.video_height_label.setText(self.translator.get("target_height"))
        self.remove_audio_checkbox.setText(self.translator.get("remove_audio"))
        self.create_thumbs_checkbox.setText(self.translator.get("create_thumbs"))
        self.video_log_group.setTitle(self.translator.get("processing_log"))
        self.start_button.setText(self.translator.get("start_processing"))
        self.stop_button.setText(self.translator.get("stop"))

        # File Download Tab
        self.download_title_label.setText(self.translator.get("download_title"))
        self.download_input_group.setTitle(self.translator.get("settings"))
        self.download_url_file_label.setText(self.translator.get("url_file"))
        self.download_file_input.setPlaceholderText(self.translator.get("select_url_file"))
        self.download_browse_file_button.setText(self.translator.get("browse"))
        self.download_folder_label.setText(self.translator.get("download_folder"))
        self.download_folder_input.setPlaceholderText(self.translator.get("select_download_folder"))
        self.download_browse_folder_button.setText(self.translator.get("browse"))
        self.download_column_index_label.setText(self.translator.get("column_index_name"))
        self.download_column_index_spinbox.setSpecialValueText(self.translator.get("not_used"))
        self.download_column_index_spinbox.setToolTip(self.translator.get("column_index_name_tooltip"))
        self.download_column_index_hint_label.setText(self.translator.get("column_index_name_hint"))
        self.download_log_group.setTitle(self.translator.get("download_log"))
        self.download_start_button.setText(self.translator.get("start_download"))
        self.download_stop_button.setText(self.translator.get("stop"))

        # File Rename Tab
        self.rename_title_label.setText(self.translator.get("rename_title"))
        self.rename_input_group.setTitle(self.translator.get("settings"))
        self.rename_folder_label.setText(self.translator.get("folder_with_files"))
        self.rename_folder_input.setPlaceholderText(self.translator.get("select_files_folder"))
        self.rename_browse_button.setText(self.translator.get("browse"))
        self.rename_sort_label.setText(self.translator.get("sort"))

        # Update rename sort combo box items
        self.rename_sort_combo.blockSignals(True)
        self.rename_sort_combo.setItemText(0, self.translator.get("sort_name"))
        self.rename_sort_combo.setItemText(1, self.translator.get("sort_number"))
        self.rename_sort_combo.blockSignals(False)

        self.rename_type_label.setText(self.translator.get("rename_type"))

        # Update rename type combo box items
        self.rename_type_combo.blockSignals(True)
        self.rename_type_combo.setItemText(0, self.translator.get("rename_sequential"))
        self.rename_type_combo.setItemText(1, self.translator.get("rename_numbers_only"))
        self.rename_type_combo.setItemText(2, self.translator.get("rename_text_only"))
        self.rename_type_combo.setItemText(3, self.translator.get("rename_numbers_only_at_end"))
        self.rename_type_combo.blockSignals(False)

        self.rename_prefix_label.setText(self.translator.get("prefix"))
        self.rename_prefix_input.setPlaceholderText(self.translator.get("prefix_placeholder"))
        self.rename_suffix_label.setText(self.translator.get("suffix"))
        self.rename_suffix_input.setPlaceholderText(self.translator.get("suffix_placeholder"))
        self.rename_zero_padding_label.setText(self.translator.get("zero_padding"))
        self.rename_zero_num_spinbox.setToolTip(self.translator.get("zero_padding_tooltip"))
        self.rename_zero_padding_hint_label.setText(self.translator.get("zero_padding_hint"))
        self.rename_dry_run_checkbox.setText(self.translator.get("dry_run"))
        self.rename_log_group.setTitle(self.translator.get("rename_log"))
        self.rename_start_button.setText(self.translator.get("start_rename"))
        self.rename_stop_button.setText(self.translator.get("stop"))

        # Status bar
        self.statusBar().showMessage(self.translator.get("ready"))

    def create_video_resize_tab(self):
        """Create the video resize tab."""
        self.video_tab = QWidget()
        tab_layout = QVBoxLayout(self.video_tab)

        # Title
        self.video_title_label = QLabel(self.translator.get("video_title"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.video_title_label.setFont(title_font)
        self.video_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab_layout.addWidget(self.video_title_label)

        # Input group
        self.video_input_group = QGroupBox(self.translator.get("settings"))
        input_layout = QVBoxLayout()

        # Folder selection
        folder_layout = QHBoxLayout()
        self.video_folder_label = QLabel(self.translator.get("folder_with_videos"))
        folder_layout.addWidget(self.video_folder_label)
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText(self.translator.get("select_video_folder"))
        folder_layout.addWidget(self.folder_input)
        self.browse_button = QPushButton(self.translator.get("browse"))
        self.browse_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.browse_button)
        input_layout.addLayout(folder_layout)

        # Height setting
        height_layout = QHBoxLayout()
        self.video_height_label = QLabel(self.translator.get("target_height"))
        height_layout.addWidget(self.video_height_label)
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setMinimum(1)
        self.height_spinbox.setMaximum(8192)
        self.height_spinbox.setValue(720)
        self.height_spinbox.setSuffix(" px")
        height_layout.addWidget(self.height_spinbox)
        height_layout.addStretch()
        input_layout.addLayout(height_layout)

        # Options
        self.remove_audio_checkbox = QCheckBox(self.translator.get("remove_audio"))
        input_layout.addWidget(self.remove_audio_checkbox)

        self.create_thumbs_checkbox = QCheckBox(self.translator.get("create_thumbs"))
        input_layout.addWidget(self.create_thumbs_checkbox)

        self.video_input_group.setLayout(input_layout)
        tab_layout.addWidget(self.video_input_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        tab_layout.addWidget(self.progress_bar)

        # Log output
        self.video_log_group = QGroupBox(self.translator.get("processing_log"))
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        self.video_log_group.setLayout(log_layout)
        tab_layout.addWidget(self.video_log_group)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.start_button = QPushButton(self.translator.get("start_processing"))
        self.start_button.clicked.connect(self.start_processing)
        self.start_button.setMinimumWidth(150)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton(self.translator.get("stop"))
        self.stop_button.clicked.connect(self.stop_processing)
        self.stop_button.setEnabled(False)
        self.stop_button.setMinimumWidth(150)
        button_layout.addWidget(self.stop_button)

        button_layout.addStretch()
        tab_layout.addLayout(button_layout)

        # Add tab to tab widget
        self.tab_widget.addTab(self.video_tab, self.translator.get("tab_video_resize"))

    def create_file_download_tab(self):
        """Create the file download tab."""
        self.download_tab = QWidget()
        tab_layout = QVBoxLayout(self.download_tab)

        # Title
        self.download_title_label = QLabel(self.translator.get("download_title"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.download_title_label.setFont(title_font)
        self.download_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab_layout.addWidget(self.download_title_label)

        # Input group
        self.download_input_group = QGroupBox(self.translator.get("settings"))
        input_layout = QVBoxLayout()

        # Input file selection
        input_file_layout = QHBoxLayout()
        self.download_url_file_label = QLabel(self.translator.get("url_file"))
        input_file_layout.addWidget(self.download_url_file_label)
        self.download_file_input = QLineEdit()
        self.download_file_input.setPlaceholderText(self.translator.get("select_url_file"))
        input_file_layout.addWidget(self.download_file_input)
        self.download_browse_file_button = QPushButton(self.translator.get("browse"))
        self.download_browse_file_button.clicked.connect(self.browse_download_file)
        input_file_layout.addWidget(self.download_browse_file_button)
        input_layout.addLayout(input_file_layout)

        # Output folder selection
        output_folder_layout = QHBoxLayout()
        self.download_folder_label = QLabel(self.translator.get("download_folder"))
        output_folder_layout.addWidget(self.download_folder_label)
        self.download_folder_input = QLineEdit()
        self.download_folder_input.setPlaceholderText(self.translator.get("select_download_folder"))
        output_folder_layout.addWidget(self.download_folder_input)
        self.download_browse_folder_button = QPushButton(self.translator.get("browse"))
        self.download_browse_folder_button.clicked.connect(self.browse_download_folder)
        output_folder_layout.addWidget(self.download_browse_folder_button)
        input_layout.addLayout(output_folder_layout)

        # Column index for custom filename
        column_index_layout = QHBoxLayout()
        self.download_column_index_label = QLabel(self.translator.get("column_index_name"))
        column_index_layout.addWidget(self.download_column_index_label)
        self.download_column_index_spinbox = QSpinBox()
        self.download_column_index_spinbox.setMinimum(-1)
        self.download_column_index_spinbox.setMaximum(100)
        self.download_column_index_spinbox.setValue(-1)
        self.download_column_index_spinbox.setSpecialValueText(self.translator.get("not_used"))
        self.download_column_index_spinbox.setToolTip(self.translator.get("column_index_name_tooltip"))
        column_index_layout.addWidget(self.download_column_index_spinbox)
        self.download_column_index_hint_label = QLabel(self.translator.get("column_index_name_hint"))
        column_index_layout.addWidget(self.download_column_index_hint_label)
        column_index_layout.addStretch()
        input_layout.addLayout(column_index_layout)

        self.download_input_group.setLayout(input_layout)
        tab_layout.addWidget(self.download_input_group)

        # Progress bar
        self.download_progress_bar = QProgressBar()
        self.download_progress_bar.setValue(0)
        tab_layout.addWidget(self.download_progress_bar)

        # Log output
        self.download_log_group = QGroupBox(self.translator.get("download_log"))
        log_layout = QVBoxLayout()
        self.download_log_text = QTextEdit()
        self.download_log_text.setReadOnly(True)
        self.download_log_text.setMaximumHeight(200)
        log_layout.addWidget(self.download_log_text)
        self.download_log_group.setLayout(log_layout)
        tab_layout.addWidget(self.download_log_group)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.download_start_button = QPushButton(self.translator.get("start_download"))
        self.download_start_button.clicked.connect(self.start_downloading)
        self.download_start_button.setMinimumWidth(150)
        button_layout.addWidget(self.download_start_button)

        self.download_stop_button = QPushButton(self.translator.get("stop"))
        self.download_stop_button.clicked.connect(self.stop_downloading)
        self.download_stop_button.setEnabled(False)
        self.download_stop_button.setMinimumWidth(150)
        button_layout.addWidget(self.download_stop_button)

        button_layout.addStretch()
        tab_layout.addLayout(button_layout)

        # Add tab to tab widget
        self.tab_widget.addTab(self.download_tab, self.translator.get("tab_file_download"))

    def create_file_rename_tab(self):
        """Create the file rename tab."""
        self.rename_tab = QWidget()
        tab_layout = QVBoxLayout(self.rename_tab)

        # Title
        self.rename_title_label = QLabel(self.translator.get("rename_title"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.rename_title_label.setFont(title_font)
        self.rename_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab_layout.addWidget(self.rename_title_label)

        # Input group
        self.rename_input_group = QGroupBox(self.translator.get("settings"))
        input_layout = QVBoxLayout()

        # Folder selection
        folder_layout = QHBoxLayout()
        self.rename_folder_label = QLabel(self.translator.get("folder_with_files"))
        folder_layout.addWidget(self.rename_folder_label)
        self.rename_folder_input = QLineEdit()
        self.rename_folder_input.setPlaceholderText(self.translator.get("select_files_folder"))
        folder_layout.addWidget(self.rename_folder_input)
        self.rename_browse_button = QPushButton(self.translator.get("browse"))
        self.rename_browse_button.clicked.connect(self.browse_rename_folder)
        folder_layout.addWidget(self.rename_browse_button)
        input_layout.addLayout(folder_layout)

        # Sort type selection
        sort_layout = QHBoxLayout()
        self.rename_sort_label = QLabel(self.translator.get("sort"))
        sort_layout.addWidget(self.rename_sort_label)

        self.rename_sort_combo = QComboBox()
        self.rename_sort_combo.addItem(self.translator.get("sort_name"), "name")
        self.rename_sort_combo.addItem(self.translator.get("sort_number"), "number")
        sort_layout.addWidget(self.rename_sort_combo)
        sort_layout.addStretch()
        input_layout.addLayout(sort_layout)

        # Rename type selection
        rename_type_layout = QHBoxLayout()
        self.rename_type_label = QLabel(self.translator.get("rename_type"))
        rename_type_layout.addWidget(self.rename_type_label)
        self.rename_type_combo = QComboBox()
        self.rename_type_combo.addItem(self.translator.get("rename_sequential"), "sequential")
        self.rename_type_combo.addItem(self.translator.get("rename_numbers_only"), "numbers_only")
        self.rename_type_combo.addItem(self.translator.get("rename_text_only"), "text_only")
        self.rename_type_combo.addItem(self.translator.get("rename_numbers_only_at_end"), "numbers_only_at_end")
        rename_type_layout.addWidget(self.rename_type_combo)
        rename_type_layout.addStretch()
        input_layout.addLayout(rename_type_layout)

        # Prefix input
        prefix_layout = QHBoxLayout()
        self.rename_prefix_label = QLabel(self.translator.get("prefix"))
        prefix_layout.addWidget(self.rename_prefix_label)
        self.rename_prefix_input = QLineEdit()
        self.rename_prefix_input.setPlaceholderText(self.translator.get("prefix_placeholder"))
        prefix_layout.addWidget(self.rename_prefix_input)
        prefix_layout.addStretch()
        input_layout.addLayout(prefix_layout)

        # Suffix input
        suffix_layout = QHBoxLayout()
        self.rename_suffix_label = QLabel(self.translator.get("suffix"))
        suffix_layout.addWidget(self.rename_suffix_label)
        self.rename_suffix_input = QLineEdit()
        self.rename_suffix_input.setPlaceholderText(self.translator.get("suffix_placeholder"))
        suffix_layout.addWidget(self.rename_suffix_input)
        suffix_layout.addStretch()
        input_layout.addLayout(suffix_layout)

        # Zero padding input
        zero_num_layout = QHBoxLayout()
        self.rename_zero_padding_label = QLabel(self.translator.get("zero_padding"))
        zero_num_layout.addWidget(self.rename_zero_padding_label)
        self.rename_zero_num_spinbox = QSpinBox()
        self.rename_zero_num_spinbox.setMinimum(0)
        self.rename_zero_num_spinbox.setMaximum(10)
        self.rename_zero_num_spinbox.setValue(0)
        self.rename_zero_num_spinbox.setToolTip(self.translator.get("zero_padding_tooltip"))
        zero_num_layout.addWidget(self.rename_zero_num_spinbox)
        self.rename_zero_padding_hint_label = QLabel(self.translator.get("zero_padding_hint"))
        zero_num_layout.addWidget(self.rename_zero_padding_hint_label)
        zero_num_layout.addStretch()
        input_layout.addLayout(zero_num_layout)

        # Dry run checkbox
        self.rename_dry_run_checkbox = QCheckBox(self.translator.get("dry_run"))
        self.rename_dry_run_checkbox.setChecked(True)  # Enable by default for safety
        input_layout.addWidget(self.rename_dry_run_checkbox)

        self.rename_input_group.setLayout(input_layout)
        tab_layout.addWidget(self.rename_input_group)

        # Progress bar
        self.rename_progress_bar = QProgressBar()
        self.rename_progress_bar.setValue(0)
        tab_layout.addWidget(self.rename_progress_bar)

        # Log output
        self.rename_log_group = QGroupBox(self.translator.get("rename_log"))
        log_layout = QVBoxLayout()
        self.rename_log_text = QTextEdit()
        self.rename_log_text.setReadOnly(True)
        self.rename_log_text.setMaximumHeight(200)
        log_layout.addWidget(self.rename_log_text)
        self.rename_log_group.setLayout(log_layout)
        tab_layout.addWidget(self.rename_log_group)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.rename_start_button = QPushButton(self.translator.get("start_rename"))
        self.rename_start_button.clicked.connect(self.start_renaming)
        self.rename_start_button.setMinimumWidth(150)
        button_layout.addWidget(self.rename_start_button)

        self.rename_stop_button = QPushButton(self.translator.get("stop"))
        self.rename_stop_button.clicked.connect(self.stop_renaming)
        self.rename_stop_button.setEnabled(False)
        self.rename_stop_button.setMinimumWidth(150)
        button_layout.addWidget(self.rename_stop_button)

        button_layout.addStretch()
        tab_layout.addLayout(button_layout)

        # Add tab to tab widget
        self.tab_widget.addTab(self.rename_tab, self.translator.get("tab_file_rename"))

    def browse_folder(self):
        """Open folder browser dialog."""
        folder = QFileDialog.getExistingDirectory(
            self,
            self.translator.get("select_video_folder_dialog"),
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.folder_input.setText(folder)

    def browse_download_file(self):
        """Open file browser dialog for input file."""
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.translator.get("select_url_file_dialog"),
            "",
            "Spreadsheet Files (*.xls *.xlsx *.csv);;All Files (*)"
        )
        if file:
            self.download_file_input.setText(file)

    def browse_download_folder(self):
        """Open folder browser dialog for download folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            self.translator.get("select_download_folder_dialog"),
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
                self.translator.get("error"),
                self.translator.get("please_select_folder")
            )
            return

        folder_path = Path(folder_path)
        if not folder_path.exists() or not folder_path.is_dir():
            QMessageBox.warning(
                self,
                self.translator.get("error"),
                self.translator.get("folder_not_exists", folder_path)
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
            create_thumbs,
            self.translator
        )
        self.processor_thread.progress.connect(self.update_progress)
        self.processor_thread.log.connect(self.add_log)
        self.processor_thread.finished.connect(self.processing_finished)
        self.processor_thread.start()

        self.statusBar().showMessage(self.translator.get("processing"))

    def stop_processing(self):
        """Stop video processing."""
        if self.processor_thread and self.processor_thread.isRunning():
            self.processor_thread.stop()
            self.add_log(self.translator.get("stopping_processing"))
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
        self.add_log(self.translator.get("processing_complete_summary"))
        self.add_log(self.translator.get("successful", stats['successful']))
        self.add_log(self.translator.get("errors", stats['failed']))
        self.add_log(self.translator.get("total", stats['total']))

        if self.create_thumbs_checkbox.isChecked():
            self.add_log(self.translator.get("thumbs_created", stats['thumbs_created']))
            self.add_log(self.translator.get("thumbs_errors", stats['thumbs_failed']))

        self.add_log("=" * 50)

        self.statusBar().showMessage(self.translator.get("ready"))

        # Show completion message
        if stats['total'] > 0:
            QMessageBox.information(
                self,
                self.translator.get("processing_complete"),
                self.translator.get("processing_complete_msg", stats['successful'], stats['total'])
            )

    def start_downloading(self):
        """Start file downloading."""
        # Validate input
        file_path = self.download_file_input.text().strip()
        if not file_path:
            QMessageBox.warning(
                self,
                self.translator.get("error"),
                self.translator.get("please_select_url_file")
            )
            return

        file_path = Path(file_path)
        if not file_path.exists() or not file_path.is_file():
            QMessageBox.warning(
                self,
                self.translator.get("error"),
                self.translator.get("file_not_exists", file_path)
            )
            return

        # Check file extension
        if file_path.suffix.lower() not in ['.csv', '.xlsx', '.xls']:
            QMessageBox.warning(
                self,
                self.translator.get("error"),
                self.translator.get("unsupported_format")
            )
            return

        # Validate output folder
        output_folder = self.download_folder_input.text().strip()
        if not output_folder:
            QMessageBox.warning(
                self,
                self.translator.get("error"),
                self.translator.get("please_select_download_folder")
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

        # Get column index for custom filename
        column_index_name = self.download_column_index_spinbox.value()
        if column_index_name == -1:
            column_index_name = None

        # Start downloading thread
        self.downloader_thread = FileDownloaderThread(file_path, output_folder, column_index_name, self.translator)
        self.downloader_thread.progress.connect(self.update_download_progress)
        self.downloader_thread.log.connect(self.add_download_log)
        self.downloader_thread.finished.connect(self.downloading_finished)
        self.downloader_thread.start()

        self.statusBar().showMessage(self.translator.get("downloading"))

    def stop_downloading(self):
        """Stop file downloading."""
        if self.downloader_thread and self.downloader_thread.isRunning():
            self.downloader_thread.stop()
            self.add_download_log(self.translator.get("stopping_download"))
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
        self.add_download_log(self.translator.get("download_complete_summary"))
        self.add_download_log(self.translator.get("successful", stats['successful']))
        self.add_download_log(self.translator.get("errors", stats['failed']))
        self.add_download_log(self.translator.get("skipped", stats['skipped']))
        if stats.get('renamed', 0) > 0:
            self.add_download_log(self.translator.get("renamed", stats['renamed']))
        self.add_download_log(self.translator.get("total_urls", stats['total']))
        self.add_download_log("=" * 50)

        self.statusBar().showMessage(self.translator.get("ready"))

        # Show completion message
        if stats['total'] > 0:
            QMessageBox.information(
                self,
                self.translator.get("download_complete"),
                self.translator.get("download_complete_msg", stats['successful'], stats['total'])
            )

    def browse_rename_folder(self):
        """Open folder browser dialog for rename folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            self.translator.get("select_files_folder_dialog"),
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
                self.translator.get("error"),
                self.translator.get("please_select_files_folder")
            )
            return

        folder_path = Path(folder_path)
        if not folder_path.exists() or not folder_path.is_dir():
            QMessageBox.warning(
                self,
                self.translator.get("error"),
                self.translator.get("folder_not_exists", folder_path)
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
            zero_num,
            self.translator
        )
        self.renamer_thread.progress.connect(self.update_rename_progress)
        self.renamer_thread.log.connect(self.add_rename_log)
        self.renamer_thread.finished.connect(self.renaming_finished)
        self.renamer_thread.start()

        self.statusBar().showMessage(self.translator.get("renaming"))

    def stop_renaming(self):
        """Stop file renaming."""
        if self.renamer_thread and self.renamer_thread.isRunning():
            self.renamer_thread.stop()
            self.add_rename_log(self.translator.get("stopping_rename"))
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
            self.add_rename_log(self.translator.get("preview_complete"))
        else:
            self.add_rename_log(self.translator.get("rename_complete_summary"))
        self.add_rename_log(self.translator.get("successful", stats['successful']))
        self.add_rename_log(self.translator.get("errors", stats['failed']))
        self.add_rename_log(self.translator.get("total", stats['total']))
        self.add_rename_log("=" * 50)

        self.statusBar().showMessage(self.translator.get("ready"))

        # Show completion message
        if stats['total'] > 0:
            if self.rename_dry_run_checkbox.isChecked():
                QMessageBox.information(
                    self,
                    self.translator.get("rename_preview_complete"),
                    self.translator.get("rename_preview_msg", stats['successful'], stats['total'])
                )
            else:
                QMessageBox.information(
                    self,
                    self.translator.get("rename_complete"),
                    self.translator.get("rename_complete_msg", stats['successful'], stats['total'])
                )


def main():
    """Main entry point for GUI application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
