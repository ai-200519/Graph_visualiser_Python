from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QStackedWidget
from PyQt5.QtCore import Qt
from ui.algorithm_toolbar import AlgorithmToolbar


class ToolBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)
        self.setStyleSheet("background-color: #f0f0f0;")

        # Create the main toolbar
        self.main_toolbar = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        main_layout.addWidget(QLabel("Modes"))
        self.default_btn = QPushButton("DEFAULT")
        self.add_vertex_btn = QPushButton("ADD VERTEX")
        self.connect_btn = QPushButton("CONNECT VERTICES")
        self.remove_btn = QPushButton("REMOVE OBJECT")
        self.algo_btn = QPushButton("ALGORITHMS")
        self.reset_btn = QPushButton("RESET GRAPH")
        self.matrices_btn = QPushButton("SHOW MATRICES")

        main_layout.addWidget(self.default_btn)
        main_layout.addWidget(self.add_vertex_btn)
        main_layout.addWidget(self.connect_btn)
        main_layout.addWidget(self.remove_btn)
        main_layout.addWidget(self.algo_btn)
        main_layout.addWidget(self.reset_btn)
        main_layout.addWidget(self.matrices_btn)

        main_layout.addWidget(QLabel("Nom des sommets"))
        self.naming_mode = QComboBox()
        self.naming_mode.addItems(["Auto", "Custom"])
        main_layout.addWidget(self.naming_mode)

        self.main_toolbar.setLayout(main_layout)

        # Create the algorithm toolbar
        self.algorithm_toolbar = AlgorithmToolbar()
        self.algorithm_toolbar.back_clicked.connect(self.switch_to_main_toolbar)

        # Use a QStackedWidget to switch between toolbars
        self.toolbar_stack = QStackedWidget()
        self.toolbar_stack.addWidget(self.main_toolbar)
        self.toolbar_stack.addWidget(self.algorithm_toolbar)

        # Set the initial layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar_stack)
        self.setLayout(layout)

    def switch_to_algorithm_toolbar(self):
        """Switch to the algorithm toolbar."""
        self.toolbar_stack.setCurrentWidget(self.algorithm_toolbar)

    def switch_to_main_toolbar(self):
        """Switch back to the main toolbar."""
        self.toolbar_stack.setCurrentWidget(self.main_toolbar)

    def get_naming_mode(self):
        """Get the current naming mode."""
        return self.naming_mode.currentText()
