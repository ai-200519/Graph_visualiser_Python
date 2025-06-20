import heapq
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QMessageBox
from core.matrices.graph_matrices import GraphMatrices
from ui.edge_item import EdgeItem

class PrimVisualizer:
    COLORS = {
        'default': QColor(200, 200, 200),
        'mst_edge': QColor(0, 255, 0),
        'mst_vertex': QColor(255, 215, 0),
        'current': QColor(255, 0, 0)
    }

    def __init__(self, matrices, canvas):
        self.m = matrices
        self.c = canvas
        self.t = QTimer()
        self.t.timeout.connect(self._step)
        self.cleanup()

    def cleanup(self):
        if hasattr(self, 't') and self.t.isActive():
            self.t.stop()
        self.q = []
        self.total_weight = 0
        self.mst_vertices = set()
        self.mst_edges = set()
        self.algorithm_finished = False

    def reset_colors(self):
        for vertex in self.m.vertices:
            vertex.set_color(self.COLORS['default'])
        for item in self.c.scene.items():
            if isinstance(item, EdgeItem):
                item.setPen(QPen(self.COLORS['default'], 2))

    def check_connectivity(self):
        """Vérifie si le MST couvre tous les sommets du graphe."""
        if len(self.mst_vertices) < len(self.m.vertices):
            QMessageBox.warning(self.c, "Graphe non connexe",
                                "L'algorithme a trouvé un arbre couvrant minimal pour une composante du graphe, mais le graphe entier n'est pas connexe.")
            return False
        return True

    def start(self, start_vertex):
        n = len(self.m.adjacency_matrix)
        if n == 0:
            QMessageBox.warning(self.c, "Erreur", "Le graphe est vide.")
            return
        if n == 1:
            QMessageBox.information(self.c, "Prim", "Le graphe n'a qu'un sommet. Poids total : 0")
            return

        self.cleanup()
        self.reset_colors()

        start_idx = self.m.vertex_indices.get(start_vertex)
        if start_idx is None:
            QMessageBox.critical(self.c, "Erreur", "Le sommet de départ est invalide.")
            return

        try:
            key = [float('inf')] * n
            parent = [-1] * n
            in_mst = [False] * n
            
            pq = [(0, start_idx)]
            key[start_idx] = 0

            while pq:
                weight, u_idx = heapq.heappop(pq)

                if in_mst[u_idx]:
                    continue
                
                in_mst[u_idx] = True
                
                self.q.append(('visit', u_idx, parent[u_idx], key[u_idx]))

                for v_idx, edge_weight in enumerate(self.m.adjacency_matrix[u_idx]):
                    if not in_mst[v_idx] and edge_weight > 0 and key[v_idx] > edge_weight:
                        key[v_idx] = edge_weight
                        parent[v_idx] = u_idx
                        heapq.heappush(pq, (key[v_idx], v_idx))
            
            self.t.start(500)
        except Exception as e:
            QMessageBox.critical(self.c, "Erreur", f"Une erreur est survenue lors de l'initialisation de Prim : {e}")
            self.cleanup()

    def _step(self):
        try:
            if not self.q:
                self.t.stop()
                self.algorithm_finished = True
                self.apply_final_colors()
                if self.check_connectivity():
                    QMessageBox.information(self.c, "Prim", f"Poids total de l'arbre couvrant minimal : {self.total_weight}")
                return

            step_type, u_idx, p_idx, weight = self.q.pop(0)
            
            vertex_u = self.m.vertices[u_idx]
            vertex_u.set_color(self.COLORS['current'])
            
            edge_to_color = None
            if p_idx != -1:
                vertex_p = self.m.vertices[p_idx]
                for item in self.c.scene.items():
                    if isinstance(item, EdgeItem):
                        if (item.source == vertex_p and item.target == vertex_u) or \
                           (item.source == vertex_u and item.target == vertex_p):
                            edge_to_color = item
                            edge_to_color.setPen(QPen(self.COLORS['current'], 2))
                            break

            QTimer.singleShot(250, lambda: self.confirm_step(vertex_u, p_idx, edge_to_color, weight))
        except Exception as e:
            QMessageBox.critical(self.c, "Erreur", f"Une erreur est survenue pendant l'animation de Prim : {e}")
            self.cleanup()

    def confirm_step(self, vertex_u, p_idx, edge, weight):
        try:
            vertex_u.set_color(self.COLORS['mst_vertex'])
            self.mst_vertices.add(vertex_u)
            
            if edge:
                vertex_p = self.m.vertices[p_idx]
                edge.setPen(QPen(self.COLORS['mst_edge'], 2))
                self.mst_edges.add(tuple(sorted((vertex_p.label, vertex_u.label))))
                self.total_weight += weight
        except Exception as e:
            QMessageBox.critical(self.c, "Erreur", f"Une erreur est survenue lors de la confirmation d'une étape : {e}")
            self.cleanup()

    def apply_final_colors(self):
        try:
            for vertex in self.m.vertices:
                if vertex not in self.mst_vertices:
                    vertex.set_color(self.COLORS['default'])
            
            for item in self.c.scene.items():
                if isinstance(item, EdgeItem):
                    edge_tuple = tuple(sorted((item.source.label, item.target.label)))
                    if edge_tuple not in self.mst_edges:
                        item.setPen(QPen(self.COLORS['default'], 2))
        except Exception as e:
            QMessageBox.critical(self.c, "Erreur", f"Une erreur est survenue lors de la coloration finale : {e}")

def run_prim(matrices: GraphMatrices, canvas):
    animator = PrimVisualizer(matrices, canvas)

    # Vérifier les poids négatifs
    for row in matrices.adjacency_matrix:
        for weight in row:
            if weight < 0:
                QMessageBox.critical(canvas, "Erreur Prim", "L'algorithme de Prim ne supporte pas les poids négatifs.")
                return None

    QMessageBox.information(canvas, "Prim", "Cliquez sur un sommet pour commencer l'algorithme de Prim.")
    
    def on_vertex_click(vertex):
        canvas.vertex_clicked.disconnect(on_vertex_click)
        animator.start(vertex)
    
    canvas.vertex_clicked.connect(on_vertex_click)
    return animator
