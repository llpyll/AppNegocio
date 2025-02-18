# estadisticas_view.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class EstadisticasView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Contenido de la vista de estadísticas
        label = QLabel("Contenido de Estadísticas")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(label)
        self.setLayout(layout)
