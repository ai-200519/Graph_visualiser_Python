from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QMessageBox
from core.matrices.graph_matrices import GraphMatrices
import math

class DijkstraAnimator(QObject):
    finished = pyqtSignal(dict)

    def __init__(self, graph_matrices: GraphMatrices, graph_canvas, delay=500):
        super().__init__()
        self.graph_matrices = graph_matrices
        self.graph_canvas = graph_canvas
        self.colors = {
            'default': QColor(200, 200, 200),
            'visited': QColor(255, 165, 0),
            'current': QColor(255, 0, 0),
            'edge_default': QColor(0, 0, 0),
            'edge_visited': QColor(0, 128, 255),
            'path': QColor(0, 255, 0),
            'start': QColor(255, 255, 0),
            'end': QColor(255, 0, 255)
        }
        self.delay = delay
        self.visited = set()
        self.distances = {}
        self.previous = {}
        self.unvisited = set()
        self.timer = QTimer()
        self.timer.timeout.connect(self._step)
        self.current_vertex = None
        self.start_vertex = None
        self.end_vertex = None
        self.path_found = False

    def reset_colors(self):
        for vertex in self.graph_matrices.vertices:
            vertex.set_color(self.colors['default'])
        for edge in self.graph_canvas.edges:
            edge[2].setPen(QPen(self.colors['edge_default'], 2))
        self.graph_canvas.scene.update()

    def start(self, start_vertex, end_vertex):
        self.reset_colors()
        self.visited.clear()
        self.unvisited = set(self.graph_matrices.vertices)
        self.distances = {v: math.inf for v in self.graph_matrices.vertices}
        self.previous = {v: None for v in self.graph_matrices.vertices}
        self.distances[start_vertex] = 0
        self.current_vertex = start_vertex
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        self.path_found = False
        start_vertex.set_color(self.colors['start'])
        end_vertex.set_color(self.colors['end'])
        self.graph_canvas.scene.update()
        self.timer.start(self.delay)

    def _step(self):
        if not self.unvisited or self.path_found:
            self.timer.stop()
            self._highlight_shortest_path()
            self.finished.emit(self.distances)
            self._show_distance()
            return

        # Trouver le sommet non visité avec la plus petite distance
        current = min(
            (v for v in self.unvisited),
            key=lambda v: self.distances[v],
            default=None
        )
        if current is None or self.distances[current] == math.inf:
            self.timer.stop()
            self._highlight_shortest_path()
            self.finished.emit(self.distances)
            self._show_distance()
            return

        # Si on atteint le sommet d'arrivée, on arrête l'animation
        if current == self.end_vertex:
            self.path_found = True
            self.timer.stop()
            self._highlight_shortest_path()
            self.finished.emit(self.distances)
            self._show_distance()
            return

        # Colorer le sommet courant
        current.set_color(self.colors['current'])
        self.graph_canvas.scene.update()

        QTimer.singleShot(self.delay // 2, lambda: self._visit_neighbors(current))

    def _visit_neighbors(self, current):
        current.set_color(self.colors['visited'])
        self.unvisited.remove(current)
        current_idx = self.graph_matrices.vertex_indices[current]
        for neighbor_idx, weight in enumerate(self.graph_matrices.adjacency_matrix[current_idx]):
            if weight > 0:
                neighbor = self.graph_matrices.vertices[neighbor_idx]
                if neighbor in self.unvisited:
                    alt = self.distances[current] + weight
                    if alt < self.distances[neighbor]:
                        self.distances[neighbor] = alt
                        self.previous[neighbor] = current
                        # Colorer l'arête comme "visitée"
                        for edge in self.graph_canvas.edges:
                            if (edge[0] == current and edge[1] == neighbor) or \
                               (edge[0] == neighbor and edge[1] == current):
                                edge[2].setPen(QPen(self.colors['edge_visited'], 2))
                                break
        self.graph_canvas.scene.update()

    def _highlight_shortest_path(self):
        # Colorer le chemin le plus court de start à end
        v = self.end_vertex
        if self.previous[v] is None and v != self.start_vertex:
            return  # Pas de chemin trouvé
        while self.previous[v] is not None:
            u = self.previous[v]
            for edge in self.graph_canvas.edges:
                if (edge[0] == u and edge[1] == v) or (edge[0] == v and edge[1] == u):
                    edge[2].setPen(QPen(self.colors['path'], 3))
                    break
            v = u
        self.graph_canvas.scene.update()

    def _show_distance(self):
        # Afficher la distance minimale entre start et end
        d = self.distances[self.end_vertex]
        label_start = getattr(self.start_vertex, "label", str(self.graph_matrices.vertex_indices[self.start_vertex]))
        label_end = getattr(self.end_vertex, "label", str(self.graph_matrices.vertex_indices[self.end_vertex]))
        if d == math.inf:
            msg = f"Aucun chemin entre {label_start} et {label_end}."
        else:
            msg = f"Distance minimale de {label_start} à {label_end} : {d}"
        QMessageBox.information(self.graph_canvas, "Dijkstra - Résultat", msg)

    def run(self, start_vertex, end_vertex):
        self.start(start_vertex, end_vertex)

def run_dijkstra(graph_matrices: GraphMatrices, graph_canvas, start_vertex=None, end_vertex=None):
    animator = DijkstraAnimator(graph_matrices, graph_canvas)
    if not graph_matrices.vertices:
        QMessageBox.warning(graph_canvas, "Dijkstra", "Le graphe est vide.")
        return None

    # Vérification des poids négatifs
    for row in graph_matrices.adjacency_matrix:
        for weight in row:
            if weight < 0:
                QMessageBox.critical(graph_canvas, "Erreur Dijkstra", "Le graphe contient des poids négatifs.\nDijkstra ne supporte pas les arêtes de poids négatif.")
                return None

    if start_vertex and end_vertex:
        animator.run(start_vertex, end_vertex)
        return animator
    else:
        # Demander à l'utilisateur de cliquer sur deux sommets
        QMessageBox.information(graph_canvas, "Dijkstra", "Cliquez sur le sommet de départ.")
        selection = {'start': None, 'end': None}

        def on_first_click(vertex):
            selection['start'] = vertex
            graph_canvas.vertex_clicked.disconnect(on_first_click)
            vertex.set_color(QColor(255, 255, 0))  # Jaune pour le départ
            graph_canvas.scene.update()
            QMessageBox.information(graph_canvas, "Dijkstra", "Cliquez sur le sommet d'arrivée.")
            graph_canvas.vertex_clicked.connect(on_second_click)

        def on_second_click(vertex):
            selection['end'] = vertex
            graph_canvas.vertex_clicked.disconnect(on_second_click)
            vertex.set_color(QColor(255, 0, 255))  # Magenta pour l'arrivée
            graph_canvas.scene.update()
            animator.run(selection['start'], selection['end'])

        graph_canvas.vertex_clicked.connect(on_first_click)
        return animator