from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QHBoxLayout

class EdgeInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Entrer les détails de l'arête")
        self.setFixedSize(300, 150)

        # Layout
        layout = QVBoxLayout()

        # Weight input
        self.weight_label = QLabel("Entrez le poids de l'arête (optionnel) :")
        self.weight_input = QLineEdit()
        layout.addWidget(self.weight_label)
        layout.addWidget(self.weight_input)

        # Directed checkbox
        self.directed_checkbox = QCheckBox("Arête orientée (flèche)")
        layout.addWidget(self.directed_checkbox)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Annuler")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Connect buttons
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.setLayout(layout)

    def get_input(self):
        """Return the weight and whether the edge is directed."""
        weight = self.weight_input.text().strip()
        directed = self.directed_checkbox.isChecked()
        return weight, directed