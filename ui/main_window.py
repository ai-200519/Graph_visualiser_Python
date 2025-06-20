from PyQt5.QtWidgets import (
    QMainWindow, QToolBar, QAction, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLabel, QComboBox, QMessageBox, QDialog, QInputDialog, QMenu
)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt, QSize
from ui.toolbar import ToolBar
from ui.graph_canvas import GraphCanvas
from ui.matrix_dialog import MatrixDialog
from core.matrices import GraphMatrices
from core.algorithms.traversal.bfs import run_bfs
from core.algorithms.traversal.dfs import run_dfs
from core.algorithms.coloring.greedy_coloring import run_greedy_coloring
from core.algorithms.coloring.welsh_powell import run_welsh_powell
from core.algorithms.shortest_path.dijkstra import run_dijkstra
from core.algorithms.shortest_path.bellman_ford import run_bellman_ford
from core.algorithms.mst.prim import run_prim
from core.algorithms.mst.kruskal import run_kruskal
from core.algorithms.flow.ford_fulkerson import run_ford_fulkerson

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Visualizer")
        self.setGeometry(100, 100, 1000, 700)

        # Initialiser le mode par défaut
        self.current_mode = "DEFAULT"

        # Créer les widgets
        self.toolbar = ToolBar()
        self.canvas = GraphCanvas(self)

        # Connecter les boutons à la méthode de changement de mode
        self.toolbar.default_btn.clicked.connect(lambda: self.set_mode("DEFAULT"))
        self.toolbar.add_vertex_btn.clicked.connect(lambda: self.set_mode("ADD_VERTEX"))
        self.toolbar.connect_btn.clicked.connect(lambda: self.set_mode("CONNECT"))
        self.toolbar.remove_btn.clicked.connect(lambda: self.set_mode("REMOVE"))
        self.toolbar.algo_btn.clicked.connect(lambda: self.set_mode("ALGORITHMS"))
        self.toolbar.reset_btn.clicked.connect(lambda: self.set_mode("RESET GRAPH"))

        # Connecter le bouton de réinitialisation à la méthode de réinitialisation
        self.toolbar.reset_btn.clicked.connect(self.canvas.reset_graph)

        # Connect matrices button
        self.toolbar.matrices_btn.clicked.connect(self.show_matrices)

        # Connecter les boutons de la barre d'outils des algorithmes pour afficher les menus
        self.toolbar.algorithm_toolbar.traversal_btn.clicked.connect(self.show_traversal_algorithms)
        self.toolbar.algorithm_toolbar.coloring_btn.clicked.connect(self.show_coloring_algorithms)
        self.toolbar.algorithm_toolbar.mst_btn.clicked.connect(self.show_mst_algorithms)
        self.toolbar.algorithm_toolbar.shortest_path_btn.clicked.connect(self.show_shortest_path_algorithms)
        self.toolbar.algorithm_toolbar.flow_btn.clicked.connect(self.show_flow_algorithms)
        self.toolbar.algorithm_toolbar.back_btn.clicked.connect(lambda: self.set_mode("DEFAULT"))

        # Layout principal
        central_widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def set_mode(self, mode):
        """Set the current mode and update the UI."""
        self.current_mode = mode
        print(f"Mode actuel : {mode}")
        self.canvas.set_mode(mode)

        if mode == "ALGORITHMS":
            self.toolbar.switch_to_algorithm_toolbar()
        else:
            self.toolbar.switch_to_main_toolbar()

    def show_traversal_algorithms(self):
        """Show traversal algorithms menu."""
        menu = QMenu(self)
        bfs_action = menu.addAction("BFS")
        dfs_action = menu.addAction("DFS")
        
        action = menu.exec_(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))
        if action == bfs_action:
            self.canvas.set_mode("TRAVERSAL")
            self.run_algorithm("TRAVERSAL", "BFS")
        elif action == dfs_action:
            self.canvas.set_mode("TRAVERSAL")
            self.run_algorithm("TRAVERSAL", "DFS")

    def show_coloring_algorithms(self):
        """Show coloring algorithms menu."""
        menu = QMenu(self)
        greedy_action = menu.addAction("Greedy Coloring")
        welsh_powell_action = menu.addAction("Welsh-Powell")
        
        action = menu.exec_(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))
        if action == greedy_action:
            self.canvas.set_mode("COLORING")
            self.run_algorithm("COLORING", "Greedy Coloring")
        elif action == welsh_powell_action:
            self.canvas.set_mode("COLORING")
            self.run_algorithm("COLORING", "Welsh-Powell")

    def show_mst_algorithms(self):
        """Show MST algorithms menu."""
        menu = QMenu(self)
        prim_action = menu.addAction("Prim")
        kruskal_action = menu.addAction("Kruskal")
        
        action = menu.exec_(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))
        if action == prim_action:
            self.canvas.set_mode("MST")
            self.run_algorithm("MST", "Prim")
        elif action == kruskal_action:
            self.canvas.set_mode("MST")
            self.run_algorithm("MST", "Kruskal")            

    def show_shortest_path_algorithms(self):
        """Show shortest path algorithms menu."""
        menu = QMenu(self)
        dijkstra_action = menu.addAction("Dijkstra")
        bellman_ford_action = menu.addAction("Bellman-Ford")
        
        action = menu.exec_(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))
        if action == dijkstra_action:
            self.canvas.set_mode("SHORTEST_PATH")
            self.run_algorithm("SHORTEST_PATH", "Dijkstra")
        elif action == bellman_ford_action:
            self.canvas.set_mode("SHORTEST_PATH")
            self.run_algorithm("SHORTEST_PATH", "Bellman-Ford")

    def show_flow_algorithms(self):
        """Show flow algorithms menu."""
        menu = QMenu(self)
        ford_fulkerson_action = menu.addAction("Ford-Fulkerson")
        
        action = menu.exec_(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))
        if action == ford_fulkerson_action:
            self.canvas.set_mode("FLOW")
            self.run_algorithm("FLOW", "Ford-Fulkerson")

    def run_algorithm(self, category: str, algorithm: str):
        """Run the selected algorithm."""
        if category == "TRAVERSAL":
            if not self.canvas.matrices.vertices:
                QMessageBox.warning(self, "Erreur", "Aucun sommet dans le graphe.")
                return
            if algorithm == "BFS":
                self.bfs_animator = run_bfs(self.canvas.matrices, self.canvas)
            elif algorithm == "DFS":
                self.dfs_animator = run_dfs(self.canvas.matrices, self.canvas)
        elif category == "COLORING":
            if algorithm == "Greedy Coloring":
                run_greedy_coloring(self.canvas.matrices, self.canvas)
            elif algorithm == "Welsh-Powell":
                run_welsh_powell(self.canvas.matrices, self.canvas)
        elif category == "SHORTEST_PATH":
            if algorithm == "Dijkstra":
                self.dijkstra_animator = run_dijkstra(self.canvas.matrices, self.canvas)
            elif algorithm == "Bellman-Ford":
                run_bellman_ford(self.canvas.matrices, self.canvas)
        elif category == "MST":
            # Vérifier si le graphe est non orienté pour les deux
            for edge in self.canvas.edges:
                if hasattr(edge[2], 'is_directed') and edge[2].is_directed:
                    QMessageBox.warning(self, "Erreur", "L'algorithme MST nécessite un graphe non orienté.")
                    return
            if algorithm == "Prim":
                self.prim_animator = run_prim(self.canvas.matrices, self.canvas)
            elif algorithm == "Kruskal":
                self.kruskal_animator = run_kruskal(self.canvas.matrices, self.canvas)
        elif category == "FLOW":
            if algorithm == "Ford-Fulkerson":
                run_ford_fulkerson(self.canvas.matrices, self.canvas)

    def get_vertex_naming_mode(self):
        return self.toolbar.get_naming_mode()

    def show_matrices(self):
        """Show the graph matrices dialog."""
        dialog = MatrixDialog(self.canvas, self)
        dialog.exec_()

    def create_algorithm_toolbar(self):
        """Create the algorithm toolbar."""
        algorithm_toolbar = QToolBar("Algorithmes")
        algorithm_toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(algorithm_toolbar)

        # Traversal algorithms
        traversal_btn = QPushButton("Run Traversal")
        traversal_btn.clicked.connect(self.show_traversal_algorithms)
        algorithm_toolbar.addWidget(traversal_btn)

        # Coloring algorithms
        coloring_btn = QPushButton("Run Coloration")
        coloring_btn.clicked.connect(self.show_coloring_algorithms)
        algorithm_toolbar.addWidget(coloring_btn)

        # Shortest path algorithms
        shortest_path_btn = QPushButton("Run Plus court chemin")
        shortest_path_btn.clicked.connect(self.show_shortest_path_algorithms)
        algorithm_toolbar.addWidget(shortest_path_btn)

        # MST algorithms
        mst_btn = QPushButton("Run MST")
        mst_btn.clicked.connect(self.show_mst_algorithms)
        algorithm_toolbar.addWidget(mst_btn)

        # Flow algorithms
        flow_btn = QPushButton("Run Flot")
        flow_btn.clicked.connect(self.show_flow_algorithms)
        algorithm_toolbar.addWidget(flow_btn)
