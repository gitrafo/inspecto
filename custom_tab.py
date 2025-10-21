# custom_tab.py
import os
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QLabel, QSizePolicy, QVBoxLayout,
    QHBoxLayout, QSpinBox, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class DroppableLabel(QLabel):
    """A QLabel that scales its image to fill the current label size."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Drag image here")
        self.setStyleSheet("""
            border: 1px dashed gray;
            min-width: 80px;
            min-height: 80px;
            background-color: #d3d3d3;
            color: #555555;
            font-weight: bold;
        """)
        self.setAcceptDrops(True)
        self.pixmap_path = None
        self.original_pixmap = None  # store original pixmap for rescaling

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isfile(path):
                pixmap = QPixmap(path)
                self.set_pixmap(pixmap)
                self.pixmap_path = path
        event.acceptProposedAction()

    def set_pixmap(self, pixmap: QPixmap):
        """Store original pixmap and scale it to current label size."""
        self.original_pixmap = pixmap
        self.rescale_pixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.rescale_pixmap()

    def rescale_pixmap(self):
        if self.original_pixmap:
            scaled = self.original_pixmap.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled)
            self.setText("")  # hide placeholder if pixmap exists
        else:
            self.setText("Drag image here")



class CustomImageGrid(QWidget):
    """Grid of DroppableLabels with adjustable rows and columns, images keep max width."""
    images_dropped = pyqtSignal(list)

    def __init__(self, default_columns=4, default_rows=3, max_width=200):
        super().__init__()
        self.max_width = max_width
        self.labels = []
        self.images = []

        self.layout = QVBoxLayout(self)

        # Controls
        self.control_layout = QHBoxLayout()
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 10)
        self.cols_spin.setValue(default_columns)
        self.cols_spin.valueChanged.connect(self.build_grid)

        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 10)
        self.rows_spin.setValue(default_rows)
        self.rows_spin.valueChanged.connect(self.build_grid)

        self.clear_button = QPushButton("Clear Grid")
        self.clear_button.clicked.connect(self.clear_grid)

        self.control_layout.addWidget(QLabel("Columns:"))
        self.control_layout.addWidget(self.cols_spin)
        self.control_layout.addWidget(QLabel("Rows:"))
        self.control_layout.addWidget(self.rows_spin)
        self.control_layout.addStretch()
        self.control_layout.addWidget(self.clear_button)
        self.layout.addLayout(self.control_layout)

        # Grid container
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)
        self.layout.addWidget(self.grid_widget)

        self.build_grid()

    def build_grid(self):
        """Rebuild grid based on current rows, columns, preserving existing images."""
        # save current images
        existing_images = [lbl.pixmap_path for lbl in self.labels if lbl.pixmap_path]

        # clear old labels
        for lbl in self.labels:
            self.grid_layout.removeWidget(lbl)
            lbl.deleteLater()
        self.labels.clear()

        cols = self.cols_spin.value()
        rows = self.rows_spin.value()
        total_images = len(existing_images)
        required_rows = max(rows, (total_images + cols - 1) // cols)

        idx = 0
        for r in range(required_rows):
            for c in range(cols):
                lbl = DroppableLabel()
                lbl.setAcceptDrops(True)
                lbl.dropEvent = self.make_drop_event(lbl)

                # restore existing image if available
                if idx < total_images:
                    path = existing_images[idx]
                    pixmap = QPixmap(path)
                    lbl.set_pixmap(pixmap)  # ✅ store original pixmap for rescaling
                    lbl.pixmap_path = path
                else:
                    lbl.setText("Drag image here")
                    lbl.pixmap_path = None

                self.grid_layout.addWidget(lbl, r, c)
                self.labels.append(lbl)
                idx += 1

        # update internal images list
        self.images = [lbl.pixmap_path for lbl in self.labels if lbl.pixmap_path]
        self.images_dropped.emit(self.images)

    def make_drop_event(self, lbl):
        def dropEvent(event):
            urls = event.mimeData().urls()
            if urls:
                path = urls[0].toLocalFile()
                if os.path.isfile(path):
                    pixmap = QPixmap(path)
                    
                    # Resize the label to max_width while keeping aspect ratio
                    w, h = pixmap.width(), pixmap.height()
                    max_w = self.max_width
                    scale_factor = min(max_w / w, 1.0)  # never upscale
                    lbl.setFixedSize(int(w * scale_factor), int(h * scale_factor))
                    
                    lbl.set_pixmap(pixmap)  # store original and rescale
                    lbl.pixmap_path = path

                    if path not in self.images:
                        self.images.append(path)
                    self.images_dropped.emit(self.images)
            event.acceptProposedAction()
        return dropEvent

    def clear_grid(self):
        self.images.clear()
        for lbl in self.labels:
            lbl.clear()
            lbl.pixmap_path = None
            lbl.setText("Drag image here")
        self.images_dropped.emit([])

    def get_images(self):
        return [lbl.pixmap_path for lbl in self.labels if lbl.pixmap_path]



    