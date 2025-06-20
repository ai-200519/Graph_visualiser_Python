from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QMessageBox
from core.matrices.graph_matrices import GraphMatrices
from ui.edge_item import EdgeItem

class BellmanFordAnimator(QObject):
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
            'end': QColor(255, 0, 255),
            'negative_cycle': QColor(255, 0, 0)
        }
        self.delay = delay
        self.visited = set()
        self.distances = {}
        self.previous = {}
        self.timer = QTimer()
        self.timer.timeout.connect(self._step)
        self.current_vertex = None
        self.start_vertex = None
        self.end_vertex = None
        self.animation_queue = []
        self.current_iteration = 0
        self.max_iterations = 0
        self.negative_cycle_detected = False
        self.algorithm_completed = False

    def reset_colors(self):
        """Reset all colors to default"""
        for vertex in self.graph_matrices.vertices:
            vertex.set_color(self.colors['default'])
        for edge in self.graph_canvas.edges:
            edge[2].setPen(QPen(self.colors['edge_default'], 2))
        self.graph_canvas.scene.update()

    def start(self, start_vertex, end_vertex):
        """Start the Bellman-Ford algorithm animation"""
        if not self.graph_matrices.vertices:
            QMessageBox.warning(self.graph_canvas, "Bellman-Ford", "Le graphe est vide.")
            return

        # Check for edge weights and inform user about default weights
        default_weights_used = False
        for i in range(len(self.graph_matrices.adjacency_matrix)):
            for j in range(len(self.graph_matrices.adjacency_matrix[i])):
                if self.graph_matrices.adjacency_matrix[i][j] == 1:
                    # Check if this might be a default weight (from empty weight input)
                    u_vertex = self.graph_matrices.vertices[i]
                    v_vertex = self.graph_matrices.vertices[j]
                    
                    # Look for edges without weight text
                    for edge in self.graph_canvas.edges:
                        if (edge[0] == u_vertex and edge[1] == v_vertex) or \
                           (edge[0] == v_vertex and edge[1] == u_vertex):
                            if edge[3] is None:  # No weight text
                                default_weights_used = True
                                break
        
        if default_weights_used:
            QMessageBox.information(self.graph_canvas, "Bellman-Ford", 
                                  "Note: Certaines arêtes utilisent le poids par défaut (1) car aucun poids n'a été spécifié.")

        self.reset_colors()
        self.visited.clear()
        self.animation_queue.clear()
        self.current_iteration = 0
        self.negative_cycle_detected = False
        self.algorithm_completed = False
        
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        
        # Color start and end vertices
        start_vertex.set_color(self.colors['start'])
        end_vertex.set_color(self.colors['end'])
        self.graph_canvas.scene.update()

        try:
            # Prepare the algorithm data
            n = len(self.graph_matrices.vertices)
            self.distances = {v: float('inf') for v in self.graph_matrices.vertices}
            self.previous = {v: None for v in self.graph_matrices.vertices}
            self.distances[start_vertex] = 0
            
            # Get all edges
            edges = []
            for i in range(n):
                for j in range(n):
                    if self.graph_matrices.adjacency_matrix[i][j] != 0:
                        edges.append((i, j, self.graph_matrices.adjacency_matrix[i][j]))

            self.max_iterations = n - 1
            
            # Prepare animation steps for N-1 iterations (normal Bellman-Ford)
            for iteration in range(self.max_iterations):
                self.animation_queue.append(('iteration_start', iteration))
                
                # For each iteration, we'll check all edges and add relaxations to queue
                for u_idx, v_idx, weight in edges:
                    u_vertex = self.graph_matrices.vertices[u_idx]
                    v_vertex = self.graph_matrices.vertices[v_idx]
                    
                    # We'll check during animation if this edge should be relaxed
                    self.animation_queue.append(('check_relax', u_idx, v_idx, weight))
                
                self.animation_queue.append(('iteration_end', iteration))
            
            # Add one more iteration for negative cycle detection
            self.animation_queue.append(('iteration_start', self.max_iterations))
            for u_idx, v_idx, weight in edges:
                u_vertex = self.graph_matrices.vertices[u_idx]
                v_vertex = self.graph_matrices.vertices[v_idx]
                self.animation_queue.append(('check_negative_cycle', u_idx, v_idx, weight))
            
            # Show final path
            self.animation_queue.append(('show_path',))
            
            # Start animation
            self.timer.start(self.delay)
            
        except Exception as e:
            QMessageBox.critical(self.graph_canvas, "Erreur", f"Erreur lors de l'initialisation de Bellman-Ford : {str(e)}")
            self.cleanup()

    def _step(self):
        """Execute one animation step"""
        try:
            if not self.animation_queue:
                self.timer.stop()
                self.algorithm_completed = True
                self.finished.emit(self.distances)
                return

            step_type, *args = self.animation_queue.pop(0)

            if step_type == 'iteration_start':
                iteration = args[0]
                self.current_iteration = iteration
                # Color all vertices that have finite distances
                for vertex in self.graph_matrices.vertices:
                    if self.distances[vertex] != float('inf'):
                        vertex.set_color(self.colors['visited'])
                self.graph_canvas.scene.update()

            elif step_type == 'check_relax':
                u_idx, v_idx, weight = args
                u_vertex = self.graph_matrices.vertices[u_idx]
                v_vertex = self.graph_matrices.vertices[v_idx]
                
                # Check if we can relax this edge
                if self.distances[u_vertex] != float('inf'):
                    new_distance = self.distances[u_vertex] + weight
                    if new_distance < self.distances[v_vertex]:
                        # Color current vertices being processed
                        u_vertex.set_color(self.colors['current'])
                        v_vertex.set_color(self.colors['current'])
                        
                        # Update distances
                        self.distances[v_vertex] = new_distance
                        self.previous[v_vertex] = u_vertex
                        
                        # Color the edge being relaxed
                        for edge in self.graph_canvas.edges:
                            if (edge[0] == u_vertex and edge[1] == v_vertex) or \
                               (edge[0] == v_vertex and edge[1] == u_vertex):
                                edge[2].setPen(QPen(self.colors['edge_visited'], 2))
                                break

                        self.graph_canvas.scene.update()
                        
                        # Reset colors after a short delay
                        QTimer.singleShot(self.delay // 2, lambda: self._reset_step_colors(u_vertex, v_vertex))

            elif step_type == 'iteration_end':
                # Reset current colors and mark as visited
                for vertex in self.graph_matrices.vertices:
                    if vertex.brush().color() == self.colors['current']:
                        vertex.set_color(self.colors['visited'])
                self.graph_canvas.scene.update()

            elif step_type == 'check_negative_cycle':
                u_idx, v_idx, weight = args
                u_vertex = self.graph_matrices.vertices[u_idx]
                v_vertex = self.graph_matrices.vertices[v_idx]
                
                # Check for negative cycle
                if self.distances[u_vertex] != float('inf'):
                    if self.distances[u_vertex] + weight < self.distances[v_vertex]:
                        # Found a negative cycle
                        u_vertex.set_color(self.colors['negative_cycle'])
                        v_vertex.set_color(self.colors['negative_cycle'])
                        
                        # Color the edge in red
                        for edge in self.graph_canvas.edges:
                            if (edge[0] == u_vertex and edge[1] == v_vertex) or \
                               (edge[0] == v_vertex and edge[1] == u_vertex):
                                edge[2].setPen(QPen(self.colors['negative_cycle'], 3))
                                break
                        
                        self.negative_cycle_detected = True
                        self.graph_canvas.scene.update()
                        QMessageBox.warning(self.graph_canvas, "Cycle Négatif Détecté", 
                                          "L'algorithme a détecté un cycle de poids négatif dans le graphe.")
                        self.timer.stop()
                        return

            elif step_type == 'show_path':
                if self.negative_cycle_detected:
                    return
                
                # Show the shortest path
                path = self._reconstruct_path()
                if path:
                    # Color the path
                    for i in range(len(path) - 1):
                        u_vertex = path[i]
                        v_vertex = path[i + 1]
                        u_vertex.set_color(self.colors['path'])
                        v_vertex.set_color(self.colors['path'])
                        
                        # Color the edge
                        for edge in self.graph_canvas.edges:
                            if (edge[0] == u_vertex and edge[1] == v_vertex) or \
                               (edge[0] == v_vertex and edge[1] == u_vertex):
                                edge[2].setPen(QPen(self.colors['path'], 3))
                                break

                    # Color the last vertex
                    if path:
                        path[-1].set_color(self.colors['path'])
                    
                    self.graph_canvas.scene.update()
                    
                    # Show result
                    distance = self.distances[self.end_vertex]
                    if distance == float('inf'):
                        QMessageBox.information(self.graph_canvas, "Bellman-Ford", 
                                              f"Aucun chemin trouvé de {self.start_vertex.label} à {self.end_vertex.label}.")
                    else:
                        QMessageBox.information(self.graph_canvas, "Bellman-Ford", 
                                              f"Distance minimale de {self.start_vertex.label} à {self.end_vertex.label} : {distance}")
                else:
                    QMessageBox.information(self.graph_canvas, "Bellman-Ford", 
                                          f"Aucun chemin trouvé de {self.start_vertex.label} à {self.end_vertex.label}.")

        except Exception as e:
            self.timer.stop()
            QMessageBox.critical(self.graph_canvas, "Erreur", f"Erreur lors de l'animation de Bellman-Ford : {str(e)}")
            self.cleanup()

    def _reset_step_colors(self, u_vertex, v_vertex):
        """Reset colors after a relaxation step"""
        if u_vertex.brush().color() == self.colors['current']:
            u_vertex.set_color(self.colors['visited'])
        if v_vertex.brush().color() == self.colors['current']:
            v_vertex.set_color(self.colors['visited'])
        self.graph_canvas.scene.update()

    def _reconstruct_path(self):
        """Reconstruct the shortest path from start to end"""
        if self.distances[self.end_vertex] == float('inf'):
            return None
        
        path = []
        current = self.end_vertex
        
        while current is not None:
            path.append(current)
            current = self.previous[current]
        
        path.reverse()
        return path if path[0] == self.start_vertex else None

    def cleanup(self):
        """Clean up the animator"""
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        self.animation_queue.clear()
        self.algorithm_completed = False

    def run(self, start_vertex, end_vertex):
        """Run the Bellman-Ford algorithm"""
        self.start(start_vertex, end_vertex)

def run_bellman_ford(graph_matrices: GraphMatrices, graph_canvas, start_vertex=None, end_vertex=None):
    """Run Bellman-Ford algorithm with animation"""
    animator = BellmanFordAnimator(graph_matrices, graph_canvas)
    
    if not graph_matrices.vertices:
        QMessageBox.warning(graph_canvas, "Bellman-Ford", "Le graphe est vide.")
        return None

    if start_vertex and end_vertex:
        animator.run(start_vertex, end_vertex)
        return animator
    else:
        # Ask user to click on two vertices
        QMessageBox.information(graph_canvas, "Bellman-Ford", "Cliquez sur le sommet de départ.")
        selection = {'start': None, 'end': None}

        def on_first_click(vertex):
            selection['start'] = vertex
            graph_canvas.vertex_clicked.disconnect(on_first_click)
            vertex.set_color(QColor(255, 255, 0))  # Yellow for start
            graph_canvas.scene.update()
            QMessageBox.information(graph_canvas, "Bellman-Ford", "Cliquez sur le sommet d'arrivée.")
            graph_canvas.vertex_clicked.connect(on_second_click)

        def on_second_click(vertex):
            selection['end'] = vertex
            graph_canvas.vertex_clicked.disconnect(on_second_click)
            vertex.set_color(QColor(255, 0, 255))  # Magenta for end
            graph_canvas.scene.update()
            
            if selection['start'] == selection['end']:
                QMessageBox.information(graph_canvas, "Bellman-Ford", 
                                      "Le sommet de départ et d'arrivée est le même. Distance : 0")
                animator.reset_colors()
                return
            
            animator.run(selection['start'], selection['end'])

        graph_canvas.vertex_clicked.connect(on_first_click)
        return animator