from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
import numpy as np
import os

class MatrixDialog(QDialog):
    """Dialog for displaying graph matrices."""
    
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.setWindowTitle("Graph Matrices")
        self.setMinimumSize(600, 400)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add import button at the top
        import_layout = QHBoxLayout()
        import_label = QLabel("Importation de matrice d'adjacence :")
        self.import_button = QPushButton("Import TXT File")
        self.import_button.clicked.connect(self.import_from_file)
        import_layout.addWidget(import_label)
        import_layout.addWidget(self.import_button)
        import_layout.addStretch()
        layout.addLayout(import_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs for each matrix
        self.create_adjacency_tab()
        self.create_incidence_tab()
        self.create_distance_tab()
        
        # Add tab widget to layout
        layout.addWidget(self.tab_widget)
        
        # Add close button
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def import_from_file(self):
        """Import adjacency matrix from a txt file and create the graph."""
        try:
            # Open file dialog
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Selectionnez matrice d'adjacence _ file", 
                "", 
                "Text files (*.txt);;All files (*)"
            )
            
            if not file_path:
                return
            
            # Read and parse the file
            adjacency_matrix = self.parse_adjacency_file(file_path)
            
            if adjacency_matrix is not None:
                # Create graph from adjacency matrix
                self.create_graph_from_matrix(adjacency_matrix)
                
                # Refresh the dialog
                self.refresh_matrices()
                
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Grapg creer avec success par {os.path.basename(file_path)}"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to import file: {str(e)}"
            )
    
    def parse_adjacency_file(self, file_path):
        """Parse adjacency matrix from txt file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # Remove empty lines and strip whitespace
            lines = [line.strip() for line in lines if line.strip()]
            
            if not lines:
                raise ValueError("fichier vide!")
            
            # Parse the matrix
            matrix = []
            for line in lines:
                # Split by whitespace and convert to float
                row = []
                for value in line.split():
                    try:
                        if value.lower() in ['inf', 'infinity', '∞']:
                            row.append(float('inf'))
                        elif value.lower() in ['0', '0.0']:
                            row.append(0.0)
                        else:
                            row.append(float(value))
                    except ValueError:
                        raise ValueError(f"valeur invalide dans matrix: {value}")
                matrix.append(row)
            
            # Check if matrix is square
            n = len(matrix)
            for i, row in enumerate(matrix):
                if len(row) != n:
                    raise ValueError(f"Matrix n'est pas un carree. ligne {i} a {len(row)} elements, expected {n}")
            
            return np.array(matrix)
            
        except Exception as e:
            raise ValueError(f"Error parsing file: {str(e)}")
    
    def create_graph_from_matrix(self, adjacency_matrix):
        """Create a graph from adjacency matrix."""
        try:
            # Clear existing graph
            self.canvas.reset_graph()
            
            n = len(adjacency_matrix)
            if n == 0:
                return
            
            # Create vertices
            vertices = []
            for i in range(n):
                vertex = self.canvas.add_vertex_from_matrix(i * 100 + 50, 100 + (i % 3) * 100, str(i + 1))
                vertices.append(vertex)
            
            # Create edges based on adjacency matrix
            for i in range(n):
                for j in range(n):
                    weight = adjacency_matrix[i, j]
                    if weight > 0 and not np.isinf(weight):
                        # Check if edge already exists (for undirected graphs)
                        if i != j:  # No self-loops for now
                            # Determine if graph is directed by checking asymmetry
                            is_directed = (adjacency_matrix[i, j] != adjacency_matrix[j, i])
                            
                            # Only create edge if it doesn't exist or if it's directed
                            if is_directed or i < j:  # For undirected, only create once
                                self.canvas.create_edge_from_matrix(
                                    vertices[i], 
                                    vertices[j], 
                                    weight, 
                                    is_directed
                                )
            
            print(f"[MatrixDialog] Graph created with {n} vertices")
            
        except Exception as e:
            raise ValueError(f"Error creating graph: {str(e)}")
    
    def refresh_matrices(self):
        """Refresh all matrix tabs."""
        self.tab_widget.clear()
        self.create_adjacency_tab()
        self.create_incidence_tab()
        self.create_distance_tab()
    
    def create_adjacency_tab(self):
        """Create the adjacency matrix tab."""
        tab = QTableWidget()
        self.tab_widget.addTab(tab, "Adjacency Matrix")
        
        # Get matrix data
        matrix = self.canvas.get_adjacency_matrix()
        vertex_labels = self.canvas.get_vertex_labels()
        
        if len(matrix) == 0:
            tab.setRowCount(1)
            tab.setColumnCount(1)
            tab.setItem(0, 0, QTableWidgetItem("Pas de sommets dans le graph"))
            return
        
        # Set up table
        n = len(vertex_labels)
        tab.setRowCount(n)
        tab.setColumnCount(n)
        
        # Set headers
        tab.setHorizontalHeaderLabels(vertex_labels)
        tab.setVerticalHeaderLabels(vertex_labels)
        
        # Fill table with matrix values
        for i in range(n):
            for j in range(n):
                value = matrix[i, j]
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                tab.setItem(i, j, item)
        
        # Resize columns to content
        tab.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    
    def create_incidence_tab(self):
        """Create the incidence matrix tab."""
        tab = QTableWidget()
        self.tab_widget.addTab(tab, "Incidence Matrix")
        
        # Get matrix data
        matrix = self.canvas.get_incidence_matrix()
        vertex_labels = self.canvas.get_vertex_labels()
        edge_labels = self.canvas.get_edge_labels()
        
        if len(matrix) == 0 or len(edge_labels) == 0:
            tab.setRowCount(1)
            tab.setColumnCount(1)
            tab.setItem(0, 0, QTableWidgetItem("pas d'arcs dans le graphe"))
            return
        
        # Set up table
        n_vertices = len(vertex_labels)
        n_edges = len(edge_labels)
        tab.setRowCount(n_vertices)
        tab.setColumnCount(n_edges)
        
        # Set headers
        tab.setHorizontalHeaderLabels(edge_labels)
        tab.setVerticalHeaderLabels(vertex_labels)
        
        # Fill table with matrix values
        for i in range(n_vertices):
            for j in range(n_edges):
                value = matrix[i, j]
                item = QTableWidgetItem(str(int(value)))
                item.setTextAlignment(Qt.AlignCenter)
                tab.setItem(i, j, item)
        
        # Resize columns to content
        tab.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    
    def create_distance_tab(self):
        """Create the distance matrix tab."""
        tab = QTableWidget()
        self.tab_widget.addTab(tab, "Distance Matrix")
        
        # Get matrix data
        matrix = self.canvas.get_distance_matrix()
        vertex_labels = self.canvas.get_vertex_labels()
        
        if len(matrix) == 0:
            tab.setRowCount(1)
            tab.setColumnCount(1)
            tab.setItem(0, 0, QTableWidgetItem("Pas de sommets dans le graph"))
            return
        
        # Set up table
        n = len(vertex_labels)
        tab.setRowCount(n)
        tab.setColumnCount(n)
        
        # Set headers
        tab.setHorizontalHeaderLabels(vertex_labels)
        tab.setVerticalHeaderLabels(vertex_labels)
        
        # Fill table with matrix values
        for i in range(n):
            for j in range(n):
                value = matrix[i, j]
                if np.isinf(value):
                    text = "∞"
                else:
                    text = str(value)
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                tab.setItem(i, j, item)
        
        # Resize columns to content
        tab.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)