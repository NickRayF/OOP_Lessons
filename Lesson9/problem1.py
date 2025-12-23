import json
import sys
import itertools
from typing import Optional, List, Dict
from PySide6.QtGui import QPalette
from PySide6.QtCore import Qt, QRectF, QLineF, QPointF, Signal, QObject
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPainterPathStroker, QAction, QFont
from PySide6.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsTextItem, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QLabel,
    QPushButton, QInputDialog, QGroupBox
)


class UI:
    NODE_DIAMETER = 34
    NODE_RADIUS = NODE_DIAMETER / 2
    EDGE_WIDTH = 2
    MIN_DISTANCE = 52

    BG = QColor(245, 247, 250)
    CARD = QColor(255, 255, 255)
    BORDER = QColor(220, 224, 230)

    NODE = QColor(59, 130, 246)
    NODE_ACTIVE = QColor(99, 102, 241)
    EDGE = QColor(100, 116, 139)

    TEXT = QColor(17, 24, 39)
    MUTED = QColor(107, 114, 128)
    WEIGHT = QColor(2, 132, 199)
    MATCH = QColor(22, 163, 74)

    TABLE_BG = QColor(255, 255, 255)
    TABLE_ALT = QColor(250, 250, 252)
    TABLE_DIAG = QColor(240, 242, 245)


def solve_mapping(graph_adj: Dict[str, Dict[str, int]], matrix_data: List[List[str]]) -> Optional[Dict[str, int]]:
    if not graph_adj:
        return None

    n = len(matrix_data)
    if n == 0 or any(len(r) != n for r in matrix_data):
        return None

    nodes = list(graph_adj.keys())
    if len(nodes) != n:
        return None

    m_adj: Dict[int, Dict[int, int]] = {i: {} for i in range(n)}
    for r in range(n):
        for c in range(n):
            s = (matrix_data[r][c] or "").strip()
            if s.isdigit():
                w = int(s)
                if w > 0:
                    m_adj[r][c] = w

    graph_has_weights = any(any(w > 1 for w in neigh.values()) for neigh in graph_adj.values())
    if not graph_has_weights:
        for r in m_adj:
            for c in list(m_adj[r].keys()):
                m_adj[r][c] = 1

    g_deg = {u: len(graph_adj[u]) for u in nodes}
    m_deg = {i: len(m_adj[i]) for i in range(n)}
    if sorted(g_deg.values()) != sorted(m_deg.values()):
        return None

    g_by_deg: Dict[int, List[str]] = {}
    for u, d in g_deg.items():
        g_by_deg.setdefault(d, []).append(u)

    m_by_deg: Dict[int, List[int]] = {}
    for i, d in m_deg.items():
        m_by_deg.setdefault(d, []).append(i)

    for d in g_by_deg:
        if d not in m_by_deg or len(g_by_deg[d]) != len(m_by_deg[d]):
            return None

    groups = []
    for d in sorted(g_by_deg.keys()):
        groups.append((sorted(g_by_deg[d]), sorted(m_by_deg[d])))

    def check(mapping: Dict[str, int]) -> bool:
        for u, neigh in graph_adj.items():
            ui = mapping[u]
            for v, w in neigh.items():
                vi = mapping[v]
                if vi not in m_adj[ui]:
                    return False
                if m_adj[ui][vi] != w:
                    return False
        return True

    def rec(k: int, mapping: Dict[str, int]) -> Optional[Dict[str, int]]:
        if k == len(groups):
            return mapping if check(mapping) else None
        g_nodes, m_idx = groups[k]
        for perm in itertools.permutations(m_idx):
            nm = dict(mapping)
            for j, u in enumerate(g_nodes):
                nm[u] = perm[j]
            res = rec(k + 1, nm)
            if res is not None:
                return res
        return None

    ans0 = rec(0, {})
    if ans0 is None:
        return None
    return {u: ans0[u] + 1 for u in ans0}


