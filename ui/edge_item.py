from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtGui import QPainterPath, QPen, QBrush
from PyQt5.QtCore import QPointF, Qt, QLineF, QRectF
import math

class EdgeItem(QGraphicsPathItem):
    def __init__(self, source, target, radius=20, directed=False, is_curvy=False, parent=None):
        super().__init__(parent)
        self.source = source
        self.target = target
        self.radius = radius
        self.directed = directed
        self.is_curvy = is_curvy 
        self.arrow_size = 10  # Size of the arrowhead
        self.pen = QPen(Qt.black, 2)
        self.brush = QBrush(Qt.NoBrush)  # No fill for the edge
        self.setPen(self.pen)
        self.setBrush(self.brush)
        self.setZValue(-1)  # Set the Z value to be below the vertices
                
        # Update successors and predecessors
        if self.directed:
            self.source.successors.append(self.target)
            self.target.predecessors.append(self.source)
        self.source.voisins.append(self.target)
        self.target.voisins.append(self.source)        
        self.debug_successors_predecessors_voisins()
        
        # Set the initial path    
        self.update_path()

    def update_path(self):
        """Update the path of the edge (line + arrowhead)."""
        p1 = self.source.sceneBoundingRect().center()
        p2 = self.target.sceneBoundingRect().center()

        if self.source == self.target:
            # Handle self-loops
            loop_radius = self.radius + 20  # Adjust the radius for the loop
            offset = self.radius + 30  # Offset for the control point of the curve
            path = QPainterPath()

            # Start point of the loop (top of the vertex boundary)
            start_x = p1.x()
            start_y = p1.y() - self.radius

            # End point of the loop (right side of the vertex boundary)
            end_x = p1.x() + self.radius
            end_y = p1.y()

            # Control point for the curve (above and to the right of the vertex)
            control_x = p1.x() + offset
            control_y = p1.y() - offset

            # Move to the start point
            path.moveTo(start_x, start_y)
            

            # Draw the curved line using a quadratic Bezier curve
            path.quadTo(control_x, control_y, end_x, end_y)

            self.setPen(self.pen)  # Ensure the pen is applied

            self.setPath(path)
            return

        path = QPainterPath()
        if self.is_curvy:
            # Calculate the control point for the curve
            control_x = (p1.x() + p2.x()) / 2 + 40
            control_y = (p1.y() + p2.y()) / 2 - 40
            path.moveTo(p1)
            path.quadTo(QPointF(control_x, control_y), p2)
            
            # Calculate the tangent at the endpoint of the curve
            tangent = QLineF(QPointF(control_x, control_y), p2)
            tangent.setLength(tangent.length() - self.radius)  # Adjust the endpoint to stop at the circle boundary
            adjusted_end = tangent.p2()  # New endpoint for the arrowhead
            
            angle = math.atan2(-tangent.dy(), tangent.dx())

            # Calculate the two points of the arrowhead
            arrow_p1 = adjusted_end + QPointF(
                math.sin(angle - math.pi / 3) * self.arrow_size,
                math.cos(angle - math.pi / 3) * self.arrow_size
            )
            arrow_p2 = adjusted_end + QPointF(
                math.sin(angle - math.pi + math.pi / 3) * self.arrow_size,
                math.cos(angle - math.pi + math.pi / 3) * self.arrow_size
            )

            # Create the arrowhead path
            arrow_path = QPainterPath()
            arrow_path.moveTo(adjusted_end)
            arrow_path.lineTo(arrow_p1)
            arrow_path.lineTo(arrow_p2)
            arrow_path.lineTo(adjusted_end)
            path.addPath(arrow_path)
            
        else:
            # Calculate the line
            line = QLineF(p1, p2)
            line.setLength(line.length() - self.radius)  # Stop at the target circle boundary
            
            path.moveTo(line.p1())
            path.lineTo(line.p2())
            
            if self.directed:
                # Calculate the arrowhead
                angle = math.atan2(-line.dy(), line.dx())
                arrow_p1 = line.p2() + QPointF(
                    math.sin(angle - math.pi / 3) * self.arrow_size,
                    math.cos(angle - math.pi / 3) * self.arrow_size
                )
                arrow_p2 = line.p2() + QPointF(
                    math.sin(angle - math.pi + math.pi / 3) * self.arrow_size,
                    math.cos(angle - math.pi + math.pi / 3) * self.arrow_size
                )

                # Add the arrowhead to the path
                path.moveTo(line.p2())
                path.lineTo(arrow_p1)
                path.lineTo(arrow_p2)
                path.lineTo(line.p2())

        self.setPath(path)
        
    def set_source(self, source):
        # Remove the old source from the target's predecessors and voisins
        if self.directed and self.source in self.target.predecessors:
            self.target.predecessors.remove(self.source)
        if self.source in self.target.voisins:
            self.target.voisins.remove(self.source)
            
        self.source = source
        # Update successors, predecessors, and voisins
        if self.directed:
            self.source.successors.append(self.target)
            self.target.predecessors.append(self.source)
        self.source.voisins.append(self.target)
        self.target.voisins.append(self.source)
        self.debug_successors_predecessors_voisins()
            
        self.update_path()

    def set_target(self, target):
        # Remove the old target from the source's successors and voisins
        if self.directed and self.target in self.source.successors:
            self.source.successors.remove(self.target)
        if self.target in self.source.voisins:
            self.source.voisins.remove(self.target)

        self.target = target

        # Update successors, predecessors, and voisins
        if self.directed:
            self.source.successors.append(self.target)
            self.target.predecessors.append(self.source)
        self.source.voisins.append(self.target)
        self.target.voisins.append(self.source)
        self.debug_successors_predecessors_voisins()
        
        self.update_path()
    def remove_edge(self):
        """Remove the edge and update successors, predecessors, and voisins."""
        if self.directed:
            # Remove the target from the source's successors
            if self.target in self.source.successors:
                self.source.successors.remove(self.target)
            # Remove the source from the target's predecessors
            if self.source in self.target.predecessors:
                self.target.predecessors.remove(self.source)
        # Remove each other from voisins
        if self.target in self.source.voisins:
            self.source.voisins.remove(self.target)
        if self.source in self.target.voisins:
            self.target.voisins.remove(self.source)
        self.scene().removeItem(self)  # Remove the edge from the scene
        print(f"[Debug] Edge removed: {self.source.label} -> {self.target.label}")

    def debug_successors_predecessors_voisins(self):
        """Debug function to print successors, predecessors, and voisins."""
        print(f"[Debug] Source: {self.source.label}")
        print(f"  Successors: {[v.label for v in self.source.successors]}")
        print(f"  Voisins: {[v.label for v in self.source.voisins]}")
        print(f"[Debug] Target: {self.target.label}")
        print(f"  Predecessors: {[v.label for v in self.target.predecessors]}")
        print(f"  Voisins: {[v.label for v in self.target.voisins]}")