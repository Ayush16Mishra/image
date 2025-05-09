# image_viewer.py

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QPixmap, QPen, QFont,QImage
from PyQt5.QtCore import Qt, QRectF
import os,json

class ImageViewer(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.image_item = None
        self.rect_items = []
        self.coord_labels_map = {}  # Map rect -> coord labels
        self.start_pos = None
        self.drawing_enabled = False
        self.erase_enabled = False
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setFocusPolicy(Qt.StrongFocus)

    def toggle_erase_mode(self, enabled):
        self.erase_enabled = enabled
        if enabled:
            self.enable_drawing(False)  # ⬅️ Disable drawing when erasing
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            self.setDragMode(QGraphicsView.ScrollHandDrag)


    def load_image(self, file_path):
        pixmap = QPixmap(file_path)
        self.scene.clear()
        self.image_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.image_item)
        self.rect_items.clear()
        self.coord_labels_map.clear()
        self.fitInView(self.image_item, Qt.KeepAspectRatio)

    def enable_drawing(self, enabled):
        self.drawing_enabled = enabled
        if enabled:
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    def wheelEvent(self, event):
        if not self.drawing_enabled:
            zoom = 1.25 if event.angleDelta().y() > 0 else 0.8
            self.scale(zoom, zoom)

    def keyPressEvent(self, event):
        if not self.drawing_enabled:
            if event.key() in (Qt.Key_Plus, Qt.Key_Equal):
                self.scale(1.25, 1.25)
            elif event.key() == Qt.Key_Minus:
                self.scale(0.8, 0.8)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
       pos = self.mapToScene(event.pos())

       if self.erase_enabled and event.button() == Qt.LeftButton:
        for rect in self.rect_items:
            if rect.rect().contains(pos):
                self.erase_box(rect)
                self.toggle_erase_mode(False)  # ⬅️ Turn it off right after one erase
                return

       elif self.drawing_enabled and event.button() == Qt.LeftButton:
             self.start_pos = pos
             rect_item = QGraphicsRectItem(QRectF(self.start_pos, self.start_pos))
             rect_item.setPen(QPen(Qt.red, 2))
             self.scene.addItem(rect_item)
             self.rect_items.append(rect_item)

       super().mousePressEvent(event)


    def mouseMoveEvent(self, event):
        if self.drawing_enabled and self.start_pos:
            current_pos = self.mapToScene(event.pos())
            rect = QRectF(self.start_pos, current_pos).normalized()
            self.rect_items[-1].setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drawing_enabled and self.rect_items:
            rect = self.rect_items[-1].rect()
            font = QFont("Arial", 10)

            top_left_label = QGraphicsTextItem(f"({rect.left():.0f}, {rect.top():.0f})")
            top_left_label.setFont(font)
            top_left_label.setDefaultTextColor(Qt.red)
            top_left_label.setPos(rect.left() - 50, rect.top())

            bottom_right_label = QGraphicsTextItem(f"({rect.right():.0f}, {rect.bottom():.0f})")
            bottom_right_label.setFont(font)
            bottom_right_label.setDefaultTextColor(Qt.red)
            bottom_right_label.setPos(rect.right(), rect.bottom())

            self.scene.addItem(top_left_label)
            self.scene.addItem(bottom_right_label)
            self.coord_labels_map[self.rect_items[-1]] = [top_left_label, bottom_right_label]

        self.start_pos = None
        super().mouseReleaseEvent(event)

    def erase_box(self, rect):
        self.scene.removeItem(rect)
        self.rect_items.remove(rect)
        if rect in self.coord_labels_map:
            for label in self.coord_labels_map[rect]:
                self.scene.removeItem(label)
            del self.coord_labels_map[rect]

    
    def crop_boxes(self):
        if not self.image_item:
            return
    
        original_pixmap = self.image_item.pixmap()
        base_path = os.path.join(os.getcwd(), "crops")
        os.makedirs(base_path, exist_ok=True)
    
        metadata = {}
    
        for idx, rect_item in enumerate(self.rect_items, 1):
            rect = rect_item.rect().toRect()
            cropped = original_pixmap.copy(rect)
    
            save_path = os.path.join(base_path, f"{idx}.png")
            cropped.save(save_path)
    
            # Save metadata
            metadata[str(idx)] = {
                "x": rect.x(),
                "y": rect.y(),
                "width": rect.width(),
                "height": rect.height()
            }
    
        # Write metadata JSON
        metadata_path = os.path.join(base_path, "coordinates.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=4)