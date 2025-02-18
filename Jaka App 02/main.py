import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QSizePolicy
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from src.views.movimientos_view import MovimientosView
from src.views.estadisticas_view import EstadisticasView
from src.views.productos_view import ProductosView
from db.database import initialize_db

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jaka Bicicletería")
        self.setGeometry(100, 100, 800, 600)

        # Inicializar la base de datos
        try:
            initialize_db()
        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")

        # Crear el layout principal
        main_layout = QHBoxLayout()

        # Crear la barra lateral
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #f0f0f0;")
        sidebar_layout = QVBoxLayout(self.sidebar)

        # Cargar y redimensionar el logo
        logo_pixmap = QPixmap("images/logo.png")
        logo_label = QLabel()
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(180, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("Logo no disponible")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo_label)

        # Título de la empresa
        title_label = QLabel("Jaka Bicicletería")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title_label)

        # Crear botones de la barra lateral
        self.buttons = {}
        for text in ["Movimientos", "Estadísticas", "Productos"]:
            button = QPushButton(text)
            button.clicked.connect(lambda checked, t=text: self.show_view(t))
            sidebar_layout.addWidget(button)
            self.buttons[text] = button

        sidebar_layout.addStretch()

        # Crear el área de contenido
        self.content_area = QStackedWidget()
        self.content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Crear las vistas
        self.views = {
            "Movimientos": MovimientosView(),
            "Estadísticas": EstadisticasView(),
            "Productos": ProductosView()
        }

        for view in self.views.values():
            self.content_area.addWidget(view)

        # Agregar la barra lateral y el área de contenido al layout principal
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)

        # Crear el widget central y establecer el layout principal
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Mostrar la vista inicial
        self.show_view("Movimientos")

    def show_view(self, view_name):
        # Actualizar los estilos de los botones
        self.update_button_styles(view_name)
        # Mostrar la vista seleccionada
        self.content_area.setCurrentWidget(self.views[view_name])

    def update_button_styles(self, active_button_name):
        # Actualizar el estilo del botón activo y restablecer el estilo de los demás
        for button_name, button in self.buttons.items():
            if button_name == active_button_name:
                button.setStyleSheet("background-color: #505050; color: white; font-weight: bold;")
            else:
                button.setStyleSheet("background-color: #f0f0f0; color: black;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Cargar la hoja de estilo externa
    with open("resources/main.css", "r") as f:
        app.setStyleSheet(f.read())

    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())