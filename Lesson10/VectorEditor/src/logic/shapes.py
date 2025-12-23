from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItemGroup
from PySide6.QtGui import QPen, QColor, QPainterPath
from src.constants import TYPE_GROUP

class Shape:
    @property
    def type_name(self) -> str:
        raise NotImplementedError

    def to_dict(self) -> dict:
        raise NotImplementedError
    
    def set_geometry(self, start, end):
        raise NotImplementedError

    def set_active_color(self, color: str):
        if hasattr(self, "setPen"):
            pen = self.pen()
            pen.setColor(QColor(color))
            self.setPen(pen)

    def set_stroke_width(self, width: int):
        if hasattr(self, "setPen"):
            pen = self.pen()
            pen.setWidth(width)
            self.setPen(pen)

class PrimitiveShape(QGraphicsPathItem, Shape):
    def __init__(self, color="black", stroke_width=2):
        super().__init__()
        pen = QPen(QColor(color))
        pen.setWidth(stroke_width)
        self.setPen(pen)
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemSendsGeometryChanges)

class Rectangle(PrimitiveShape):
    def __init__(self, x, y, w, h, color="black", stroke_width=2):
        super().__init__(color, stroke_width)
        self.rect_x = x
        self.rect_y = y
        self.rect_w = w
        self.rect_h = h
        self._update_path()

    @property
    def type_name(self): return "rect"

    def _update_path(self):
        path = QPainterPath()
        path.addRect(self.rect_x, self.rect_y, self.rect_w, self.rect_h)
        self.setPath(path)

    def set_geometry(self, start, end):
        self.rect_x = min(start.x(), end.x())
        self.rect_y = min(start.y(), end.y())
        self.rect_w = abs(end.x() - start.x())
        self.rect_h = abs(end.y() - start.y())
        self._update_path()

    def to_dict(self):
        return {
            "type": self.type_name,
            "pos": [self.x(), self.y()],
            "props": {
                "x": self.rect_x, "y": self.rect_y, "w": self.rect_w, "h": self.rect_h,
                "color": self.pen().color().name(), "width": self.pen().width()
            }
        }

class Ellipse(PrimitiveShape):
    def __init__(self, x, y, w, h, color="black", stroke_width=2):
        super().__init__(color, stroke_width)
        self.rect_x = x; self.rect_y = y; self.rect_w = w; self.rect_h = h
        self._update_path()

    @property
    def type_name(self): return "ellipse"

    def _update_path(self):
        path = QPainterPath()
        path.addEllipse(self.rect_x, self.rect_y, self.rect_w, self.rect_h)
        self.setPath(path)

    def set_geometry(self, start, end):
        self.rect_x = min(start.x(), end.x())
        self.rect_y = min(start.y(), end.y())
        self.rect_w = abs(end.x() - start.x())
        self.rect_h = abs(end.y() - start.y())
        self._update_path()

    def to_dict(self):
        return {
            "type": self.type_name,
            "pos": [self.x(), self.y()],
            "props": {
                "x": self.rect_x, "y": self.rect_y, "w": self.rect_w, "h": self.rect_h,
                "color": self.pen().color().name(), "width": self.pen().width()
            }
        }

class Line(PrimitiveShape):
    def __init__(self, x1, y1, x2, y2, color="black", stroke_width=2):
        super().__init__(color, stroke_width)
        self.lx1, self.ly1, self.lx2, self.ly2 = x1, y1, x2, y2
        self._update_path()

    @property
    def type_name(self): return "line"

    def _update_path(self):
        path = QPainterPath()
        path.moveTo(self.lx1, self.ly1)
        path.lineTo(self.lx2, self.ly2)
        self.setPath(path)

    def set_geometry(self, start, end):
        self.lx1, self.ly1 = start.x(), start.y()
        self.lx2, self.ly2 = end.x(), end.y()
        self._update_path()

    def to_dict(self):
        return {
            "type": self.type_name,
            "pos": [self.x(), self.y()],
            "props": {
                "x1": self.lx1, "y1": self.ly1, "x2": self.lx2, "y2": self.ly2,
                "color": self.pen().color().name(), "width": self.pen().width()
            }
        }

class Group(QGraphicsItemGroup, Shape):
    def __init__(self):
        super().__init__()
        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable)
        self.setHandlesChildEvents(True)

    @property
    def type_name(self): return TYPE_GROUP

    def set_geometry(self, start, end): pass

    def set_active_color(self, color: str):
        for child in self.childItems():
            if isinstance(child, Shape):
                child.set_active_color(color)

    def set_stroke_width(self, width: int):
        for child in self.childItems():
            if isinstance(child, Shape):
                child.set_stroke_width(width)

    def to_dict(self):
        children_data = []
        for child in self.childItems():
            if isinstance(child, Shape):
                children_data.append(child.to_dict())
        return {
            "type": self.type_name,
            "pos": [self.x(), self.y()],
            "children": children_data
        }