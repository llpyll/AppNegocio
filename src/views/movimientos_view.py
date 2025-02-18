from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QSizePolicy, QSpacerItem, QFrame, QMenu, QDialog, QLabel, QLineEdit, QDateTimeEdit, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt, QDateTime, QTimer
from src.views.venta_productos_view import VentasProductosView
from PyQt6.QtGui import QIcon, QPixmap
import sqlite3
from datetime import datetime

class MovimientosView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_styles()

    def init_ui(self):
        # Crear el layout principal
        main_layout = QVBoxLayout()

        # Crear el layout para los botones superiores y alinearlos a la derecha
        top_buttons_layout = QHBoxLayout()
        top_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        # Botón Nueva Venta con menú desplegable
        self.new_sale_button = QPushButton("Nueva Venta")
        self.new_sale_button.setObjectName("new_sale_button")
        self.new_sale_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Crear menú desplegable para el botón Nueva Venta
        self.new_sale_menu = QMenu(self)
        self.new_sale_menu.addAction("Venta de productos", self.open_ventas_productos_view)
        self.new_sale_menu.addAction("Venta libre", self.on_sale_free)
        self.new_sale_button.setMenu(self.new_sale_menu)

        top_buttons_layout.addWidget(self.new_sale_button)

        # Botón Nuevo Gasto con menú desplegable
        self.new_expense_button = QPushButton("Nuevo Gasto")
        self.new_expense_button.setObjectName("new_expense_button")
        self.new_expense_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Crear menú desplegable para el botón Nuevo Gasto
        self.new_expense_menu = QMenu(self)
        self.new_expense_menu.addAction("Gasto Libre", self.on_expense_free)
        self.new_expense_menu.addAction("Compra de Insumo", self.on_supply_purchase)
        self.new_expense_button.setMenu(self.new_expense_menu)

        top_buttons_layout.addWidget(self.new_expense_button)

        # Agregar el layout de los botones superiores al layout principal
        main_layout.addLayout(top_buttons_layout)

        # Agregar Resumen Financiero
        self.resumen_financiero_view = ResumenFinancieroView()
        main_layout.addWidget(self.resumen_financiero_view)

        # Agregar vista de ingresos y egresos
        self.ingresos_egresos_view = IngresosEgresosView()
        main_layout.addWidget(self.ingresos_egresos_view)

        # Establecer el layout principal
        self.setLayout(main_layout)

    def open_ventas_productos_view(self):
        # Abrir la vista de ventas de productos
        self.ventas_productos_view = VentasProductosView()
        self.ventas_productos_view.show()
        self.ingresos_egresos_view.refresh_tables()

    def on_sale_free(self):
        # Abrir el diálogo de venta libre
        dialog = VentaLibreDialog(self)
        if dialog.exec():
            print("Venta libre guardada exitosamente")
            self.ingresos_egresos_view.refresh_tables()

    def on_expense_free(self):
        # Abrir el diálogo de gasto libre
        dialog = GastoLibreDialog(self)
        if dialog.exec():
            print("Gasto libre guardado exitosamente")
            self.ingresos_egresos_view.refresh_tables()

    def on_supply_purchase(self):
        # Abrir el diálogo de compra de insumos
        dialog = SupplyPurchaseDialog(self)
        if dialog.exec():
            print("Compra de insumo guardada exitosamente")
            self.ingresos_egresos_view.refresh_tables()

    def load_styles(self):
        # Cargar el archivo CSS y aplicarlo
        try:
            with open("resources/movimientos_view.css", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Error: No se pudo cargar el archivo CSS. Asegúrate de que 'movimientos_view.css' exista.")


class IngresosEgresosView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Crear el layout principal
        main_layout = QVBoxLayout()

        # Botones para mostrar tablas de ingresos y egresos
        tables_buttons_layout = QHBoxLayout()

        self.show_ingresos_button = QPushButton("Mostrar Ingresos")
        self.show_ingresos_button.clicked.connect(self.toggle_ingresos_table)
        tables_buttons_layout.addWidget(self.show_ingresos_button)

        self.show_egresos_button = QPushButton("Mostrar Egresos")
        self.show_egresos_button.clicked.connect(self.toggle_egresos_table)
        tables_buttons_layout.addWidget(self.show_egresos_button)

        main_layout.addLayout(tables_buttons_layout)

        # Crear tablas para ingresos y egresos
        self.ingresos_table = QTableWidget()
        self.ingresos_table.setColumnCount(3)
        self.ingresos_table.setHorizontalHeaderLabels(["Fecha y Hora", "Concepto", "Total"])
        self.ingresos_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ingresos_table.verticalHeader().setVisible(False)
        self.ingresos_table.setAlternatingRowColors(True)
        self.ingresos_table.setStyleSheet("QTableWidget::item { border: none; } QTableWidget { gridline-color: transparent; alternate-background-color: #f9f9f9; } QHeaderView::section { padding: 10px; }")
        main_layout.addWidget(self.ingresos_table)
        self.ingresos_table.hide()

        self.egresos_table = QTableWidget()
        self.egresos_table.setColumnCount(3)
        self.egresos_table.setHorizontalHeaderLabels(["Fecha y Hora", "Concepto", "Total"])
        self.egresos_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.egresos_table.verticalHeader().setVisible(False)
        self.egresos_table.setAlternatingRowColors(True)
        self.egresos_table.setStyleSheet("QTableWidget::item { border: none; } QTableWidget { gridline-color: transparent; alternate-background-color: #f9f9f9; } QHeaderView::section { padding: 10px; }")
        main_layout.addWidget(self.egresos_table)
        self.egresos_table.hide()

        # Establecer el layout principal
        self.setLayout(main_layout)

    def toggle_ingresos_table(self):
        if self.ingresos_table.isHidden():
            self.show_ingresos_table()
            self.egresos_table.hide()
        else:
            self.ingresos_table.hide()

    def toggle_egresos_table(self):
        if self.egresos_table.isHidden():
            self.show_egresos_table()
            self.ingresos_table.hide()
        else:
            self.egresos_table.hide()

    def refresh_tables(self):
        if not self.ingresos_table.isHidden():
            self.show_ingresos_table()
        if not self.egresos_table.isHidden():
            self.show_egresos_table()

    def show_ingresos_table(self):
        # Conectar a la base de datos y obtener los ingresos
        connection = sqlite3.connect('productos.db')
        cursor = connection.cursor()
        cursor.execute('SELECT fecha, concepto, total FROM ventas')
        ingresos = cursor.fetchall()
        connection.close()

        # Poblar la tabla de ingresos
        self.ingresos_table.setRowCount(len(ingresos))
        for row_idx, (fecha, concepto, total) in enumerate(ingresos):
            self.ingresos_table.setItem(row_idx, 0, QTableWidgetItem(fecha))
            self.ingresos_table.setItem(row_idx, 1, QTableWidgetItem(concepto))
            self.ingresos_table.setItem(row_idx, 2, QTableWidgetItem(f"Gs. {total}"))

        self.ingresos_table.show()

    def show_egresos_table(self):
        # Conectar a la base de datos y obtener los egresos
        connection = sqlite3.connect('productos.db')
        cursor = connection.cursor()
        cursor.execute('SELECT fecha, concepto, total FROM gastos')
        egresos = cursor.fetchall()
        connection.close()

        # Poblar la tabla de egresos
        self.egresos_table.setRowCount(len(egresos))
        for row_idx, (fecha, concepto, total) in enumerate(egresos):
            self.egresos_table.setItem(row_idx, 0, QTableWidgetItem(fecha))
            self.egresos_table.setItem(row_idx, 1, QTableWidgetItem(concepto))
            self.egresos_table.setItem(row_idx, 2, QTableWidgetItem(f"Gs. {total}"))

        self.egresos_table.show()


# Definir los diálogos faltantes para evitar errores
class VentaLibreDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Venta Libre")
        # Aquí puedes agregar los elementos del diálogo según tus necesidades

class GastoLibreDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gasto Libre")
        # Aquí puedes agregar los elementos del diálogo según tus necesidades

class SupplyPurchaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compra de Insumo")
        # Aquí puedes agregar los elementos del diálogo según tus necesidades



class ResumenFinancieroView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_timer()
        self.update_resumen()

    def init_ui(self):
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        # Layout para las tarjetas
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        # Crear las tres tarjetas
        balance_card = self.create_card("Balance", "Gs. 0", "#E6F4EA")
        ventas_card = self.create_card("Ventas totales", "Gs. 0", "#E6F4EA")
        gastos_card = self.create_card("Gastos totales", "Gs. 0", "#FCE8E8")

        # Guardar referencias a los valores para actualizarlos después
        self.balance_value = balance_card.findChild(QLabel, "value")
        self.ventas_value = ventas_card.findChild(QLabel, "value")
        self.gastos_value = gastos_card.findChild(QLabel, "value")

        # Añadir las tarjetas al layout de tarjetas
        cards_layout.addWidget(balance_card)
        cards_layout.addWidget(ventas_card)
        cards_layout.addWidget(gastos_card)

        # Añadir el layout de tarjetas al layout principal
        main_layout.insertLayout(0, cards_layout)

        # Establecer márgenes externos
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.setLayout(main_layout)

    def setup_timer(self):
        # Configurar un temporizador para actualizar los valores en tiempo real
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_resumen)
        self.timer.start(5000)  # Actualizar cada 5 segundos

    def create_card(self, title, initial_value, background_color):
        # Crear un widget contenedor para la tarjeta
        card = QWidget()
        card.setObjectName("card")
        card.setStyleSheet(f"""
            QWidget#card {{
                background-color: {background_color};
                border-radius: 10px;
                padding: 15px;
            }}
            QLabel#title {{
                color: #5F6368;
                font-size: 14px;
                padding-bottom: 5px;
            }}
            QLabel#value {{
                color: #202124;
                font-size: 24px;
                font-weight: bold;
            }}
        """)

        # Layout vertical para la tarjeta
        card_layout = QVBoxLayout()
        card_layout.setSpacing(5)

        # Título
        title_label = QLabel(title)
        title_label.setObjectName("title")

        # Valor
        value_label = QLabel(initial_value)
        value_label.setObjectName("value")
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Añadir elementos al layout de la tarjeta
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        card_layout.addStretch()

        # Establecer márgenes internos de la tarjeta
        card_layout.setContentsMargins(15, 15, 15, 15)

        # Ajustar tamaño de la tarjeta según el contenido
        card.setFixedSize(250, 120)

        card.setLayout(card_layout)
        return card

    def update_resumen(self):
        total_ventas = self.get_total_ventas()
        total_gastos = self.get_total_gastos()
        diferencia = total_ventas - total_gastos

        # Formatear números con separador de miles
        self.ventas_value.setText(f"Gs. {self.format_number(total_ventas)}")
        self.gastos_value.setText(f"Gs. {self.format_number(total_gastos)}")
        self.balance_value.setText(f"Gs. {self.format_number(diferencia)}")

    def format_number(self, number):
        """Formatea un número con separador de miles."""
        return f"{int(number):,d}".replace(',', '.')

    def get_total_ventas(self):
        """Obtiene la suma total de las ventas registradas."""
        query = 'SELECT SUM(total) FROM ventas WHERE concepto != "insumo"'
        return self.execute_query(query)

    def get_total_gastos(self):
        """Obtiene la suma total de los gastos registrados."""
        query = 'SELECT SUM(total) FROM gastos WHERE concepto != "insumo"'
        return self.execute_query(query)

    def execute_query(self, query):
        """Ejecuta una consulta SQL y devuelve un valor numérico o 0."""
        with sqlite3.connect('productos.db') as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()[0]
            return result if result else 0


class VentaLibreDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Venta Libre")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Campo para el monto de la venta
        self.monto_label = QLabel("Monto de la venta:")
        self.monto_input = QLineEdit()
        self.monto_input.setPlaceholderText("Ingrese el monto")
        layout.addWidget(self.monto_label)
        layout.addWidget(self.monto_input)

        # Campo para el concepto de la venta
        self.concepto_label = QLabel("Concepto de la venta:")
        self.concepto_input = QLineEdit()
        self.concepto_input.setPlaceholderText("Ingrese el concepto")
        layout.addWidget(self.concepto_label)
        layout.addWidget(self.concepto_input)

        # Fecha y hora actual (no editable)
        self.fecha_hora_label = QLabel("Fecha y hora de la venta:")
        self.fecha_hora_input = QDateTimeEdit()
        self.fecha_hora_input.setDateTime(QDateTime.currentDateTime())
        self.fecha_hora_input.setEnabled(False)  # Deshabilitar edición de fecha y hora
        layout.addWidget(self.fecha_hora_label)
        layout.addWidget(self.fecha_hora_input)

        # Botón para guardar
        self.save_button = QPushButton("Guardar Venta")
        self.save_button.clicked.connect(self.save_venta_libre)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_venta_libre(self):
        # Obtener los valores ingresados
        monto = self.monto_input.text()
        concepto = self.concepto_input.text()
        fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Guardar fecha y hora actual

        # Validar que los campos no estén vacíos
        if not monto or not concepto:
            print("Error: Todos los campos son obligatorios.")
            return

        # Conectar a la base de datos y guardar la venta
        connection = sqlite3.connect('productos.db')
        cursor = connection.cursor()

        # Insertar los datos en la tabla de ventas
        cursor.execute('INSERT INTO ventas (fecha, total, concepto) VALUES (?, ?, ?)', (fecha_hora, monto, concepto))
        connection.commit()
        connection.close()

        # Actualizar el resumen financiero
        parent = self.parent()
        if isinstance(parent, MovimientosView):
            parent.resumen_financiero_view.update_resumen()

        # Cerrar el diálogo
        self.accept()

class GastoLibreDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gasto Libre")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Campo para el monto del gasto
        self.monto_label = QLabel("Monto del gasto:")
        self.monto_input = QLineEdit()
        self.monto_input.setPlaceholderText("Ingrese el monto")
        layout.addWidget(self.monto_label)
        layout.addWidget(self.monto_input)

        # Campo para el concepto del gasto
        self.concepto_label = QLabel("Concepto del gasto:")
        self.concepto_input = QLineEdit()
        self.concepto_input.setPlaceholderText("Ingrese el concepto")
        layout.addWidget(self.concepto_label)
        layout.addWidget(self.concepto_input)

        # Fecha y hora actual (no editable)
        self.fecha_hora_label = QLabel("Fecha y hora del gasto:")
        self.fecha_hora_input = QDateTimeEdit()
        self.fecha_hora_input.setDateTime(QDateTime.currentDateTime())
        self.fecha_hora_input.setEnabled(False)  # Deshabilitar edición de fecha y hora
        layout.addWidget(self.fecha_hora_label)
        layout.addWidget(self.fecha_hora_input)

        # Botón para guardar
        self.save_button = QPushButton("Guardar Gasto")
        self.save_button.clicked.connect(self.save_gasto_libre)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_gasto_libre(self):
        # Obtener los valores ingresados
        monto = self.monto_input.text()
        concepto = self.concepto_input.text()
        fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Guardar fecha y hora actual

        # Validar que los campos no estén vacíos
        if not monto or not concepto:
            print("Error: Todos los campos son obligatorios.")
            return

        # Conectar a la base de datos y guardar el gasto
        connection = sqlite3.connect('productos.db')
        cursor = connection.cursor()

        # Insertar los datos en la tabla de gastos (asegúrate de que la tabla exista)
        cursor.execute('INSERT INTO gastos (fecha, total, concepto) VALUES (?, ?, ?)', (fecha_hora, monto, concepto))
        connection.commit()
        connection.close()

        # Actualizar el resumen financiero
        parent = self.parent()
        if isinstance(parent, MovimientosView):
            parent.resumen_financiero_view.update_resumen()

        # Cerrar el diálogo
        self.accept()

class CompraInsumoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compra de Insumo")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Campo para seleccionar el producto
        self.producto_label = QLabel("Seleccionar producto:")
        self.producto_combo = QComboBox()
        self.producto_combo.addItems(self.get_productos())  # Cargar los productos desde la base de datos
        layout.addWidget(self.producto_label)
        layout.addWidget(self.producto_combo)

        # Campo para la cantidad a agregar
        self.cantidad_label = QLabel("Cantidad a agregar:")
        self.cantidad_input = QLineEdit()
        self.cantidad_input.setPlaceholderText("Ingrese la cantidad")
        layout.addWidget(self.cantidad_label)
        layout.addWidget(self.cantidad_input)

        # Botón para guardar
        self.save_button = QPushButton("Guardar Compra")
        self.save_button.clicked.connect(self.save_compra_insumo)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def get_productos(self):
        """Obtiene la lista de productos de la base de datos."""
        connection = sqlite3.connect('productos.db')
        cursor = connection.cursor()
        cursor.execute('SELECT name FROM products')  # Cambia a la columna que necesitas
        productos = [row[0] for row in cursor.fetchall()]
        connection.close()
        return productos

    def save_compra_insumo(self):
        # Obtener el producto seleccionado y la cantidad
        producto = self.producto_combo.currentText()
        cantidad = self.cantidad_input.text()

        # Validar que la cantidad no esté vacía
        if not cantidad:
            print("Error: La cantidad es obligatoria.")
            return

        # Convertir la cantidad a un entero
        cantidad = int(cantidad)

        # Actualizar el stock del producto en la base de datos
        self.update_stock(producto, cantidad)

        # Registrar el gasto en la base de datos
        self.registrar_gasto(producto, cantidad)

        # Cerrar el diálogo
        self.accept()

    def update_stock(self, producto, cantidad):
        """Actualiza el stock del producto en la base de datos."""
        connection = sqlite3.connect('productos.db')
        cursor = connection.cursor()

        # Obtener el stock actual
        cursor.execute('SELECT stock FROM products WHERE name = ?', (producto,))
        stock_actual = cursor.fetchone()[0]

        # Calcular el nuevo stock
        nuevo_stock = stock_actual + cantidad

        # Actualizar el stock en la base de datos
        cursor.execute('UPDATE products SET stock = ? WHERE name = ?', (nuevo_stock, producto))
        connection.commit()
        connection.close()

    def registrar_gasto(self, producto, cantidad):
        """Registra el gasto asociado a la compra de insumos."""
        fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        concepto = f"Compra de insumo: {producto}"
        total = cantidad * self.get_precio_compra(producto)

        # Insertar el gasto en la tabla de gastos
        connection = sqlite3.connect('productos.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO gastos (fecha, total, concepto) VALUES (?, ?, ?)', (fecha_hora, total, concepto))
        connection.commit()
        connection.close()

    def get_precio_compra(self, producto):
        """Obtiene el precio de compra del producto."""
        connection = sqlite3.connect('productos.db')
        cursor = connection.cursor()
        cursor.execute('SELECT purchase_price FROM products WHERE name = ?', (producto,))
        precio = cursor.fetchone()[0]
        connection.close()
        return precio
    



