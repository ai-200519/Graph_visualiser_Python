from typing import List, Dict, Set
import time
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPen
from core.matrices.graph_matrices import GraphMatrices

class GreedyColoringVisualizer:
    def __init__(self, graph_matrices: GraphMatrices, graph_canvas):
        self.graph_matrices = graph_matrices
        self.graph_canvas = graph_canvas
        # Couleurs pour les sommets (max 8 couleurs)
        self.vertex_colors = [
            QColor(255, 0, 0),    # Rouge
            QColor(0, 255, 0),    # Vert
            QColor(0, 0, 255),    # Bleu
            QColor(255, 255, 0),  # Jaune
            QColor(255, 0, 255),  # Magenta
            QColor(0, 255, 255),  # Cyan
            QColor(128, 0, 128),  # Violet
            QColor(255, 165, 0)   # Orange
        ]
        self.colors = {
            'default': QColor(200, 200, 200),  # Gris
            'current': QColor(255, 255, 255),  # Blanc
            'edge_default': QColor(0, 0, 0)    # Noir
        }
        self.vertex_color_map = {}  # Map des sommets à leurs couleurs

    def reset_colors(self):
        """Reset all vertex and edge colors to default"""
        for vertex in self.graph_matrices.vertices:
            vertex.set_color(self.colors['default'])
        for edge in self.graph_canvas.edges:
            edge[2].setPen(QPen(self.colors['edge_default'], 2))
        self.vertex_color_map.clear()

    def get_available_color(self, vertex) -> int:
        """Trouve la plus petite couleur disponible pour un sommet"""
        used_colors = set()
        # Vérifier les couleurs des voisins
        current_idx = self.graph_matrices.vertex_indices[vertex]
        for neighbor_idx, weight in enumerate(self.graph_matrices.adjacency_matrix[current_idx]):
            if weight > 0:  # Si il y a une arête
                neighbor = self.graph_matrices.vertices[neighbor_idx]
                if neighbor in self.vertex_color_map:
                    used_colors.add(self.vertex_color_map[neighbor])
        
        # Trouver la première couleur disponible
        for color_idx in range(len(self.vertex_colors)):
            if color_idx not in used_colors:
                return color_idx
        return 0  # Par défaut, utiliser la première couleur

    def greedy_coloring(self) -> Dict:
        """Implémentation de l'algorithme de coloration glouton avec visualisation"""
        self.reset_colors()
        
        # Colorer chaque sommet
        for vertex in self.graph_matrices.vertices:
            # Visualiser le sommet courant
            vertex.set_color(self.colors['current'])
            self.graph_canvas.scene.update()
            time.sleep(0.5)  # Animation delay
            
            # Trouver et appliquer la couleur disponible
            color_idx = self.get_available_color(vertex)
            self.vertex_color_map[vertex] = color_idx
            vertex.set_color(self.vertex_colors[color_idx])
            self.graph_canvas.scene.update()
            time.sleep(0.5)  # Animation delay
        
        return self.vertex_color_map

def run_greedy_coloring(graph_matrices: GraphMatrices, graph_canvas):
    """Exécuter l'algorithme de coloration glouton"""
    visualizer = GreedyColoringVisualizer(graph_matrices, graph_canvas)
    return visualizer.greedy_coloring()
