from typing import Dict
import time
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QApplication
from core.matrices.graph_matrices import GraphMatrices

class WelshPowellVisualizer:
    def __init__(self, graph_matrices: GraphMatrices, graph_canvas, delay: float = 0.5):
        self.graph_matrices = graph_matrices
        self.graph_canvas = graph_canvas
        self.delay = delay
        self.vertex_colors = [
            QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255),
            QColor(255, 255, 0), QColor(255, 0, 255), QColor(0, 255, 255),
            QColor(128, 0, 128), QColor(255, 165, 0)
        ]
        self.colors = {
            'default': QColor(200, 200, 200),
            'current': QColor(255, 255, 255),
            'edge_default': QColor(0, 0, 0)
        }
        self.vertex_color_map = {}

    def reset_colors(self):
        for vertex in self.graph_matrices.vertices:
            vertex.set_color(self.colors['default'])
        for edge in self.graph_canvas.edges:
            edge[2].setPen(QPen(self.colors['edge_default'], 2))
        self.vertex_color_map.clear()
        self.graph_canvas.scene.update()
        QApplication.processEvents()

    def get_vertex_degree(self, vertex) -> int:
        idx = self.graph_matrices.vertex_indices[vertex]
        return sum(1 for w in self.graph_matrices.adjacency_matrix[idx] if w > 0)

    def are_adjacent(self, v1, v2) -> bool:
        idx1 = self.graph_matrices.vertex_indices[v1]
        idx2 = self.graph_matrices.vertex_indices[v2]
        return self.graph_matrices.adjacency_matrix[idx1][idx2] > 0

    def welsh_powell_coloring(self) -> Dict:
        self.reset_colors()
        if not self.graph_matrices.vertices:
            return {}

        # 1. Calculer le degré de chaque sommet
        vertices_with_degree = [(vertex, self.get_vertex_degree(vertex))
                                for vertex in self.graph_matrices.vertices]
        # 2. Trier les sommets par degré décroissant
        vertices_with_degree.sort(key=lambda x: x[1], reverse=True)
        sorted_vertices = [v[0] for v in vertices_with_degree]

        current_color = 0
        while sorted_vertices:
            vertex = sorted_vertices[0]
            # Visualiser le sommet courant
            vertex.set_color(self.colors['current'])
            self.graph_canvas.scene.update()
            QApplication.processEvents()
            time.sleep(self.delay)

            # Colorer le sommet
            self.vertex_color_map[vertex] = current_color
            vertex.set_color(self.vertex_colors[current_color])
            self.graph_canvas.scene.update()
            QApplication.processEvents()
            time.sleep(0.5)

            sorted_vertices.remove(vertex)

            # Colorer tous les sommets non adjacents avec la même couleur
            vertices_to_color = []
            for v in sorted_vertices[:]:
                if not self.are_adjacent(vertex, v):
                    vertices_to_color.append(v)
                    sorted_vertices.remove(v)

            for v in vertices_to_color:
                v.set_color(self.colors['current'])
                self.graph_canvas.scene.update()
                QApplication.processEvents()
                time.sleep(self.delay * 0.6)

                self.vertex_color_map[v] = current_color
                v.set_color(self.vertex_colors[current_color])
                self.graph_canvas.scene.update()
                QApplication.processEvents()
                time.sleep(0.3)

            current_color = (current_color + 1) % len(self.vertex_colors)

        return self.vertex_color_map

def run_welsh_powell(graph_matrices: GraphMatrices, graph_canvas, delay: float = 0.5):
    visualizer = WelshPowellVisualizer(graph_matrices, graph_canvas, delay)
    return visualizer.welsh_powell_coloring()