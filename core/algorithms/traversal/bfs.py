
from collections import deque
from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QMessageBox
from core.matrices.graph_matrices import GraphMatrices

class BFSAnimator(QObject):
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
        self.queue = deque()
        self.timer = QTimer()
        self.timer.timeout.connect(self._step)

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
        self.queue = deque([start_vertex])
        self.visited.add(start_vertex)
        self.timer.start(self.delay)

    def _step(self):
        if not self.queue:
            self.timer.stop()
            self.finished.emit(self.traversal_order)
            return

        current_vertex = self.queue.popleft()
        current_vertex.set_color(self.colors['current'])
        self.graph_canvas.scene.update()

        QTimer.singleShot(self.delay // 2, lambda: self._visit_neighbors(current_vertex))

    def _visit_neighbors(self, current_vertex):
        current_vertex.set_color(self.colors['visited'])
        self.traversal_order.append(current_vertex)
        current_idx = self.graph_matrices.vertex_indices[current_vertex]
        for neighbor_idx, weight in enumerate(self.graph_matrices.adjacency_matrix[current_idx]):
            if weight > 0:
                neighbor = self.graph_matrices.vertices[neighbor_idx]
                if neighbor not in self.visited:
                    for edge in self.graph_canvas.edges:
                        if (edge[0] == current_vertex and edge[1] == neighbor) or \
                           (edge[0] == neighbor and edge[1] == current_vertex):
                            edge[2].setPen(QPen(self.colors['edge_visited'], 2))
                            self.visited_edges.add(edge)
                            break
                    self.visited.add(neighbor)
                    self.queue.append(neighbor)
        self.graph_canvas.scene.update()

    def run(self, start_vertex):
        self.start(start_vertex)

def run_bfs(graph_matrices: GraphMatrices, graph_canvas, start_vertex=None):
    animator = BFSAnimator(graph_matrices, graph_canvas)
    if start_vertex:
        animator.run(start_vertex)
        return animator
    else:
        # Afficher le message à l'utilisateur
        QMessageBox.information(graph_canvas, "BFS", "Cliquez sur un sommet pour commencer le parcours BFS.")
        def on_vertex_click(vertex):
            graph_canvas.vertex_clicked.disconnect(on_vertex_click)
            animator.run(vertex)
        graph_canvas.vertex_clicked.connect(on_vertex_click)
        return animator