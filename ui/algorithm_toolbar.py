from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, pyqtSignal


class AlgorithmToolbar(QWidget):
    # Signal pour notifier lorsque le bouton RETOUR est cliqué
    back_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setStyleSheet("background-color: #f0f0f0;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("Problèmes"))

        # Boutons pour chaque catégorie de problème
        self.traversal_btn = QPushButton("De Parcours")
        self.coloring_btn = QPushButton("De Coloration")
        self.mst_btn = QPushButton("D'Arbres couvrants à poids minimum")
        self.shortest_path_btn = QPushButton("De plus court chemin")
        self.flow_btn = QPushButton("De Flots")
        self.back_btn = QPushButton("←– RETOUR")

        # Ajouter les widgets à la mise en page
        layout.addWidget(self.traversal_btn)
        layout.addWidget(self.coloring_btn)
        layout.addWidget(self.mst_btn)
        layout.addWidget(self.shortest_path_btn)
        layout.addWidget(self.flow_btn)
        layout.addWidget(self.back_btn)

        self.setLayout(layout)

        # La connexion des boutons se fera dans MainWindow pour afficher les menus
        self.back_btn.clicked.connect(self.back_clicked)