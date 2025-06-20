import numpy as np
from typing import Dict, List, Tuple, Set, Optional, Any

class GraphMatrices:
    """
    A class to manage various graph matrices:
    - Adjacency Matrix: Represents connections between vertices
    - Incidence Matrix: Represents connections between vertices and edges
    - Distance Matrix: Represents shortest path distances between vertices
    """
    
    def __init__(self):
        """Initialize empty matrices."""
        self.vertices = []  # List of vertex objects
        self.vertex_indices = {}  # Mapping from vertex to index
        self.edges = []  # List of edge tuples (source, target, weight, directed)
        
        # Initialize empty matrices
        self.adjacency_matrix = np.array([])
        self.incidence_matrix = np.array([])
        self.distance_matrix = np.array([])
        
    def add_vertex(self, vertex):
        """
        Add a vertex to the matrices.
        
        Args:
            vertex: The vertex object to add
        """
        if vertex not in self.vertex_indices:
            # Add vertex to the list and update the index mapping
            self.vertex_indices[vertex] = len(self.vertices)
            self.vertices.append(vertex)
            
            # Update matrices
            self._update_adjacency_matrix()
            self._update_incidence_matrix()
            self._update_distance_matrix()
    
    def remove_vertex(self, vertex):
        """
        Remove a vertex from the matrices.
        
        Args:
            vertex: The vertex object to remove
        """
        if vertex in self.vertex_indices:
            # Get the index of the vertex
            index = self.vertex_indices[vertex]
            
            # Remove edges connected to this vertex
            self.edges = [edge for edge in self.edges 
                         if edge[0] != vertex and edge[1] != vertex]
            
            # Remove the vertex from the list
            self.vertices.pop(index)
            
            # Update the index mapping
            self.vertex_indices = {v: i for i, v in enumerate(self.vertices)}
            
            # Update matrices
            self._update_adjacency_matrix()
            self._update_incidence_matrix()
            self._update_distance_matrix()
    
    def add_edge(self, source, target, weight=1, directed=False):
        """
        Add an edge to the matrices.
        
        Args:
            source: The source vertex
            target: The target vertex
            weight: The weight of the edge (default: 1)
            directed: Whether the edge is directed (default: False)
        """
        # Ensure both vertices are in the matrices
        self.add_vertex(source)
        self.add_vertex(target)
        
        # Add the edge to the list
        edge = (source, target, weight, directed)
        if edge not in self.edges:
            self.edges.append(edge)
            
            # Update matrices
            self._update_adjacency_matrix()
            self._update_incidence_matrix()
            self._update_distance_matrix()
    
    def remove_edge(self, source, target, directed=False):
        """
        Remove an edge from the matrices.
        
        Args:
            source: The source vertex
            target: The target vertex
            directed: Whether the edge is directed (default: False)
        """
        # Find and remove the edge
        edges_to_remove = []
        for edge in self.edges:
            s, t, _, d = edge
            if directed:
                if s == source and t == target:
                    edges_to_remove.append(edge)
            else:
                if (s == source and t == target) or (s == target and t == source):
                    edges_to_remove.append(edge)
        
        for edge in edges_to_remove:
            self.edges.remove(edge)
        
        # Update matrices
        self._update_adjacency_matrix()
        self._update_incidence_matrix()
        self._update_distance_matrix()
    
    def reset(self):
        """Reset all matrices and data."""
        self.vertices = []
        self.vertex_indices = {}
        self.edges = []
        self.adjacency_matrix = np.array([])
        self.incidence_matrix = np.array([])
        self.distance_matrix = np.array([])
    
    def _update_adjacency_matrix(self):
        """Update the adjacency matrix based on current vertices and edges."""
        n = len(self.vertices)
        if n == 0:
            self.adjacency_matrix = np.array([])
            return
        
        # Create a new adjacency matrix filled with zeros
        self.adjacency_matrix = np.zeros((n, n))
        
        # Fill the matrix based on edges
        for source, target, weight, directed in self.edges:
            source_idx = self.vertex_indices[source]
            target_idx = self.vertex_indices[target]
            
            # Set the weight in the matrix
            self.adjacency_matrix[source_idx, target_idx] = weight
            
            # For undirected edges, set the weight in both directions
            if not directed:
                self.adjacency_matrix[target_idx, source_idx] = weight
    
    def _update_incidence_matrix(self):
        """Update the incidence matrix based on current vertices and edges."""
        n_vertices = len(self.vertices)
        n_edges = len(self.edges)
        
        if n_vertices == 0 or n_edges == 0:
            self.incidence_matrix = np.array([])
            return
        
        # Create a new incidence matrix filled with zeros
        self.incidence_matrix = np.zeros((n_vertices, n_edges))
        
        # Fill the matrix based on edges
        for edge_idx, (source, target, weight, directed) in enumerate(self.edges):
            source_idx = self.vertex_indices[source]
            target_idx = self.vertex_indices[target]
            
            if directed:
                # For directed edges: -1 for source, 1 for target
                self.incidence_matrix[source_idx, edge_idx] = -1
                self.incidence_matrix[target_idx, edge_idx] = 1
            else:
                # For undirected edges: 1 for both source and target
                self.incidence_matrix[source_idx, edge_idx] = 1
                self.incidence_matrix[target_idx, edge_idx] = 1
    
    def _update_distance_matrix(self):
        """Update the distance matrix using Floyd-Warshall algorithm."""
        n = len(self.vertices)
        if n == 0:
            self.distance_matrix = np.array([])
            return
        
        # Initialize distance matrix with infinity
        self.distance_matrix = np.full((n, n), np.inf)
        
        # Set diagonal to 0 (distance to self)
        np.fill_diagonal(self.distance_matrix, 0)
        
        # Set direct connections based on adjacency matrix
        for i in range(n):
            for j in range(n):
                if self.adjacency_matrix[i, j] > 0:
                    self.distance_matrix[i, j] = self.adjacency_matrix[i, j]
        
        # Floyd-Warshall algorithm
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if self.distance_matrix[i, k] + self.distance_matrix[k, j] < self.distance_matrix[i, j]:
                        self.distance_matrix[i, j] = self.distance_matrix[i, k] + self.distance_matrix[k, j]
    
    def get_adjacency_matrix(self) -> np.ndarray:
        """Get the adjacency matrix."""
        return self.adjacency_matrix
    
    def get_incidence_matrix(self) -> np.ndarray:
        """Get the incidence matrix."""
        return self.incidence_matrix
    
    def get_distance_matrix(self) -> np.ndarray:
        """Get the distance matrix."""
        return self.distance_matrix
    
    def get_vertex_labels(self) -> List[str]:
        """Get the labels of all vertices."""
        return [vertex.label for vertex in self.vertices]
    
    def get_edge_labels(self) -> List[str]:
        """Get the labels of all edges."""
        return [f"{s.label}-{t.label}" for s, t, _, _ in self.edges]
    
    def __str__(self) -> str:
        """String representation of the matrices."""
        vertex_labels = self.get_vertex_labels()
        
        adj_str = "Adjacency Matrix:\n"
        if len(self.adjacency_matrix) > 0:
            adj_str += f"  {' '.join(vertex_labels)}\n"
            for i, row in enumerate(self.adjacency_matrix):
                adj_str += f"{vertex_labels[i]} {' '.join(map(str, row))}\n"
        else:
            adj_str += "  Empty\n"
        
        inc_str = "Incidence Matrix:\n"
        if len(self.incidence_matrix) > 0:
            edge_labels = self.get_edge_labels()
            inc_str += f"  {' '.join(edge_labels)}\n"
            for i, row in enumerate(self.incidence_matrix):
                inc_str += f"{vertex_labels[i]} {' '.join(map(str, row))}\n"
        else:
            inc_str += "  Empty\n"
        
        dist_str = "Distance Matrix:\n"
        if len(self.distance_matrix) > 0:
            dist_str += f"  {' '.join(vertex_labels)}\n"
            for i, row in enumerate(self.distance_matrix):
                dist_str += f"{vertex_labels[i]} {' '.join(map(lambda x: 'inf' if np.isinf(x) else str(x), row))}\n"
        else:
            dist_str += "  Empty\n"
        
        return f"{adj_str}\n{inc_str}\n{dist_str}"