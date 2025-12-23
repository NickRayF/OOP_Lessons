from abc import ABC, abstractmethod
import json
from PySide6.QtGui import QImage, QPainter, QColor
from PySide6.QtCore import QRectF

class SaveStrategy(ABC):
    @abstractmethod
    def save(self, filename, scene): pass

class JsonSaveStrategy(SaveStrategy):
    def save(self, filename, scene):
        data = {"version": "1.0", "shapes": []}
        items = scene.items()[::-1]
        for item in items:
            if hasattr(item, "to_dict"):
                data["shapes"].append(item.to_dict())
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

class ImageSaveStrategy(SaveStrategy):
    def __init__(self, fmt="PNG", bg="transparent"):
        self.fmt = fmt
        self.bg = bg

    def save(self, filename, scene):
        rect = scene.itemsBoundingRect() # Обрезаем по содержимому
        if rect.isEmpty(): rect = scene.sceneRect()
            
        image = QImage(int(rect.width()), int(rect.height()), QImage.Format_ARGB32)
        if self.bg == "transparent":
            image.fill(QColor(0,0,0,0))
        else:
            image.fill(QColor(self.bg))
            
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        scene.render(painter, QRectF(image.rect()), rect)
        painter.end()
        image.save(filename, self.fmt)