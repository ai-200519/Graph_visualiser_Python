# Graph Algorithms Visualizer

A graph visualization and animation tool inspired by [GraphOnline](https://graphonline.top/en/).

## Features

### Interaction Modes
- **DEFAULT**: Select and drag vertices
- **ADD VERTEX**: Click to create a vertex (custom name or auto-numbered)
- **CONNECT VERTEX**: Click two vertices to connect (oriented or not), optionally adding edge weight
- **REMOVE OBJECT**: Delete vertex/edge on click
- **RESET GRAPH**: Clear all vertices and edges
- **ALGORITHM MODE**: Animate graph algorithms (Dijkstra, Prim, etc.)
- **SHOW MATRICES**: Display adjacency, incidence, and distance matrices

### Graph Visualization
- Zoom in/out functionality (mouse wheel or +/- keys)
- Reset zoom (0 key)
- Drag to pan the view
- Directed and undirected edges
- Self-loops
- Edge weights

### Graph Matrices
- **Adjacency Matrix**: Represents connections between vertices
- **Incidence Matrix**: Represents connections between vertices and edges
- **Distance Matrix**: Represents shortest path distances between vertices

### Graph Relationships
- Predecessors/successors (for directed graphs)
- Neighbors/voisins (for all graphs)

## Usage

### Keyboard Shortcuts
- **+**: Zoom in
- **-**: Zoom out
- **0**: Reset zoom

### Mouse Controls
- **Wheel**: Zoom in/out
- **Drag**: Pan the view (in DEFAULT mode)
- **Click**: Select vertices/edges or perform mode-specific actions

## Project Structure
- **core/**: Core functionality
  - **algorithms/**: Graph algorithms
  - **matrices/**: Graph matrix implementations
- **ui/**: User interface components
  - **graph_canvas.py**: Main canvas for graph visualization
  - **vertex_item.py**: Vertex representation
  - **edge_item.py**: Edge representation
  - **matrix_dialog.py**: Dialog for displaying matrices
  - **toolbar.py**: Toolbar with action buttons
  - **main_window.py**: Main application window
# recherche-Op-rationnel
