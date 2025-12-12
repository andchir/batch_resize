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
    QTextEdit, QProgressBar, QGroupBox, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont

from main import get_video_files, resize_video, create_thumbnail


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


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.processor_thread: Optional[VideoProcessorThread] = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Batch Video Resize")
        self.setMinimumSize(800, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("Пакетное изменение размера видео")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

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
        main_layout.addWidget(input_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # Log output
        log_group = QGroupBox("Журнал обработки")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

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
        main_layout.addLayout(button_layout)

        # Status bar
        self.statusBar().showMessage("Готов к работе")

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


def main():
    """Main entry point for GUI application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
