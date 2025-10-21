from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QSize, pyqtSignal
import os


class CustomImageGrid(QWidget):
    images_dropped = pyqtSignal(list)  # emitted when one or more images are dropped

    def __init__(self):
        super().__init__()

        self.images = []  # store paths of loaded images

        # --- Controls ---
        controls = QHBoxLayout()
        controls.setAlignment(Qt.AlignmentFlag.AlignLeft)

        controls.addWidget(QLabel("Rows:"))
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 10)
        self.rows_spin.setValue(3)
        controls.addWidget(self.rows_spin)

        controls.addWidget(QLabel("Cols:"))
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 10)
        self.cols_spin.setValue(4)
        controls.addWidget(self.cols_spin)

        # --- Grid Layout ---
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.grid_layout.setSpacing(5)

        # --- Main Layout ---
        main_layout = QVBoxLayout()
        main_layout.addLayout(controls)
        main_layout.addLayout(self.grid_layout)
        main_layout.addStretch(1)
        self.setLayout(main_layout)

        # --- Connect ---
        self.rows_spin.valueChanged.connect(self.update_grid)
        self.cols_spin.valueChanged.connect(self.update_grid)

        # --- Initialize grid ---
        self.update_grid()

    def update_grid(self):
        """Rebuild grid with current images or placeholders."""
        # clear layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        rows = self.rows_spin.value()
        cols = self.cols_spin.value()

        total_slots = rows * cols
        for idx in range(total_slots):
            if idx < len(self.images):
                # already loaded image
                path = self.images[idx]
                placeholder = ImagePlaceholder()
                placeholder.load_image(path)
                placeholder.image_loaded.connect(self.on_image_loaded)
            else:
                # empty placeholder
                placeholder = ImagePlaceholder()
                placeholder.setText("Drop image")
                placeholder.image_loaded.connect(self.on_image_loaded)
            r = idx // cols
            c = idx % cols
            self.grid_layout.addWidget(placeholder, r, c)

        self.adjust_grid()

    def on_image_loaded(self, path):
        """Triggered when an image is dropped."""
        if path and path not in self.images:
            self.images.append(path)
            self.images_dropped.emit([path])
            self.update_grid()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_grid()

    def adjust_grid(self):
        """Resize placeholders to fill area nicely without stretching."""
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        if rows == 0 or cols == 0:
            return

        total_width = self.width() - self.grid_layout.contentsMargins().left() - self.grid_layout.contentsMargins().right()
        total_height = self.height() - self.grid_layout.contentsMargins().top() - self.grid_layout.contentsMargins().bottom() - 50

        spacing_x = self.grid_layout.spacing() * (cols - 1)
        spacing_y = self.grid_layout.spacing() * (rows - 1)

        available_width = max(1, total_width - spacing_x)
        available_height = max(1, total_height - spacing_y)

        box_w = max(120, available_width // cols)
        box_h = max(90, available_height // rows)

        # Store last size to prevent recursive resize
        if hasattr(self, "_last_box_size") and self._last_box_size == (box_w, box_h):
            return
        self._last_box_size = (box_w, box_h)

        size = QSize(box_w, box_h)

        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setMaximumSize(size)
                widget.setMinimumSize(size)



# -----------------------------------------------------------------------------
# Image placeholder that accepts drag & drop
# -----------------------------------------------------------------------------
from PyQt6.QtWidgets import QLabel


class ImagePlaceholder(QLabel):
    image_loaded = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QLabel {
                background-color: #666;
                color: white;
                border: 1px dashed #999;
                border-radius: 8px;
            }
            QLabel:hover {
                background-color: #777;
            }
        """)

        self.image_path = None

    def setText(self, text):
        super().setText(text)

    # --- Drag and drop events ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        if os.path.isfile(path) and path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
            self.load_image(path)
            self.image_loaded.emit(path)

    def load_image(self, path):
        """Display dropped image (scaled to fit)."""
        self.image_path = path
        img = QImage(path)
        if img.isNull():
            self.setText("Invalid image")
            return
        pixmap = QPixmap.fromImage(img)
        scaled = pixmap.scaled(
            self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)
        self.setStyleSheet("background-color: #000; border: 1px solid #333;")

    def resizeEvent(self, event):
        """Ensure image scales smoothly when resizing window."""
        super().resizeEvent(event)
        if self.image_path:
            self.load_image(self.image_path)
