from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt
from PySide6.QtGui import QUndoStack, QPainter
from src.logic.tools import SelectionTool, CreationTool
from src.logic.shapes import Group
from src.logic.commands import DeleteCommand
from src.constants import *

class EditorCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setSceneRect(0, 0, DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMouseTracking(True)
        
        self.undo_stack = QUndoStack(self)
        
        self.tools = {
            "select": SelectionTool(self, self.undo_stack),
            TYPE_RECT: CreationTool(self, TYPE_RECT, self.undo_stack),
            TYPE_ELLIPSE: CreationTool(self, TYPE_ELLIPSE, self.undo_stack),
            TYPE_LINE: CreationTool(self, TYPE_LINE, self.undo_stack)
        }
        self.current_tool = self.tools["select"]

    def set_tool(self, name):
        if name in self.tools:
            self.current_tool = self.tools[name]
            self.setCursor(Qt.CrossCursor if name != "select" else Qt.ArrowCursor)

    def mousePressEvent(self, event): self.current_tool.mouse_press(event)
    def mouseMoveEvent(self, event): self.current_tool.mouse_move(event)
    def mouseReleaseEvent(self, event): self.current_tool.mouse_release(event)

    def group_selection(self):
        sel = self.scene.selectedItems()
        if len(sel) < 2: return
        
        self.undo_stack.beginMacro("Group")
        group = Group()
        self.scene.addItem(group)
        for item in sel:
            item.setSelected(False)
            group.addToGroup(item)
        group.setSelected(True)
        self.undo_stack.endMacro()

    def ungroup_selection(self):
        for item in self.scene.selectedItems():
            if isinstance(item, Group):
                # ИСПРАВЛЕНО ЗДЕСЬ: destroyGroup -> destroyItemGroup
                self.scene.destroyItemGroup(item)

    def delete_selection(self):
        sel = self.scene.selectedItems()
        if not sel: return
        self.undo_stack.beginMacro("Delete")
        for item in sel:
            self.undo_stack.push(DeleteCommand(self.scene, item))
        self.undo_stack.endMacro()