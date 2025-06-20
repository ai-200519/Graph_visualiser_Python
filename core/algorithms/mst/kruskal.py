from PyQt5.QtGui import QColor, QPen
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
from ui.edge_item import EdgeItem

class KruskalVisualizer:
    COLORS = {
        'default': QColor(200, 200, 200),      # Gris pour sommets/arêtes non MST
        'mst_edge': QColor(0, 255, 0),         # Vert vif pour arêtes du MST
        'mst_vertex': QColor(255, 215, 0),     # Or pour sommets du MST
        'current': QColor(255, 0, 0)           # Rouge pour le sommet/arête en cours de traitement
    }

    def __init__(self, m, c):
        self.m = m  # matrices
        self.c = c  # canvas
        self.t = QTimer()
        self.t.timeout.connect(self._v)
        self.cleanup()  # Initialiser/réinitialiser l'état

    def cleanup(self):
        """Nettoie l'état de l'algorithme"""
        if hasattr(self, 't') and self.t.isActive():
            self.t.stop()
        self.q = []
        self.mst_weight = 0
        self.mst_vertices = set()
        self.mst_edges = set()
        self.algorithm_finished = False

    def find(self, p, i):
        if p[i] != i:
            p[i] = self.find(p, p[i])
        return p[i]

    def union(self, p, r, x, y):
        rx, ry = self.find(p, x), self.find(p, y)
        if rx == ry:
            return False
        if r[rx] < r[ry]:
            p[rx] = ry
        elif r[rx] > r[ry]:
            p[ry] = rx
        else:
            p[ry], r[rx] = rx, r[rx] + 1
        return True

    def reset_colors(self):
        """Reset all colors to default"""
        for vertex in self.m.vertices:
            vertex.set_color(self.COLORS['default'])
        for item in self.c.scene.items():
            if isinstance(item, EdgeItem):
                item.setPen(QPen(self.COLORS['default'], 2))

    def check_connectivity(self):
        """Vérifie si le MST couvre tous les sommets"""
        if len(self.mst_vertices) < len(self.m.vertices):
            QMessageBox.warning(self.c, "Attention", 
                "Le graphe n'est pas connexe. L'arbre couvrant minimal n'existe pas.")
            return False
        return True

    def kruskal(self):
        n = len(self.m.adjacency_matrix)
        if n == 0:
            QMessageBox.warning(self.c, "Erreur", "Le graphe est vide.")
            return
        if n == 1:
            QMessageBox.information(self.c, "Kruskal", "Le graphe n'a qu'un sommet. Poids total : 0")
            return

        # Vérifier les poids négatifs
        for i in range(n):
            for j in range(n):
                if self.m.adjacency_matrix[i][j] < 0:
                    QMessageBox.warning(self.c, "Erreur", "Le graphe contient des poids négatifs.")
                    return

        self.cleanup()  # Réinitialiser l'état
        self.reset_colors()
        
        # Liste des arêtes (poids, sommet1, sommet2)
        try:
            e = [(w, i, j) for i in range(n) for j in range(i+1, n)
                 if (w := self.m.adjacency_matrix[i][j]) > 0]
            e.sort()
            p, r = list(range(n)), [0] * n
            for w, u, v in e:
                if self.union(p, r, u, v):
                    self.q.append(('e', u, v, w))
            self.t.start(500)
        except Exception as e:
            QMessageBox.critical(self.c, "Erreur", f"Erreur lors de l'initialisation de Kruskal : {str(e)}")
            self.cleanup()

    def _v(self):
        try:
            if not self.q:
                self.t.stop()
                self.algorithm_finished = True
                self.apply_final_colors()
                if self.check_connectivity():
                    QMessageBox.information(self.c, "Kruskal", 
                        f"Poids total de l'arbre couvrant minimal : {self.mst_weight}")
                return

            _, u, v, w = self.q.pop(0)
            edge = None
            vertex_u = self.m.vertices[u]
            vertex_v = self.m.vertices[v]

            for item in self.c.scene.items():
                if hasattr(item, 'source') and hasattr(item, 'target'):
                    if (item.source == vertex_u and item.target == vertex_v) or \
                       (item.source == vertex_v and item.target == vertex_u):
                        edge = item
                        break

            # Colorer temporairement en rouge (traitement en cours)
            if edge:
                edge.setPen(QPen(self.COLORS['current'], 2))
            vertex_u.set_color(self.COLORS['current'])
            vertex_v.set_color(self.COLORS['current'])

            # Attendre un peu avant de mettre la couleur finale
            QTimer.singleShot(250, lambda: self.confirm_edge(edge, vertex_u, vertex_v, w))
        except Exception as e:
            self.t.stop()
            QMessageBox.critical(self.c, "Erreur", f"Erreur lors de l'exécution de Kruskal : {str(e)}")
            self.cleanup()

    def confirm_edge(self, edge, vertex_u, vertex_v, w):
        """Confirme l'ajout d'une arête au MST avec les couleurs finales"""
        try:
            if edge:
                edge.setPen(QPen(self.COLORS['mst_edge'], 2))
                self.mst_edges.add(tuple(sorted([vertex_u.label, vertex_v.label])))
            self.mst_weight += w

            vertex_u.set_color(self.COLORS['mst_vertex'])
            vertex_v.set_color(self.COLORS['mst_vertex'])
            self.mst_vertices.add(vertex_u)
            self.mst_vertices.add(vertex_v)
        except Exception as e:
            self.t.stop()
            QMessageBox.critical(self.c, "Erreur", f"Erreur lors de la confirmation d'une arête : {str(e)}")
            self.cleanup()

    def apply_final_colors(self):
        """Applique les couleurs finales après la fin de l'algorithme"""
        try:
            # Colorer tous les sommets et arêtes non-MST en gris
            for vertex in self.m.vertices:
                if vertex not in self.mst_vertices:
                    vertex.set_color(self.COLORS['default'])
                else:
                    vertex.set_color(self.COLORS['mst_vertex'])

            for item in self.c.scene.items():
                if isinstance(item, EdgeItem):
                    edge_tuple = tuple(sorted([item.source.label, item.target.label]))
                    if edge_tuple not in self.mst_edges:
                        item.setPen(QPen(self.COLORS['default'], 2))
                    else:
                        item.setPen(QPen(self.COLORS['mst_edge'], 2))
        except Exception as e:
            QMessageBox.critical(self.c, "Erreur", f"Erreur lors de l'application des couleurs finales : {str(e)}")

def run_kruskal(m, c, start_vertex=None):
    animator = KruskalVisualizer(m, c)
    if start_vertex:
        animator.kruskal()
        return animator
    else:
        parent = c.parent if hasattr(c, 'parent') else c
        QMessageBox.information(parent, "Kruskal", "Cliquez sur un sommet pour commencer Kruskal.")
        def on_vertex_click(vertex):
            c.vertex_clicked.disconnect(on_vertex_click)
            animator.kruskal()
        c.vertex_clicked.connect(on_vertex_click)
        return animator