class EdgeItem(QGraphicsLineItem):
    def __init__(self, source_item, dest_item, weight: str = ""):
        super().__init__()
        self.source = source_item
        self.dest = dest_item
        self.weight = weight

        self.setPen(QPen(UI.EDGE, UI.EDGE_WIDTH, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.setZValue(0)

        self.text_item = QGraphicsTextItem(weight, self)
        self.text_item.setDefaultTextColor(UI.WEIGHT)
        font = QFont("Segoe UI")
        font.setBold(True)
        font.setPointSize(10)
        self.text_item.setFont(font)

        self.update_geometry()

    def set_weight(self, value: str):
        self.weight = value
        self.text_item.setPlainText(value)
        self.update_geometry()

    def update_geometry(self):
        line = QLineF(self.source.scenePos(), self.dest.scenePos())
        self.setLine(line)
        if self.text_item.toPlainText():
            center = line.center()
            self.text_item.setPos(center.x() - 10, center.y() - 22)
        else:
            self.text_item.setPos(line.center())

    def shape(self):
        path = super().shape()
        stroker = QPainterPathStroker()
        stroker.setWidth(16)
        return stroker.createStroke(path)

    def mouseDoubleClickEvent(self, event):
        text, ok = QInputDialog.getText(None, "Вес ребра", "Введите вес (число):", text=self.weight)
        if ok:
            self.set_weight((text or "").strip())
        super().mouseDoubleClickEvent(event)


class NodeItem(QGraphicsEllipseItem):
    def __init__(self, name: str, x: float, y: float):
        rect = QRectF(-UI.NODE_RADIUS, -UI.NODE_RADIUS, UI.NODE_DIAMETER, UI.NODE_DIAMETER)
        super().__init__(rect)
        self.name = name
        self.mapped_id = None
        self.edges: List[EdgeItem] = []

        self.setBrush(QBrush(UI.NODE))
        self.setPen(QPen(Qt.NoPen))
        self.setPos(x, y)
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self._create_labels()

    def _create_labels(self):
        self.label = QGraphicsTextItem(self.name, self)
        self.label.setDefaultTextColor(QColor(255, 255, 255))
        font = QFont("Segoe UI")
        font.setBold(True)
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setPos(-7, -12)

        self.match_label = QGraphicsTextItem("", self)
        self.match_label.setDefaultTextColor(UI.MATCH)
        f2 = QFont("Segoe UI")
        f2.setBold(True)
        f2.setPointSize(11)
        self.match_label.setFont(f2)
        self.match_label.setPos(10, -26)

    def set_mapped_id(self, id_str: Optional[str]):
        self.mapped_id = id_str
        self.match_label.setPlainText(f"[{id_str}]" if id_str else "")

    def set_highlighted(self, is_active: bool):
        self.setBrush(QBrush(UI.NODE_ACTIVE if is_active else UI.NODE))

    def add_connection(self, edge: EdgeItem):
        self.edges.append(edge)

    def remove_connection(self, edge: EdgeItem):
        if edge in self.edges:
            self.edges.remove(edge)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            for edge in self.edges:
                edge.update_geometry()
        return super().itemChange(change, value)


class ChainBuilder:
    def __init__(self):
        self.active_node: Optional[NodeItem] = None

    def start_or_continue(self, node: NodeItem) -> Optional[NodeItem]:
        prev = self.active_node
        if self.active_node:
            self.active_node.set_highlighted(False)
        self.active_node = node
        self.active_node.set_highlighted(True)
        return prev

    def reset(self):
        if self.active_node:
            self.active_node.set_highlighted(False)
            self.active_node = None


class GraphManager(QObject):
    node_count_changed = Signal(int)

    def __init__(self, scene: QGraphicsScene):
        super().__init__()
        self.scene = scene
        self.node_counter = 0

    def reset(self):
        self.node_counter = 0
        self.scene.clear()
        self.node_count_changed.emit(0)

    def generate_name(self) -> str:
        n = self.node_counter
        name = ""
        while n >= 0:
            name = chr(ord("A") + (n % 26)) + name
            n = n // 26 - 1
        self.node_counter += 1
        return name

    def create_node(self, pos: QPointF, name: str = None) -> NodeItem:
        if name is None:
            name = self.generate_name()
        else:
            self.node_counter += 1
        node = NodeItem(name, pos.x(), pos.y())
        self.scene.addItem(node)
        self.node_count_changed.emit(self.get_node_count())
        return node

    def create_edge(self, u: NodeItem, v: NodeItem, weight: str = ""):
        if u == v:
            return
        for edge in u.edges:
            if (edge.source == u and edge.dest == v) or (edge.source == v and edge.dest == u):
                return
        edge = EdgeItem(u, v, weight)
        self.scene.addItem(edge)
        u.add_connection(edge)
        v.add_connection(edge)

    def delete_item(self, item: QGraphicsItem):
        if isinstance(item, NodeItem):
            for edge in list(item.edges):
                self.delete_item(edge)
            self.scene.removeItem(item)
            self.node_count_changed.emit(self.get_node_count())
            return
        if isinstance(item, EdgeItem):
            item.source.remove_connection(item)
            item.dest.remove_connection(item)
            self.scene.removeItem(item)
            return
        if isinstance(item, QGraphicsTextItem):
            parent = item.parentItem()
            if isinstance(parent, EdgeItem):
                self.delete_item(parent)

    def get_node_count(self) -> int:
        return sum(1 for item in self.scene.items() if isinstance(item, NodeItem))

    def is_position_valid(self, pos: QPointF) -> bool:
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                if QLineF(pos, item.scenePos()).length() < UI.MIN_DISTANCE:
                    return False
        return True

    def get_nodes(self) -> List[NodeItem]:
        return [i for i in self.scene.items() if isinstance(i, NodeItem)]


class WeightMatrixWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setRowCount(0)
        self.setColumnCount(0)

        self.horizontalHeader().setDefaultSectionSize(44)
        self.verticalHeader().setDefaultSectionSize(32)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.setStyleSheet("""
            QTableWidget {
                background: white;
                color: #111827;
                gridline-color: #e5e7eb;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
            }
            QHeaderView::section {
                background: #f3f4f6;
                color: #111827;
                padding: 6px;
                border: 0px;
                border-bottom: 1px solid #e5e7eb;
            }
            QTableCornerButton::section {
                background: #f3f4f6;
                border: 0px;
                border-bottom: 1px solid #e5e7eb;
            }
        """)
        self.itemChanged.connect(self.on_item_changed)

    def update_size(self, node_count: int):
        old = self.get_data()
        self.setRowCount(node_count)
        self.setColumnCount(node_count)
        headers = [str(i + 1) for i in range(node_count)]
        self.setHorizontalHeaderLabels(headers)
        self.setVerticalHeaderLabels(headers)

        self.blockSignals(True)
        for r in range(node_count):
            for c in range(node_count):
                text = ""
                if r < len(old) and c < len(old[r]):
                    text = old[r][c]
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)

                if r == c:
                    item.setFlags(Qt.ItemIsEnabled)
                    item.setBackground(QBrush(UI.TABLE_DIAG))
                else:
                    item.setBackground(QBrush(UI.TABLE_BG if (r + c) % 2 == 0 else UI.TABLE_ALT))

                self.setItem(r, c, item)
        self.blockSignals(False)

    def on_item_changed(self, item: QTableWidgetItem):
        r, c = item.row(), item.column()
        if r == c:
            return
        text = (item.text() or "").strip()
        if text and not text.isdigit():
            self.blockSignals(True)
            item.setText("")
            self.blockSignals(False)
            return

        self.blockSignals(True)
        sym = self.item(c, r)
        if sym:
            sym.setText(text)
        self.blockSignals(False)

    def get_data(self) -> List[List[str]]:
        n = self.rowCount()
        data = []
        for r in range(n):
            row = []
            for c in range(n):
                it = self.item(r, c)
                row.append(it.text() if it else "")
            data.append(row)
        return data

    def set_data(self, data: List[List[str]]):
        n = len(data)
        self.update_size(n)
        self.blockSignals(True)
        for r in range(n):
            for c in range(n):
                it = self.item(r, c)
                if it is not None:
                    it.setText((data[r][c] if c < len(data[r]) else "").strip())
        self.blockSignals(False)


class GraphScene(QGraphicsScene):
    def __init__(self, manager: GraphManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.chain_builder = ChainBuilder()
        self.setBackgroundBrush(QBrush(UI.BG))
        self.setSceneRect(0, 0, 2200, 2200)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Shift:
            self.chain_builder.reset()
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event):
        pos = event.scenePos()
        item = self.itemAt(pos, self.views()[0].transform())

        if isinstance(item, QGraphicsTextItem):
            item = item.parentItem()

        if event.button() == Qt.LeftButton:
            if event.modifiers() & Qt.ShiftModifier:
                if isinstance(item, NodeItem):
                    prev_node = self.chain_builder.start_or_continue(item)
                    if prev_node:
                        self.manager.create_edge(prev_node, item)
                    event.accept()
                    return
                self.chain_builder.reset()
            else:
                self.chain_builder.reset()

            if item is None:
                if self.manager.is_position_valid(pos):
                    self.manager.create_node(pos)
                event.accept()
                return

            super().mousePressEvent(event)
            return

        if event.button() == Qt.RightButton:
            self.chain_builder.reset()
            if item:
                self.manager.delete_item(item)
                event.accept()
                return

        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ЕГЭ Информатика — Задание 1 (Граф ↔ Матрица)")
        self.resize(1280, 720)

        base_scene = QGraphicsScene()
        self.graph_manager = GraphManager(base_scene)
        self.scene = GraphScene(self.graph_manager, self)
        self.graph_manager.scene = self.scene

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setStyleSheet("""
            QGraphicsView {
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                background: white;
            }
        """)

        self.matrix_widget = WeightMatrixWidget()
        self.graph_manager.node_count_changed.connect(self.matrix_widget.update_size)

        central = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(14)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(12)

        table_group = QGroupBox("Матрица смежности / весов")
        table_group.setStyleSheet(self._group_css())
        table_layout = QVBoxLayout()
        table_layout.addWidget(self.matrix_widget)
        table_group.setLayout(table_layout)

        ctrl_group = QGroupBox("Инструменты")
        ctrl_group.setStyleSheet(self._group_css())
        ctrl_layout = QVBoxLayout()

        self.btn_solve = QPushButton("Найти соответствие (решить)")
        self.btn_solve.setObjectName("primary")
        self.btn_solve.clicked.connect(self.run_solver)

        self.btn_clear_res = QPushButton("Сбросить результат")
        self.btn_clear_res.clicked.connect(self.clear_results)

        self.btn_clear_weights = QPushButton("Удалить веса с графа")
        self.btn_clear_weights.clicked.connect(self.clear_graph_weights)

        help_lbl = QLabel("ЛКМ пусто — узел • Shift+ЛКМ по узлам — ребро • ПКМ — удалить • Двойной клик по ребру — вес")
        help_lbl.setWordWrap(True)
        help_lbl.setStyleSheet("color: #6b7280;")

        ctrl_layout.addWidget(self.btn_solve)
        ctrl_layout.addWidget(self.btn_clear_res)
        ctrl_layout.addWidget(self.btn_clear_weights)
        ctrl_layout.addSpacing(6)
        ctrl_layout.addWidget(help_lbl)
        ctrl_group.setLayout(ctrl_layout)

        left_panel.addWidget(table_group, 2)
        left_panel.addWidget(ctrl_group, 0)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        title = QLabel("Редактор графа")
        title.setStyleSheet("font-size: 14px; font-weight: 700; color: #111827;")
        right_panel.addWidget(title)
        right_panel.addWidget(self.view, 1)

        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 3)
        self.setCentralWidget(central)

        self._apply_app_style()
        self.create_menu()

    def _group_css(self) -> str:
        return """
            QGroupBox {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                margin-top: 10px;
                color: #111827;
                font-weight: 600;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }
        """

    def _apply_app_style(self):
        self.setStyleSheet("""
            QWidget { font-family: "Segoe UI"; font-size: 10.5pt; color: #111827; }
            QPushButton {
                border: 1px solid #d1d5db;
                border-radius: 10px;
                padding: 9px 12px;
                background: white;
            }
            QPushButton:hover { background: #f9fafb; }
            QPushButton:pressed { background: #f3f4f6; }
            QPushButton#primary {
                background: #2563eb;
                color: white;
                border: 1px solid #2563eb;
                font-weight: 700;
            }
            QPushButton#primary:hover { background: #1d4ed8; border-color: #1d4ed8; }
            QMenuBar { background: white; border-bottom: 1px solid #e5e7eb; }
            QMenuBar::item { padding: 6px 10px; background: transparent; }
            QMenu { background: white; border: 1px solid #e5e7eb; }
            QMenu::item { padding: 6px 12px; }
            QMenu::item:selected { background: #eff6ff; }
        """)

    def create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("Файл")

        save_action = QAction("Сохранить...", self)
        save_action.triggered.connect(self.save_exercise)
        file_menu.addAction(save_action)

        load_action = QAction("Загрузить...", self)
        load_action.triggered.connect(self.load_exercise)
        file_menu.addAction(load_action)

        clear_action = QAction("Очистить всё", self)
        clear_action.triggered.connect(self.clear_all)
        file_menu.addAction(clear_action)

    def _graph_to_adj(self) -> Dict[str, Dict[str, int]]:
        nodes = self.graph_manager.get_nodes()
        g_adj: Dict[str, Dict[str, int]] = {n.name: {} for n in nodes}
        for node in nodes:
            for edge in node.edges:
                neigh = edge.dest if edge.source == node else edge.source
                w = 1
                s = (edge.weight or "").strip()
                if s.isdigit():
                    w = int(s)
                g_adj[node.name][neigh.name] = w
        return g_adj

    def run_solver(self):
        nodes = self.graph_manager.get_nodes()
        if not nodes:
            QMessageBox.warning(self, "Ошибка", "Граф пуст.")
            return

        matrix = self.matrix_widget.get_data()
        g_adj = self._graph_to_adj()
        mapping = solve_mapping(g_adj, matrix)

        if mapping:
            msg = "Решение найдено:\n\n"
            for name, idx in sorted(mapping.items(), key=lambda x: x[0]):
                msg += f"{name} → {idx}\n"
                for node in nodes:
                    if node.name == name:
                        node.set_mapped_id(str(idx))
            QMessageBox.information(self, "Успех", msg)
        else:
            QMessageBox.critical(
                self,
                "Не найдено",
                "Не удалось найти соответствие.\nПроверь:\n• одинаковые степени вершин\n• веса (если указаны) совпадают"
            )

    def clear_results(self):
        for node in self.graph_manager.get_nodes():
            node.set_mapped_id(None)

    def clear_graph_weights(self):
        for item in self.scene.items():
            if isinstance(item, EdgeItem):
                item.set_weight("")

    def clear_all(self):
        self.graph_manager.reset()
        self.matrix_widget.update_size(0)

    def save_exercise(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "JSON Files (*.json)")
        if not file_path:
            return

        nodes = self.graph_manager.get_nodes()
        node_id_map = {node: i for i, node in enumerate(nodes)}

        nodes_data = []
        for i, node in enumerate(nodes):
            nodes_data.append({"id": i, "name": node.name, "x": node.pos().x(), "y": node.pos().y()})

        edges_data = []
        visited = set()
        for node in nodes:
            for edge in node.edges:
                if edge in visited:
                    continue
                visited.add(edge)
                u_id = node_id_map.get(edge.source)
                v_id = node_id_map.get(edge.dest)
                if u_id is not None and v_id is not None:
                    edges_data.append({"u": u_id, "v": v_id, "w": edge.weight})

        data = {
            "graph": {"nodes": nodes_data, "edges": edges_data, "node_counter": self.graph_manager.node_counter},
            "matrix": self.matrix_widget.get_data()
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def load_exercise(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "JSON Files (*.json)")
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.clear_all()

            g_data = data.get("graph", {})
            self.graph_manager.node_counter = int(g_data.get("node_counter", 0))

            id_map = {}
            for n in g_data.get("nodes", []):
                node = self.graph_manager.create_node(QPointF(float(n["x"]), float(n["y"])), str(n["name"]))
                id_map[int(n["id"])] = node

            for e in g_data.get("edges", []):
                u = id_map.get(int(e["u"]))
                v = id_map.get(int(e["v"]))
                if u and v:
                    self.graph_manager.create_edge(u, v, str(e.get("w", "")))

            self.matrix_widget.set_data(data.get("matrix", []))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")


    pal = app.palette()

    pal.setColor(QPalette.ColorRole.Window, UI.BG)
    pal.setColor(QPalette.ColorRole.WindowText, UI.TEXT)
    pal.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(248, 250, 252))
    pal.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    pal.setColor(QPalette.ColorRole.ToolTipText, UI.TEXT)
    pal.setColor(QPalette.ColorRole.Text, UI.TEXT)
    pal.setColor(QPalette.ColorRole.Button, QColor(255, 255, 255))
    pal.setColor(QPalette.ColorRole.ButtonText, UI.TEXT)
    pal.setColor(QPalette.ColorRole.Highlight, QColor(37, 99, 235))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

    app.setPalette(pal)


    w = MainWindow()
    w.show()
    sys.exit(app.exec())
