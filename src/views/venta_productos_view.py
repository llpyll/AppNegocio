from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QGridLayout, QMessageBox, QLineEdit
from PyQt6.QtGui import QPixmap, QIntValidator
from PyQt6.QtCore import Qt

from db.database import get_products, get_product_by_name
import sqlite3
from datetime import datetime
from functools import partial

class VentasProductosView(QWidget):
    def __init__(self):
        super().__init__()
        self.carrito = {}
        self.stock_disponible = {}  # Diccionario para manejar el stock disponible temporal
        
        # Inicializa la UI después de inicializar las variables
        self.initUI()
        self.cargar_productos_view = CargarProductos(self)
        self.cargar_productos_view.cargar_productos()

    def initUI(self):
        layout = QHBoxLayout()

        # Área de productos
        self.productos_widget = QWidget()
        self.productos_layout = QGridLayout()
        self.productos_widget.setLayout(self.productos_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.productos_widget)

        layout.addWidget(scroll, 2)

        # Área del carrito
        carrito_widget = QWidget()
        carrito_layout = QVBoxLayout()

        # Crear un layout para los items del carrito
        self.carrito_lista = QWidget()
        self.carrito_lista.setLayout(QVBoxLayout())
        carrito_layout.addWidget(self.carrito_lista)

        self.total_label = QLabel("Total: Gs. 0")
        carrito_layout.addWidget(self.total_label)

        self.btn_concretar_venta = QPushButton("Concretar Venta")
        carrito_layout.addWidget(self.btn_concretar_venta)

        carrito_widget.setLayout(carrito_layout)
        layout.addWidget(carrito_widget, 1)

        self.setLayout(layout)

        # Conectar el botón concretar_venta al método
        self.btn_concretar_venta.clicked.connect(self.concretar_venta)

        # Estilos para mejorar la apariencia
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                padding: 5px;
                font-size: 14px;
            }
        """)

    def concretar_venta(self):
        if not self.carrito:
            QMessageBox.warning(self, "Carrito vacío", "No hay productos en el carrito")
            return

        # Confirmación de venta
        confirm = QMessageBox.question(self, "Confirmar Venta", "¿Está seguro de que desea concretar esta venta?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.No:
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = sum(datos['precio'] * datos['cantidad'] for datos in self.carrito.values())
        concepto = "Venta de insumos"

        try:
            with sqlite3.connect('productos.db') as connection:
                cursor = connection.cursor()
                # Agregar venta a la base de datos
                cursor.execute('INSERT INTO ventas (fecha, total, concepto) VALUES (?, ?, ?)', (fecha, total, concepto))
                venta_id = cursor.lastrowid

                # Insertar detalles de venta y actualizar el stock en una sola transacción
                for nombre, datos in self.carrito.items():
                    producto = get_product_by_name(nombre)
                    if producto:
                        nuevo_stock = producto[3] - datos['cantidad']
                        cursor.execute('INSERT INTO ventas_detalles (venta_id, producto_name, cantidad, subtotal) VALUES (?, ?, ?, ?)',
                                       (venta_id, nombre, datos['cantidad'], datos['precio'] * datos['cantidad']))
                        cursor.execute('UPDATE products SET stock = ? WHERE name = ?', (nuevo_stock, nombre))

                connection.commit()

            QMessageBox.information(self, "Venta realizada", "La venta se ha registrado correctamente")
            
            # Limpiar carrito y actualizar vista
            self.carrito.clear()
            self.actualizar_carrito()
            self.cargar_productos_view.cargar_productos()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error inesperado: {str(e)}")

    def actualizar_carrito(self):
        funciones_carrito = FuncionesCarrito(self)
        funciones_carrito.actualizar_carrito()

    def modificar_cantidad(self, cantidad_input, cambio, nombre):
        funciones_carrito = FuncionesCarrito(self)
        funciones_carrito.modificar_cantidad(cantidad_input, cambio, nombre)

    def agregar_al_carrito(self, nombre, precio, stock_label, cantidad_input):
        funciones_carrito = FuncionesCarrito(self)
        funciones_carrito.agregar_al_carrito(nombre, precio, stock_label, cantidad_input)


class FuncionesCarrito:
    def __init__(self, vista):
        self.vista = vista

    def modificar_cantidad(self, cantidad_input, cambio, nombre):
        try:
            cantidad_actual = int(cantidad_input.text())
            nueva_cantidad = cantidad_actual + cambio
            # Verificar que la nueva cantidad no sea menor que 1 ni mayor que el stock disponible
            if 1 <= nueva_cantidad <= self.vista.stock_disponible[nombre]:
                cantidad_input.setText(str(nueva_cantidad))
        except ValueError:
            pass

    def agregar_al_carrito(self, nombre, precio, stock_label, cantidad_input):
        try:
            cantidad = int(cantidad_input.text()) if cantidad_input.text() else 1
        except ValueError:
            QMessageBox.warning(self.vista, "Cantidad inválida", "Por favor, ingrese una cantidad válida.")
            return
        
        # Verificar si hay suficiente stock disponible
        if nombre in self.vista.stock_disponible and self.vista.stock_disponible[nombre] >= cantidad:
            if nombre in self.vista.carrito:
                # Incrementar la cantidad del producto en el carrito
                self.vista.carrito[nombre]['cantidad'] += cantidad
            else:
                # Si no está en el carrito, agregarlo
                self.vista.carrito[nombre] = {'precio': precio, 'cantidad': cantidad}

            # Reducir el stock disponible después de añadir el producto al carrito
            self.vista.stock_disponible[nombre] -= cantidad

            # Actualizar la etiqueta de stock del producto
            stock_label.setText(f"Stock: {self.vista.stock_disponible[nombre]}")
            
            # Actualizar el contenido del carrito
            self.actualizar_carrito()
        else:
            QMessageBox.warning(self.vista, "Stock insuficiente", f"No hay suficiente stock disponible de {nombre}")

    def actualizar_carrito(self):
        # Limpiar el layout del carrito antes de agregar los nuevos elementos
        layout = self.vista.carrito_lista.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())

        total = 0
        for nombre, datos in self.vista.carrito.items():
            subtotal = datos['precio'] * datos['cantidad']
            total += subtotal

            # Crear layout horizontal para cada producto del carrito
            item_layout = QHBoxLayout()

            # Etiqueta con el nombre del producto y la cantidad
            texto_item = QLabel(f"{nombre} x{datos['cantidad']} - Gs. {subtotal:,.0f}")
            item_layout.addWidget(texto_item)

            # Botón para quitar el producto del carrito completamente
            btn_quitar = QPushButton("Eliminar")
            btn_quitar.clicked.connect(partial(self.quitar_del_carrito, nombre))
            item_layout.addWidget(btn_quitar)

            # Agregar el layout al carrito
            layout.addLayout(item_layout)

        self.vista.total_label.setText(f"Total: Gs. {total:,.0f}")

    def quitar_del_carrito(self, nombre):
        # Confirmar antes de eliminar el producto del carrito
        confirm = QMessageBox.question(self.vista, "Eliminar Producto", f"¿Está seguro de que desea eliminar {nombre} del carrito?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.No:
            return

        if nombre in self.vista.carrito:
            # Restablecer el stock disponible del producto al eliminarlo del carrito
            cantidad_a_quitar = self.vista.carrito[nombre]['cantidad']
            self.vista.stock_disponible[nombre] += cantidad_a_quitar
            del self.vista.carrito[nombre]  # Eliminar el producto del carrito

            # Actualizar el stock en la etiqueta de stock del producto
            for i in range(self.vista.productos_layout.count()):
                producto_widget = self.vista.productos_layout.itemAt(i).widget()
                nombre_producto = producto_widget.layout().itemAt(1).widget().text()
                if nombre_producto == nombre:
                    stock_label = producto_widget.layout().itemAt(3).widget()
                    stock_label.setText(f"Stock: {self.vista.stock_disponible[nombre]}")
                    break

        # Actualizar el carrito después de eliminar el producto
        self.actualizar_carrito()

    def clear_layout(self, layout):
        # Método para limpiar recursivamente todos los widgets dentro de un layout
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())


class CargarProductos:
    def __init__(self, vista):
        self.vista = vista

    def cargar_productos(self):
        productos = get_products()
        row = 0
        col = 0
        for producto in productos:
            nombre, imagen_path, precio, stock = producto
            self.vista.stock_disponible[nombre] = stock  # Guardar el stock disponible inicial
            
            producto_widget = QWidget()
            producto_layout = QVBoxLayout()

            imagen_label = QLabel()
            pixmap = QPixmap(imagen_path)
            imagen_label.setPixmap(pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            producto_layout.addWidget(imagen_label)

            nombre_label = QLabel(nombre)
            producto_layout.addWidget(nombre_label)

            precio_label = QLabel(f"Gs. {precio:,.0f}")
            producto_layout.addWidget(precio_label)

            stock_label = QLabel(f"Stock: {stock}")
            producto_layout.addWidget(stock_label)

            # Layout horizontal para los controles de cantidad
            cantidad_layout = QHBoxLayout()

            # Botón para disminuir la cantidad
            btn_menos = QPushButton("-")
            cantidad_input = QLineEdit("1")  # Valor inicial de cantidad
            cantidad_input.setFixedWidth(40)
            cantidad_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cantidad_input.setValidator(QIntValidator(1, stock))  # Hacer que el campo sea editable y validar la cantidad

            # Botón para aumentar la cantidad
            btn_mas = QPushButton("+")

            # Funciones para modificar la cantidad
            btn_menos.clicked.connect(partial(self.vista.modificar_cantidad, cantidad_input, -1, nombre))
            btn_mas.clicked.connect(partial(self.vista.modificar_cantidad, cantidad_input, 1, nombre))

            cantidad_layout.addWidget(btn_menos)
            cantidad_layout.addWidget(cantidad_input)
            cantidad_layout.addWidget(btn_mas)
            producto_layout.addLayout(cantidad_layout)

            btn_agregar = QPushButton("Agregar al Carrito")
            btn_agregar.clicked.connect(partial(self.vista.agregar_al_carrito, nombre, precio, stock_label, cantidad_input))
            producto_layout.addWidget(btn_agregar)

            producto_widget.setLayout(producto_layout)
            self.vista.productos_layout.addWidget(producto_widget, row, col)

            col += 1
            if col > 2:
                col = 0
                row += 1
