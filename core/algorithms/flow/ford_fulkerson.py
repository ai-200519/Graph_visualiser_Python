from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QMessageBox
from core.matrices.graph_matrices import GraphMatrices
from ui.edge_item import EdgeItem
from collections import deque

class FordFulkersonAnimator(QObject):
    finished = pyqtSignal(int)

    def __init__(self, graph_matrices: GraphMatrices, graph_canvas, delay=500):
        super().__init__()
        self.graph_matrices = graph_matrices
        self.graph_canvas = graph_canvas
        self.colors = {
            'default': QColor(200, 200, 200),
            'source': QColor(0, 255, 0),      # Vert pour la source
            'sink': QColor(255, 0, 0),        # Rouge pour le puits
            'path': QColor(255, 165, 0),      # Orange pour le chemin augmentant
            'flow': QColor(0, 0, 255),        # Bleu pour le flot
            'visited': QColor(255, 255, 0),   # Jaune pour les sommets visités
            'current': QColor(128, 0, 128)    # Violet pour le sommet courant
        }
        self.delay = delay
        self.timer = QTimer()
        self.timer.timeout.connect(self._step)
        self.animation_queue = []
        self.algorithm_completed = False
        self.max_flow = 0
        self.source_vertex = None
        self.sink_vertex = None
        self.residual_graph = None
        self.current_path = []

    def reset_colors(self):
        """Reset all colors to default"""
        for vertex in self.graph_matrices.vertices:
            vertex.set_color(self.colors['default'])
        for edge in self.graph_canvas.edges:
            edge[2].setPen(QPen(self.colors['default'], 2))
        self.graph_canvas.scene.update()

    def start(self, source_vertex, sink_vertex):
        """Start the Ford-Fulkerson algorithm animation"""
        if not self.graph_matrices.vertices:
            QMessageBox.warning(self.graph_canvas, "Ford-Fulkerson", "Le graphe est vide.")
            return

        # Check if source and sink are the same
        if source_vertex == sink_vertex:
            QMessageBox.warning(self.graph_canvas, "Ford-Fulkerson", 
                              "La source et le puits ne peuvent pas être le même sommet.")
            return

        self.reset_colors()
        self.animation_queue.clear()
        self.algorithm_completed = False
        self.max_flow = 0
        self.source_vertex = source_vertex
        self.sink_vertex = sink_vertex
        
        # Color source and sink vertices
        source_vertex.set_color(self.colors['source'])
        sink_vertex.set_color(self.colors['sink'])
        self.graph_canvas.scene.update()

        try:
            # Initialize residual graph
            n = len(self.graph_matrices.vertices)
            self.residual_graph = [[0] * n for _ in range(n)]
            
            # Copy original graph to residual graph
            for i in range(n):
                for j in range(n):
                    self.residual_graph[i][j] = self.graph_matrices.adjacency_matrix[i][j]
            
            # Prepare animation steps
            self._prepare_animation()
            
            # Start animation
            self.timer.start(self.delay)
            
        except Exception as e:
            QMessageBox.critical(self.graph_canvas, "Erreur", f"Erreur lors de l'initialisation de Ford-Fulkerson : {str(e)}")
            self.cleanup()

    def _prepare_animation(self):
        """Prepare the animation steps for Ford-Fulkerson"""
        n = len(self.graph_matrices.vertices)
        source_idx = self.graph_matrices.vertex_indices[self.source_vertex]
        sink_idx = self.graph_matrices.vertex_indices[self.sink_vertex]
        
        # Run Ford-Fulkerson algorithm and prepare animation
        while True:
            # Find augmenting path using BFS
            path = self._find_augmenting_path(source_idx, sink_idx)
            
            if not path:
                # No more augmenting paths found
                break
            
            # Calculate bottleneck capacity
            bottleneck = float('inf')
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                bottleneck = min(bottleneck, self.residual_graph[u][v])
            
            # Add animation steps for this path
            self.animation_queue.append(('path_found', path, bottleneck))
            
            # Update residual graph
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                self.residual_graph[u][v] -= bottleneck
                self.residual_graph[v][u] += bottleneck
            
            self.max_flow += bottleneck
        
        # Add final result step
        self.animation_queue.append(('show_result',))

    def _find_augmenting_path(self, source_idx, sink_idx):
        """Find an augmenting path using BFS"""
        n = len(self.residual_graph)
        visited = [False] * n
        parent = [-1] * n
        queue = deque([source_idx])
        visited[source_idx] = True
        
        while queue and not visited[sink_idx]:
            u = queue.popleft()
            for v in range(n):
                if not visited[v] and self.residual_graph[u][v] > 0:
                    visited[v] = True
                    parent[v] = u
                    queue.append(v)
        
        if not visited[sink_idx]:
            return None
        
        # Reconstruct path
        path = []
        v = sink_idx
        while v != -1:
            path.append(v)
            v = parent[v]
        path.reverse()
        return path

    def _step(self):
        """Execute one animation step"""
        try:
            if not self.animation_queue:
                self.timer.stop()
                self.algorithm_completed = True
                self.finished.emit(self.max_flow)
                return

            step_type, *args = self.animation_queue.pop(0)

            if step_type == 'path_found':
                path, bottleneck = args
                
                # Color the path vertices
                for vertex_idx in path:
                    vertex = self.graph_matrices.vertices[vertex_idx]
                    if vertex == self.source_vertex:
                        vertex.set_color(self.colors['source'])
                    elif vertex == self.sink_vertex:
                        vertex.set_color(self.colors['sink'])
                    else:
                        vertex.set_color(self.colors['path'])
                
                # Color the path edges
                for i in range(len(path) - 1):
                    u_idx, v_idx = path[i], path[i + 1]
                    u_vertex = self.graph_matrices.vertices[u_idx]
                    v_vertex = self.graph_matrices.vertices[v_idx]
                    
                    for edge in self.graph_canvas.edges:
                        if (edge[0] == u_vertex and edge[1] == v_vertex) or \
                           (edge[0] == v_vertex and edge[1] == u_vertex):
                            edge[2].setPen(QPen(self.colors['path'], 3))
                            break
                
                self.graph_canvas.scene.update()
                
                # Show bottleneck information
                QMessageBox.information(self.graph_canvas, "Chemin Augmentant", 
                                      f"Chemin trouvé avec capacité de goulot d'étranglement : {bottleneck}")

            elif step_type == 'show_result':
                # Show final result
                QMessageBox.information(self.graph_canvas, "Ford-Fulkerson - Résultat", 
                                      f"Flot maximum de {self.source_vertex.label} à {self.sink_vertex.label} : {self.max_flow}")

        except Exception as e:
            self.timer.stop()
            QMessageBox.critical(self.graph_canvas, "Erreur", f"Erreur lors de l'animation de Ford-Fulkerson : {str(e)}")
            self.cleanup()

    def cleanup(self):
        """Clean up the animator"""
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        self.animation_queue.clear()
        self.algorithm_completed = False

    def run(self, source_vertex, sink_vertex):
        """Run the Ford-Fulkerson algorithm"""
        self.start(source_vertex, sink_vertex)

