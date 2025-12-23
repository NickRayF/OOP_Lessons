import json
from PySide6.QtWidgets import QMainWindow, QToolBar, QFileDialog, QMessageBox, QWidget, QHBoxLayout
from PySide6.QtGui import QAction, QKeySequence
from src.widgets.canvas import EditorCanvas
from src.widgets.properties import PropertiesPanel
from src.constants import *
from src.logic.strategies import JsonSaveStrategy, ImageSaveStrategy
from src.logic.factory import ShapeFactory

class VectorEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vector Editor Final")
        self.resize(1000, 700)
        
        self.canvas = EditorCanvas()
        self.props = PropertiesPanel(self.canvas.scene, self.canvas.undo_stack)
        
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(self.canvas, 1)
        layout.addWidget(self.props)
        self.setCentralWidget(container)
        
        self._create_actions()
        self._create_toolbar()
        self._create_menu()

    def _create_actions(self):
        self.act_sel = QAction("Select", self, triggered=lambda: self.canvas.set_tool("select"))
        self.act_rect = QAction("Rect", self, triggered=lambda: self.canvas.set_tool(TYPE_RECT))
        self.act_ell = QAction("Ellipse", self, triggered=lambda: self.canvas.set_tool(TYPE_ELLIPSE))
        self.act_line = QAction("Line", self, triggered=lambda: self.canvas.set_tool(TYPE_LINE))
        
        self.act_group = QAction("Group", self, shortcut="Ctrl+G", triggered=self.canvas.group_selection)
        self.act_ungroup = QAction("Ungroup", self, shortcut="Ctrl+U", triggered=self.canvas.ungroup_selection)
        self.act_del = QAction("Delete", self, shortcut="Delete", triggered=self.canvas.delete_selection)
        
        self.act_undo = self.canvas.undo_stack.createUndoAction(self, "Undo")
        self.act_undo.setShortcut(QKeySequence.Undo)
        self.act_redo = self.canvas.undo_stack.createRedoAction(self, "Redo")
        self.act_redo.setShortcut(QKeySequence.Redo)
        
        self.act_save = QAction("Save", self, shortcut="Ctrl+S", triggered=self.on_save)
        self.act_open = QAction("Open", self, shortcut="Ctrl+O", triggered=self.on_open)

    def _create_toolbar(self):
        tb = self.addToolBar("Tools")
        tb.addAction(self.act_sel)
        tb.addAction(self.act_rect)
        tb.addAction(self.act_ell)
        tb.addAction(self.act_line)
        tb.addSeparator()
        tb.addAction(self.act_undo)
        tb.addAction(self.act_redo)

    def _create_menu(self):
        m = self.menuBar()
        mf = m.addMenu("File")
        mf.addAction(self.act_open)
        mf.addAction(self.act_save)
        
        me = m.addMenu("Edit")
        me.addAction(self.act_group)
        me.addAction(self.act_ungroup)
        me.addAction(self.act_del)

    def on_save(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save", "", "JSON (*.json);;PNG (*.png)")
        if not path: return
        
        if path.endswith(".png"): strategy = ImageSaveStrategy()
        else: strategy = JsonSaveStrategy()
            
        try:
            strategy.save(path, self.canvas.scene)
            self.statusBar().showMessage(f"Saved: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open", "", "JSON (*.json)")
        if not path: return
        
        try:
            with open(path, 'r') as f: data = json.load(f)
            self.canvas.scene.clear()
            self.canvas.undo_stack.clear()
            for s_data in data.get("shapes", []):
                s = ShapeFactory.from_dict(s_data)
                self.canvas.scene.addItem(s)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))