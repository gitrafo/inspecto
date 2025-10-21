# custom_tab.py
import os
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PIL import Image

class CustomImageGrid(QWidget):
    images_dropped = pyqtSignal(list)  # emits list of file paths

    def __init__(self, max_columns=4, img_width=350):
        super().__init__()

        self.max_columns = max_columns
        self.img_width = img_width
        self.images = []

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Optional placeholder text
        self.placeholder_label = QLabel("Drag images here")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("""
            color: gray;
            font-size: 18px;
            border: 2px dashed #555;
            padding: 50px;
        """)
        self.layout.addWidget(self.placeholder_label, 0, 0, 1, self.max_columns)

    def add_images(self, image_paths):
        """Add images to the grid."""
        # Remove placeholder if present
        if self.placeholder_label and self.placeholder_label.parent():
            self.placeholder_label.setParent(None)
            self.placeholder_label = None

        start_index = len(self.images)
        self.images.extend(image_paths)
        self.update_grid(start_index)

    def update_grid(self, start_index=0):
        """Rebuilds grid from start_index to end."""
        col_count = self.max_columns

        for idx in range(start_index, len(self.images)):
            path = self.images[idx]
            pixmap = self.load_pixmap(path)

            # --- Container with border ---
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(5, 5, 5, 5)
            container_layout.setSpacing(5)
            container_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
            container.setStyleSheet("border: 2px solid #555; border-radius: 5px;")
            container.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

            # --- Image label ---
            img_label = QLabel()
            img_label.setPixmap(pixmap)
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img_label.setFixedWidth(self.img_width)
            img_label.setFixedHeight(int(self.img_width * 9 / 16))
            img_label.setStyleSheet("background-color: #222;")
            container_layout.addWidget(img_label, alignment=Qt.AlignmentFlag.AlignHCenter)

            # --- Sample label (filename) ---
            sample_label = QLabel(os.path.basename(path))
            sample_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sample_label.setStyleSheet("color: white; font-size: 14px;")
            container_layout.addWidget(sample_label, alignment=Qt.AlignmentFlag.AlignHCenter)

            row = idx // col_count
            col = idx % col_count
            self.layout.addWidget(container, row, col)

    def load_pixmap(self, path):
        """Load image as QPixmap and scale to width while keeping aspect ratio."""
        try:
            img = Image.open(path)
            img_ratio = img.width / img.height
            target_height = int(self.img_width / img_ratio)
            img = img.resize((self.img_width, target_height), Image.LANCZOS)
            pixmap = QPixmap(path).scaled(
                self.img_width,
                int(self.img_width * 9 / 16),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            return pixmap
        except Exception as e:
            print(f"Error loading {path}: {e}")
            # Return empty placeholder pixmap
            placeholder = QPixmap(self.img_width, int(self.img_width*9/16))
            placeholder.fill(Qt.GlobalColor.darkGray)
            return placeholder

    # --- Drag & Drop support ---
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        paths = [url.toLocalFile() for url in urls if url.isLocalFile()]
        if paths:
            self.add_images(paths)
            self.images_dropped.emit(paths)