def run_ford_fulkerson(graph_matrices: GraphMatrices, graph_canvas, source_vertex=None, sink_vertex=None):
    """Run Ford-Fulkerson algorithm with animation"""
    animator = FordFulkersonAnimator(graph_matrices, graph_canvas)
    
    if not graph_matrices.vertices:
        QMessageBox.warning(graph_canvas, "Ford-Fulkerson", "Le graphe est vide.")
        return None

    # Check for negative weights (not allowed in flow networks)
    for row in graph_matrices.adjacency_matrix:
        for weight in row:
            if weight < 0:
                QMessageBox.critical(graph_canvas, "Erreur Ford-Fulkerson", 
                                   "Le graphe contient des poids négatifs.\nFord-Fulkerson ne supporte que les capacités positives.")
                return None

    if source_vertex and sink_vertex:
        animator.run(source_vertex, sink_vertex)
        return animator
    else:
        # Ask user to click on two vertices
        QMessageBox.information(graph_canvas, "Ford-Fulkerson", "Cliquez sur le sommet source.")
        selection = {'source': None, 'sink': None}

        def on_first_click(vertex):
            selection['source'] = vertex
            graph_canvas.vertex_clicked.disconnect(on_first_click)
            vertex.set_color(QColor(0, 255, 0))  # Green for source
            graph_canvas.scene.update()
            QMessageBox.information(graph_canvas, "Ford-Fulkerson", "Cliquez sur le sommet puits.")
            graph_canvas.vertex_clicked.connect(on_second_click)

        def on_second_click(vertex):
            selection['sink'] = vertex
            graph_canvas.vertex_clicked.disconnect(on_second_click)
            vertex.set_color(QColor(255, 0, 0))  # Red for sink
            graph_canvas.scene.update()
            
            if selection['source'] == selection['sink']:
                QMessageBox.warning(graph_canvas, "Ford-Fulkerson", 
                                  "La source et le puits ne peuvent pas être le même sommet.")
                animator.reset_colors()
                return
            
            animator.run(selection['source'], selection['sink'])

        graph_canvas.vertex_clicked.connect(on_first_click)
        return animator
