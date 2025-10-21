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
    """A QLabel that accepts a single image drop."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Drag image here")
        self.setStyleSheet("""
            border: 1px dashed gray;
            min-width: 120px;
            min-height: 120px;
            background-color: #d3d3d3;   /* light grey background */
            color: #555555;               /* darker grey text */
            font-weight: bold;
        """)
        self.setAcceptDrops(True)
        self.pixmap_path = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isfile(path):
                pixmap = QPixmap(path).scaled(
                    self.width(), self.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.setPixmap(pixmap)
                self.setText("")  # remove placeholder text
                self.pixmap_path = path
        event.acceptProposedAction()



class CustomImageGrid(QWidget):
    """Grid of DroppableLabels with adjustable rows and columns, with clear/reset option."""
    images_dropped = pyqtSignal(list)  # emits all image paths

    def __init__(self, default_columns=4, default_rows=3, max_width=200):
        super().__init__()
        self.max_width = max_width
        self.labels = []
        self.images = []

        # --- Main layout ---
        self.layout = QVBoxLayout(self)

        # --- Controls for rows, columns, and clear ---
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

        # --- Grid container ---
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)
        self.layout.addWidget(self.grid_widget)

        self.build_grid()

    def build_grid(self):
        """Rebuild grid based on current rows, columns, and current images."""
        for lbl in self.labels:
            self.grid_layout.removeWidget(lbl)
            lbl.deleteLater()
        self.labels.clear()

        cols = self.cols_spin.value()
        rows = self.rows_spin.value()
        total_cells = cols * rows
        total_images = len(self.images)
        required_rows = max(rows, (total_images + cols - 1) // cols)

        idx = 0
        for r in range(required_rows):
            for c in range(cols):
                lbl = DroppableLabel()
                if idx < total_images:
                    lbl.pixmap_path = self.images[idx]
                    pixmap = QPixmap(self.images[idx]).scaled(
                        self.max_width, self.max_width,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    lbl.setPixmap(pixmap)
                lbl.setAcceptDrops(True)
                lbl.dropEvent = self.make_drop_event(lbl)
                self.grid_layout.addWidget(lbl, r, c)
                self.labels.append(lbl)
                idx += 1

    def make_drop_event(self, lbl):
        """Return a custom dropEvent for this label to track dropped image."""
        def dropEvent(event):
            urls = event.mimeData().urls()
            if urls:
                path = urls[0].toLocalFile()
                if os.path.isfile(path):
                    pixmap = QPixmap(path).scaled(
                        self.max_width, self.max_width,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    lbl.setPixmap(pixmap)
                    lbl.pixmap_path = path
                    if path not in self.images:
                        self.images.append(path)
                    self.images_dropped.emit(self.images)
            event.acceptProposedAction()
        return dropEvent

    def clear_grid(self):
        """Reset all images and restore placeholders."""
        self.images.clear()
        for lbl in self.labels:
            lbl.clear()
            lbl.pixmap_path = None
            lbl.setText("Drag image here")
            lbl.setStyleSheet("""
                border: 1px dashed gray;
                min-width: 120px;
                min-height: 120px;
                background-color: #d3d3d3;   /* light grey background */
                color: #555555;               /* darker grey text */
                font-weight: bold;
            """)
        self.images_dropped.emit([])

    def get_images(self):
        """Return current image paths."""
        return [lbl.pixmap_path for lbl in self.labels if lbl.pixmap_path]
