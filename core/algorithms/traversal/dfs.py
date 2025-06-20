from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QMessageBox
from core.matrices.graph_matrices import GraphMatrices

class DFSAnimator(QObject):
    finished = pyqtSignal(list)

    def __init__(self, graph_matrices: GraphMatrices, graph_canvas, delay=500):
        super().__init__()
        self.graph_matrices = graph_matrices
        self.graph_canvas = graph_canvas
        self.colors = {
            'default': QColor(200, 200, 200),
            'visited': QColor(255, 165, 0),
            'current': QColor(255, 0, 0),
            'edge_default': QColor(0, 0, 0),
            'edge_visited': QColor(255, 165, 0)
        }
        self.delay = delay
        self.visited = set()
        self.visited_edges = set()
        self.traversal_order = []
        self.stack = []
        self.timer = QTimer()
        self.timer.timeout.connect(self._step)
        self.current_vertex = None

    def reset_colors(self):
        for vertex in self.graph_matrices.vertices:
            vertex.set_color(self.colors['default'])
        for edge in self.graph_canvas.edges:
            edge[2].setPen(QPen(self.colors['edge_default'], 2))
        self.graph_canvas.scene.update()

    def start(self, start_vertex):
        self.reset_colors()
        self.visited.clear()
        self.visited_edges.clear()
        self.traversal_order.clear()
        self.stack = [(start_vertex, None)]
        self.current_vertex = None
        self.timer.start(self.delay)

    def _step(self):
        if not self.stack:
            self.timer.stop()
            self.finished.emit(self.traversal_order)
            return

        vertex, parent = self.stack.pop()
        if vertex in self.visited:
            return

        # Color current vertex
        vertex.set_color(self.colors['current'])
        self.graph_canvas.scene.update()

        # Color edge if not root
        if parent:
            for edge in self.graph_canvas.edges:
                if (edge[0] == parent and edge[1] == vertex) or (edge[0] == vertex and edge[1] == parent):
                    edge[2].setPen(QPen(self.colors['edge_visited'], 2))
                    self.visited_edges.add(edge)
                    break

        self.visited.add(vertex)
        self.traversal_order.append(vertex)

        # After a short delay, mark as visited and push neighbors
        QTimer.singleShot(self.delay // 2, lambda: self._visit_neighbors(vertex))

    def _visit_neighbors(self, vertex):
        vertex.set_color(self.colors['visited'])
        current_idx = self.graph_matrices.vertex_indices[vertex]
        neighbors = []
        for neighbor_idx, weight in enumerate(self.graph_matrices.adjacency_matrix[current_idx]):
            if weight > 0:
                neighbor = self.graph_matrices.vertices[neighbor_idx]
                if neighbor not in self.visited:
                    neighbors.append((neighbor, vertex))
        # Add neighbors in reverse to simulate stack (DFS)
        self.stack.extend(reversed(neighbors))
        self.graph_canvas.scene.update()

    def run(self, start_vertex):
        self.start(start_vertex)

def run_dfs(graph_matrices: GraphMatrices, graph_canvas, start_vertex=None):
    animator = DFSAnimator(graph_matrices, graph_canvas)
    if start_vertex:
        animator.run(start_vertex)
        return animator
    else:
        QMessageBox.information(graph_canvas, "DFS", "Cliquez sur un sommet pour commencer le parcours DFS.")
        def on_vertex_click(vertex):
            graph_canvas.vertex_clicked.disconnect(on_vertex_click)
            animator.run(vertex)
        graph_canvas.vertex_clicked.connect(on_vertex_click)
        return animator