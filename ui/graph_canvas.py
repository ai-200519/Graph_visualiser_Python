from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, QInputDialog, QMessageBox, QDialog
)
from PyQt5.QtGui import QBrush, QPen, QPainterPath, QPolygonF, QTransform, QPainter
from PyQt5.QtCore import Qt, QPointF, QLineF, pyqtSignal
from ui.vertex_item import VertexItem
from ui.edge_input_dialog import EdgeInputDialog
from ui.edge_item import EdgeItem
from core.matrices import GraphMatrices
from core.algorithms.mst.prim import run_prim
from core.algorithms.mst.kruskal import run_kruskal



class GraphCanvas(QGraphicsView):
    # Signal emitted when a vertex is clicked
    vertex_clicked = pyqtSignal(VertexItem)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setStyleSheet("background-color: white;")
        self.mode = "DEFAULT"
        self.selected_vertex = None
        self.edges = []  # Liste d'arêtes : (source, target, line, text)

        self.vertex_count = 0

        # Initialize graph matrices
        self.matrices = GraphMatrices()

        # Zoom settings
        self.scale_factor = 1.0
        self.min_scale = 0.1
        self.max_scale = 5.0
        self.zoom_factor = 1.15  # How much to zoom in/out per step

        # Enable mouse tracking for better interaction
        self.setMouseTracking(True)

        # Set rendering hints for better quality
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

        # Set drag mode for panning
        self.setDragMode(QGraphicsView.ScrollHandDrag)


    def set_mode(self, mode):
        self.mode = mode
        print(f"[Canvas] Mode mis à jour : {self.mode}")
        # Reset selection when changing modes
        self.reset_selection()

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            pos = self.mapToScene(event.pos())
            clicked_vertex = None

            # Check if a vertex was clicked
            for item in self.scene.items():
                if isinstance(item, VertexItem) and item.contains(item.mapFromScene(pos)):
                    clicked_vertex = item
                    break

            if clicked_vertex:
                if self.mode in ["DIJKSTRA", "BELLMAN_FORD", "TRAVERSAL", "COLORING", "MST", "FLOW", "ALGORITHMS", "SHORTEST_PATH"]:
                    # Emit signal for all algorithm modes
                    print(f"[Canvas] Sommet {clicked_vertex.label} cliqué en mode {self.mode}")
                    self.vertex_clicked.emit(clicked_vertex)
                elif self.mode == "CONNECT":
                    self.handle_vertex_selection(clicked_vertex)
                elif self.mode == "REMOVE":
                    self.remove_vertex(clicked_vertex)
                elif self.mode == "DEFAULT":
                    # Allow default behavior for selecting and moving items
                    super().mousePressEvent(event)
            else:
                # Si on n'a pas cliqué sur un sommet existant
                if self.mode == "ADD_VERTEX":
                    # Ajouter un nouveau sommet à la position du clic
                    self.add_vertex(pos.x(), pos.y())
                else:
                    # Pour les autres modes, permettre le comportement par défaut
                    super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def handle_vertex_selection(self, vertex):
        # Réinitialiser la couleur de tous les sommets non sélectionnés
        for item in self.scene.items():
            if isinstance(item, VertexItem) and item != self.selected_vertex:
                item.setBrush(QBrush(Qt.yellow))

        if self.selected_vertex is None:
            # Le premier sommet est selectionné
            self.selected_vertex = vertex
            vertex.setBrush(QBrush(Qt.cyan))
            print(f"[Canvas] Sommet sélectionné : {vertex.label}")
        else:
            if self.selected_vertex == vertex:
                # pour self-loop
                # Créer une boucle entre le même sommet
                print("[Canvas] Même sommet sélectionné deux fois — création d'une boucle.")
                dialog = EdgeInputDialog(self)
                if dialog.exec_() == QDialog.Accepted:
                    weight, directed = dialog.get_input()
                    if self.edge_exists(self.selected_vertex, self.selected_vertex, directed=directed):
                        print(f"[Canvas] Une boucle existe déjà sur le sommet '{self.selected_vertex.label}'.")
                        QMessageBox.warning(
                            self,
                            "Boucle existante",
                            f"Une boucle existe déjà sur le sommet '{self.selected_vertex.label}'."
                        )
                    else:
                        self.create_edge(self.selected_vertex, self.selected_vertex, weight, directed=True, is_self_loop=True)
                else:
                    print("[Canvas] Création de boucle annulée par l'utilisateur.")

            else:
                # Vérifier si une arête existe déjà
                dialog = EdgeInputDialog(self)
                if dialog.exec_() == QDialog.Accepted:
                    weight, directed = dialog.get_input()
                    if self.edge_exists(self.selected_vertex, vertex, directed=directed):
                        print("[Canvas] Arête déjà existante entre ces deux sommets.")
                        QMessageBox.warning(
                            self,
                            "Arête existante",
                            f"Une arête existe déjà entre '{self.selected_vertex.label}' et '{vertex.label}'."
                        )
                    else:
                        # creation d'un new arrete
                        self.create_edge(self.selected_vertex, vertex, weight, directed, is_self_loop=False)
                else:  
                    print("[Canvas] Création d'arête annulée par l'utilisateur.")
            # Reset the selection
            self.reset_selection()

    def create_edge(self, source, target, weight, directed, is_self_loop=False):
        """Create an edge between two vertices."""

        if not self.is_valid_weight(weight):
            weight = ""
        else:
            # Convert weight to float for matrices
            weight_value = float(weight)

        # Draw the edge
        self.draw_edge(source, target, weight, directed)

        # Update matrices with the new edge
        if weight:
            self.matrices.add_edge(source, target, weight_value, directed)
        else:
            self.matrices.add_edge(source, target, 1, directed)  # Default weight is 1

        if is_self_loop:
            print(f"[Canvas] Création d'une boucle entre {source.label} et lui-même, poids = '{weight}', orientée = {directed}.")
        else:
            print(f"[Canvas] Création d'une arête entre {source.label} et {target.label}, poids = '{weight}', orientée = {directed}.")

    def reset_selection(self):
        """Reset the selection of vertices."""
        if self.selected_vertex:
            self.selected_vertex.setBrush(QBrush(Qt.yellow))
        self.selected_vertex = None        

    def is_valid_weight(self, weight):
        """Check if the weight is a valid number."""
        try:
            float(weight)  # Try converting the weight to a float
            return True
        except ValueError:
            return False

    def remove_edge_by_line(self, line_item):
        for edge in self.edges:
            if edge[2] == line_item:
                source, target = edge[0], edge[1]
                print(f"[Canvas] Suppression de l'arête entre {edge[0].label} et {edge[1].label}")

                # Determine if the edge is directed
                directed = target in source.successors and source in target.predecessors

                # Update matrices
                self.matrices.remove_edge(source, target, directed)

                # Update successors and predecessors
                if target in source.successors:
                    source.successors.remove(target)
                if source in target.predecessors:
                    target.predecessors.remove(source)
                if target in source.voisins:
                    source.voisins.remove(target)
                if source in target.voisins:
                    target.voisins.remove(source)

                # Remove the line and text
                self.scene.removeItem(edge[2])  # ligne
                if edge[3]:
                    self.scene.removeItem(edge[3])  # texte
                self.edges.remove(edge)
                break

    def remove_vertex_edges(self, vertex):
        # Update matrices - remove the vertex
        self.matrices.remove_vertex(vertex)

        edges_to_remove = [edge for edge in self.edges if edge[0] == vertex or edge[1] == vertex]
        for edge in edges_to_remove:
            source, target = edge[0], edge[1]        
            print(f"[Canvas] Removing edge between {edge[0].label} and {edge[1].label}")

            # Update successors and predecessors
            if target in source.successors:
                source.successors.remove(target)
            if source in target.predecessors:
                target.predecessors.remove(source)  
            if target in source.voisins:
                source.voisins.remove(target)
            if source in target.voisins:
                target.voisins.remove(source)


            self.scene.removeItem(edge[2])  # Remove the line
            if edge[3]:
                self.scene.removeItem(edge[3])  # Remove the weight text
            self.edges.remove(edge)

    def add_vertex(self, x, y):
        naming_mode = self.parent.get_vertex_naming_mode()
        radius = 20

        if naming_mode == "Custom":
            label, ok = QInputDialog.getText(self, "Nom du sommet", "Entrez le nom du sommet :")
            if not ok or not label.strip():
                print("[Canvas] Ajout annulé (aucun nom entré)")
                return
        else:
            self.vertex_count += 1
            label = str(self.vertex_count)

        vertex = VertexItem(x, y, radius, label.strip())
        self.scene.addItem(vertex)

        # Update matrices
        self.matrices.add_vertex(vertex)

        print(f"[Canvas] Sommet ajouté : {label} en ({x:.1f}, {y:.1f})")

    def draw_edge(self, source, target, weight, directed=False):
        """Draw an edge between two vertices with optional weight and direction."""
        # Check if a directed edge already exists in the opposite direction
        is_curvy = directed and any(s == target and t == source for s, t, _, _ in self.edges)

        #Creer une ligne entre les deux sommets
        edge = EdgeItem (source, target, radius=source.radius, directed=directed, is_curvy=is_curvy)
        self.scene.addItem(edge)
        #update les voisins
        if target not in source.voisins:
            source.voisins.append(target)
        if source not in target.voisins:
            target.voisins.append(source)       
        # Ajouter le poids text
        if weight.strip():
            p1 = source.sceneBoundingRect().center()
            p2 = target.sceneBoundingRect().center()
            if source == target:
                # position weight text for self-loops
                loop_radius = source.radius + 10  # Adjust the radius to start outside the vertex
                mx, my = p1.x() + loop_radius, p1.y() - loop_radius - 10  # Adjust position above the loop
            elif is_curvy:
                control_x = (p1.x() + p2.x()) / 2 + 40
                control_y = (p1.y() + p2.y()) / 2 - 40
                mx, my = control_x, control_y - 10            
            else:
                # Position weight text for regular edges
                mx, my = (p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2 - 10  # Adjust position above the line

            # Create the text item
            text = QGraphicsTextItem(weight)
            text.setDefaultTextColor(Qt.red)
            text.setZValue(2)  # Ensure text is above the line
            text.setPos(mx - text.boundingRect().width() / 2, my - text.boundingRect().height() / 2)
            self.scene.addItem(text)
        else:
            text = None

        # Store the edge information
        self.edges.append((source, target, edge, text))
        print(f"[Canvas] Arête créée entre {source.label} et {target.label}, poids = '{weight}', orientée = {directed}")

    def edge_exists(self, v1, v2, directed=False):
        for source, target, edge_item, _ in self.edges:
            if directed:
                # Check for a directed edge
                if source == v1 and target == v2:
                    print(f"[Canvas] Directed edge already exists from {v1.label} to {v2.label}.")
                    return True
            else:
                # Check for an undirected edge
                if (source == v1 and target == v2) or (source == v2 and target == v1):
                    print(f"[Canvas] Undirected edge already exists between {v1.label} and {v2.label}.")
                    return True
        return False

    def update_edges(self, moved_vertex):
        """Update the positions of edges connected to the moved vertex."""
        for source, target, edge, text in self.edges:
            if source == moved_vertex or target == moved_vertex:
                edge.update_path()  # Update the edge path
            if text:
                # Update the position of the weight text
                p1 = source.sceneBoundingRect().center()
                p2 = target.sceneBoundingRect().center()
                if source == target:
                    # Update weight text for self-loops
                    loop_radius = source.radius + 10
                    mx, my = p1.x() + loop_radius, p1.y() - loop_radius - 10
                elif edge.is_curvy:
                    # Update weight text for curvy edges
                    control_x = (p1.x() + p2.x()) / 2 + 40
                    control_y = (p1.y() + p2.y()) / 2 - 40
                    mx, my = control_x, control_y - 10        
                else:
                    # Update weight text for regular edges
                    mx, my = (p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2 - 10
                text.setPos(mx - text.boundingRect().width() / 2, my - text.boundingRect().height() / 2)              

    def reset_graph(self):
        """Reset the graph and Clear the canvas."""
        self.scene.clear() # Clear the scene
        self.edges = [] # Reset the edges list 
        self.vertex_count = 0 #Reset the vertex counter
        self.selected_vertex = None # Reset the selected vertex
        self.mode = "DEFAULT"   # Reset the mode to default

        # Reset matrices
        self.matrices.reset()

        for item in self.scene.items():
            if isinstance(item, VertexItem):
                item.successors = []
                item.predecessors = []
                item.voisins = []

        print("[Canvas] Graph cleared and reset.")

    def clear(self):
        self.scene.clear()

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        # Get the mouse position before scaling
        old_pos = self.mapToScene(event.pos())

        # Determine zoom direction
        zoom_in = event.angleDelta().y() > 0

        # Calculate new scale factor
        if zoom_in:
            new_scale = self.scale_factor * self.zoom_factor
        else:
            new_scale = self.scale_factor / self.zoom_factor

        # Enforce scale limits
        new_scale = max(self.min_scale, min(new_scale, self.max_scale))

        # Only proceed if scale changed
        if new_scale != self.scale_factor:
            # Update scale factor
            self.scale_factor = new_scale

            # Apply the transformation
            self.setTransform(QTransform().scale(self.scale_factor, self.scale_factor))

            # Get the new position after scaling
            new_pos = self.mapToScene(event.pos())

            # Calculate the delta and adjust the view
            delta = new_pos - old_pos
            self.translate(delta.x(), delta.y())

            print(f"[Canvas] Zoom level: {self.scale_factor:.2f}")

    def reset_zoom(self):
        """Reset zoom to original scale."""
        self.scale_factor = 1.0
        self.setTransform(QTransform())
        print("[Canvas] Zoom reset to 1.0")

    def zoom_in(self):
        """Zoom in by one step."""
        new_scale = self.scale_factor * self.zoom_factor
        new_scale = min(new_scale, self.max_scale)
        if new_scale != self.scale_factor:
            self.scale_factor = new_scale
            self.setTransform(QTransform().scale(self.scale_factor, self.scale_factor))
            print(f"[Canvas] Zoomed in: {self.scale_factor:.2f}")

    def zoom_out(self):
        """Zoom out by one step."""
        new_scale = self.scale_factor / self.zoom_factor
        new_scale = max(new_scale, self.min_scale)
        if new_scale != self.scale_factor:
            self.scale_factor = new_scale
            self.setTransform(QTransform().scale(self.scale_factor, self.scale_factor))
            print(f"[Canvas] Zoomed out: {self.scale_factor:.2f}")

    # Matrix access methods
    def get_adjacency_matrix(self):
        """Get the adjacency matrix."""
        return self.matrices.get_adjacency_matrix()

    def get_incidence_matrix(self):
        """Get the incidence matrix."""
        return self.matrices.get_incidence_matrix()

    def get_distance_matrix(self):
        """Get the distance matrix."""
        return self.matrices.get_distance_matrix()

    def get_vertex_labels(self):
        """Get the labels of all vertices."""
        return self.matrices.get_vertex_labels()

    def get_edge_labels(self):
        """Get the labels of all edges."""
        return self.matrices.get_edge_labels()

    def get_matrices_string(self):
        """Get a string representation of all matrices."""
        return str(self.matrices)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            self.zoom_in()
        elif event.key() == Qt.Key_Minus:
            self.zoom_out()
        elif event.key() == Qt.Key_0:
            self.reset_zoom()
        else:
            # Pass other key events to the parent class
            super().keyPressEvent(event)

    def remove_vertex(self, vertex):
        """Remove a vertex and all its connected edges."""
        print(f"[Canvas] Suppression du sommet {vertex.label}")
        
        # Remove all edges connected to this vertex
        self.remove_vertex_edges(vertex)
        
        # Remove the vertex from the scene
        self.scene.removeItem(vertex)
        
        # Update matrices
        self.matrices.remove_vertex(vertex)
        
        # Reset vertex count if needed
        if vertex.label.isdigit():
            try:
                vertex_num = int(vertex.label)
                if vertex_num == self.vertex_count:
                    self.vertex_count -= 1
            except ValueError:
                pass

    def add_vertex_from_matrix(self, x, y, label):
        """Add a vertex from matrix import with specific position and label."""
        vertex = VertexItem(x, y, 20, label)
        self.scene.addItem(vertex)
        
        # Update matrices
        self.matrices.add_vertex(vertex)
        
        print(f"[Canvas] Sommet ajouté depuis matrice : {label} en ({x:.1f}, {y:.1f})")
        return vertex

    def create_edge_from_matrix(self, source, target, weight, directed=False):
        """Create an edge from matrix import."""
        # Check if a directed edge already exists in the opposite direction
        is_curvy = directed and any(s == target and t == source for s, t, _, _ in self.edges)

        # Create the edge
        edge = EdgeItem(source, target, radius=source.radius, directed=directed, is_curvy=is_curvy)
        self.scene.addItem(edge)
        
        # Update neighbors
        if target not in source.voisins:
            source.voisins.append(target)
        if source not in target.voisins:
            target.voisins.append(source)
        
        # Add weight text
        text = None
        if weight != 1:  # Only show weight if it's not 1
            p1 = source.sceneBoundingRect().center()
            p2 = target.sceneBoundingRect().center()
            if source == target:
                # Position weight text for self-loops
                loop_radius = source.radius + 10
                mx, my = p1.x() + loop_radius, p1.y() - loop_radius - 10
            elif is_curvy:
                control_x = (p1.x() + p2.x()) / 2 + 40
                control_y = (p1.y() + p2.y()) / 2 - 40
                mx, my = control_x, control_y - 10
            else:
                # Position weight text for regular edges
                mx, my = (p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2 - 10

            # Create the text item
            text = QGraphicsTextItem(str(weight))
            text.setDefaultTextColor(Qt.red)
            text.setZValue(2)
            text.setPos(mx - text.boundingRect().width() / 2, my - text.boundingRect().height() / 2)
            self.scene.addItem(text)

        # Store the edge information
        self.edges.append((source, target, edge, text))
        
        # Update matrices with the new edge
        self.matrices.add_edge(source, target, weight, directed)
        
        print(f"[Canvas] Arête créée depuis matrice entre {source.label} et {target.label}, poids = {weight}, orientée = {directed}")


