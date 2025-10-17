# custom_tab.py
import os
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PIL import Image
from io import BytesIO

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class CustomImageGrid(QWidget):
    images_dropped = pyqtSignal(list)

    def __init__(self, default_columns=4, default_rows=2, default_cell_height=200, max_width=350):
        super().__init__()

        # Grid parameters
        self.default_columns = default_columns
        self.default_rows = default_rows
        self.default_cell_height = default_cell_height
        self.default_cell_width = max_width

        self.image_paths = []

        self.grid_layout = QGridLayout(self)
        self.grid_layout.setContentsMargins(5,5,5,5)
        self.grid_layout.setSpacing(10)
        self.setLayout(self.grid_layout)

        self.setAcceptDrops(True)
        self.build_grid()

    # --- Update grid settings dynamically ---
    def set_max_width(self, w):
        self.default_cell_width = w
        self.build_grid()

    def set_columns(self, n):
        self.default_columns = max(1, n)
        self.build_grid()

    def set_rows(self, n):
        self.default_rows = max(1, n)
        self.build_grid()

    def update_grid(self):
        """Rebuild grid with current parameters."""
        self.build_grid()

    # --- Grid building ---
    def build_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        total_cells = max(len(self.image_paths), self.default_columns * self.default_rows)
        row = 0
        col = 0
        for idx in range(total_cells):
            if idx < len(self.image_paths):
                path = self.image_paths[idx]
                pixmap = self.load_pixmap(path)
                label = ClickableLabel()
                if pixmap:
                    label.setPixmap(pixmap)
                    label.setFixedWidth(pixmap.width())
                    label.setFixedHeight(pixmap.height())
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.clicked.connect(lambda checked=False, p=path: self.open_external_viewer(p))
                else:
                    label.setText("Invalid image")
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setFixedSize(self.default_cell_width, self.default_cell_height)
            else:
                label = QLabel("Drop here")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setFixedSize(self.default_cell_width, self.default_cell_height)
                label.setStyleSheet("border: 2px dashed gray;")

            label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            self.grid_layout.addWidget(label, row, col)

            col += 1
            if col >= self.default_columns:
                col = 0
                row += 1

    # --- Image handling ---
    def load_pixmap(self, path):
        try:
            img = Image.open(path)
            wpercent = (self.default_cell_width / float(img.size[0]))
            height = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((self.default_cell_width, height), Image.LANCZOS)
            bio = BytesIO()
            img.save(bio, format='PNG')
            bio.seek(0)
            pixmap = QPixmap()
            pixmap.loadFromData(bio.read())
            return pixmap
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return None

    def open_external_viewer(self, filepath):
        import sys, os, subprocess
        if not filepath or not os.path.isfile(filepath):
            return
        try:
            normalized_path = os.path.normpath(filepath)
            if sys.platform.startswith('win'):
                os.startfile(normalized_path)
            elif sys.platform.startswith('darwin'):
                subprocess.run(['open', normalized_path])
            else:
                subprocess.run(['xdg-open', normalized_path])
        except Exception as e:
            print(f"Unable to open file: {e}")

    # --- Drag & drop ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                paths.append(url.toLocalFile())
        self.image_paths.extend(paths)
        self.build_grid()
        self.images_dropped.emit(paths)
