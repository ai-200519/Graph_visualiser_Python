from PyQt5.QtWidgets import (
    QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsScene, QGraphicsView,
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QInputDialog,
    QMessageBox, QApplication
)
from PyQt5.QtGui import QBrush, QPen, QColor, QFont
from PyQt5.QtCore import Qt, QPointF

class VertexItem(QGraphicsEllipseItem):
    RADIUS = 20

    # Couleurs centralisées
    COLOR_DEFAULT = QBrush(Qt.yellow)
    COLOR_HOVER = QBrush(Qt.green)
    COLOR_SELECTED = QBrush(Qt.cyan)

    def __init__(self, x, y, radius, label):
        super().__init__(x - radius, y - radius, 2 * radius, 2 * radius)

        self.label = label  # pour affichage dans la console
        self.radius = radius

        # Style du sommet
        self.setBrush(self.COLOR_DEFAULT)
        self.setPen(QPen(Qt.black))
        self.setZValue(1)

        # Comportement
        self.setFlags(
            QGraphicsEllipseItem.ItemIsMovable |
            QGraphicsEllipseItem.ItemIsSelectable |
            QGraphicsEllipseItem.ItemSendsGeometryChanges |
            QGraphicsEllipseItem.ItemIsFocusable
        )
        self.setAcceptHoverEvents(True)

        # Successeur et prédécesseur
        self.voisins = []  # Liste des voisins connectés
        self.successors = [] # Liste des successeurs connectés
        self.predecessors = [] # Liste des prédécesseurs connectés
        
        # Créer le texte associé
        self.text_item = QGraphicsTextItem(label, self)
        self.text_item.setDefaultTextColor(Qt.black)
        self.center_text()

    def set_color(self, color):
        """Set the vertex color"""
        if isinstance(color, QColor):
            self.setBrush(QBrush(color))
        elif isinstance(color, QBrush):
            self.setBrush(color)
        else:
            raise TypeError("Color must be QColor or QBrush")

    def center_text(self):
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(
            self.rect().center().x() - text_rect.width() / 2,
            self.rect().center().y() - text_rect.height() / 2
        )

    def hoverEnterEvent(self, event):
        if self.brush() == self.COLOR_DEFAULT:  # Only change color if in default state
            self.setBrush(self.COLOR_HOVER)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if self.brush() == self.COLOR_HOVER:  # Only change back if in hover state
            self.setBrush(self.COLOR_DEFAULT)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.scene().views()[0].mode == "DEFAULT":
            self.setBrush(self.COLOR_SELECTED)
            super().mousePressEvent(event)
        elif event.button() == Qt.RightButton:
            # Afficher le menu contextuel
            self.show_context_menu(event)       
            
    def mouseMoveEvent(self, event):
        """Handle vertex movement and notify the canvas to update edges."""
        super().mouseMoveEvent(event)
        # Notify the parent canvas to update edges
        if self.scene():
            canvas = self.scene().views()[0]  # Assuming the first view is the GraphCanvas
            if hasattr(canvas, 'update_edges'):
                canvas.update_edges(self)        