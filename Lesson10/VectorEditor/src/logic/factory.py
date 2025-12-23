from src.logic.shapes import Rectangle, Line, Ellipse, Group, Shape
from src.constants import *

class ShapeFactory:
    @staticmethod
    def create_shape(type_name, start, end, color="black") -> Shape:
        x1, y1 = start.x(), start.y()
        x2, y2 = end.x(), end.y()
        
        if type_name == TYPE_LINE:
            return Line(x1, y1, x2, y2, color)
        
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        
        if type_name == TYPE_RECT:
            return Rectangle(x, y, w, h, color)
        elif type_name == TYPE_ELLIPSE:
            return Ellipse(x, y, w, h, color)
        else:
            raise ValueError(f"Unknown type: {type_name}")

    @staticmethod
    def from_dict(data: dict):
        t = data.get("type")
        if t == TYPE_GROUP:
            group = Group()
            pos = data.get("pos", [0, 0])
            group.setPos(pos[0], pos[1])
            for child_data in data.get("children", []):
                child = ShapeFactory.from_dict(child_data)
                group.addToGroup(child)
                if "pos" in child_data:
                    c_pos = child_data["pos"]
                    child.setPos(c_pos[0], c_pos[1])
            return group
        
        props = data.get("props", {})
        color = props.get("color", "black")
        width = props.get("width", 2)
        
        obj = None
        if t == TYPE_RECT:
            obj = Rectangle(props['x'], props['y'], props['w'], props['h'], color, width)
        elif t == TYPE_ELLIPSE:
            obj = Ellipse(props['x'], props['y'], props['w'], props['h'], color, width)
        elif t == TYPE_LINE:
            obj = Line(props['x1'], props['y1'], props['x2'], props['y2'], color, width)
            
        if obj and "pos" in data:
            obj.setPos(data["pos"][0], data["pos"][1])
            
        return obj