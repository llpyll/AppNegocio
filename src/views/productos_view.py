# Importaciones de PyQt6 y otros módulos necesarios
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit,
                             QDialog, QListWidget, QListWidgetItem, QMessageBox,
                             QLabel, QComboBox, QFileDialog, QGridLayout, QScrollArea, QFrame, 
                             QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap
from db.database import get_categories, add_category, delete_category, initialize_db, add_product, update_product_stock
import db.database as database
from PyQt6.QtCore import QFile, QTextStream


class ProductosView(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.category_dialog = None
        self.product_dialog = None

    # Inicializa la interfaz de usuario
    def initUI(self):
        layout = QVBoxLayout(self)

        # Sección de botones
        self.button_section = ButtonSection(self)
        layout.addLayout(self.button_section)

        # Añadir la lista de productos
        self.product_list = ListadeProductos()  # Instancia de ListadeProductos
        layout.addWidget(self.product_list)

        layout.addStretch()
        self.setLayout(layout)
        self.setGeometry(300, 300, 800, 600)  # Ajustar tamaño según necesidad
        self.setWindowTitle('Gestor de Productos')

    # Muestra el diálogo para agregar categorías
    def showCategoryDialog(self):
        if self.category_dialog is None:
            self.category_dialog = AddCategoryDialog(self)

        # Conectar la señal para actualizar el diálogo de productos cuando se agregue una categoría
        self.category_dialog.category_added.connect(self.updateProductCategories)

        self.category_dialog.update_category_list()
        self.category_dialog.exec()

    # Muestra el diálogo para agregar productos
    def showProductDialog(self):
        if self.product_dialog is None:
            self.product_dialog = AddProductDialog(self)

        self.product_dialog.exec()

    # Función para actualizar las categorías en AddProductDialog
    def updateProductCategories(self):
        if self.product_dialog is not None:
            self.product_dialog.populate_categories()


class ListadeProductos(QWidget):
    def __init__(self):
        super().__init__()
        initialize_db()  # Inicializar la base de datos
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.max_columns = 6
        self.init_ui()
        self.load_stylesheet()
        self.resizeEvent = self.on_resize

    def init_ui(self):
        top_layout = QHBoxLayout()
        self.total_references = QLabel("Total de referencias: 0")
        self.total_cost = QLabel("Costo total de inventario: Gs. 0")
        top_layout.addWidget(self.total_references)
        top_layout.addStretch()
        top_layout.addWidget(self.total_cost)
        self.layout.addLayout(top_layout)

        # Filters section
        filter_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.addItem("Ver todas las categorías")
        self.category_combo.addItems(database.get_categories())
        self.category_combo.currentIndexChanged.connect(self.filter_products)
        self.order_combo = QComboBox()
        self.order_combo.addItem("Ordenar: Productos más vendidos")
        filter_layout.addWidget(self.category_combo)
        filter_layout.addWidget(self.order_combo)
        self.layout.addLayout(filter_layout)

        # Products grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.load_products()

    def load_products(self, products=None):
        self.clear_products()
        if products is None:
            products = database.get_products()
        for index, product in enumerate(products):
            row = index // self.max_columns
            col = index % self.max_columns
            self.add_product(product, row, col)

        self.update_totals(products)

    def filter_products(self):
        selected_category = self.category_combo.currentText()
        if selected_category == "Ver todas las categorías":
            products = database.get_products()
        else:
            products = database.get_products_by_category(selected_category)

        self.load_products(products)

    def clear_products(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def add_product(self, product, row, col):
        product_widget = self.create_product_widget(product)
        self.grid_layout.addWidget(product_widget, row, col)

    def create_product_widget(self, product):
        name, image_path, price, stock = product
        widget = QFrame()
        widget.setFixedSize(150, 250)
        widget.setFrameShape(QFrame.Shape.Box)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        image_label = QLabel()
        image_label.setObjectName("image_label")
        pixmap = QPixmap(image_path)
        image_label.setPixmap(pixmap.scaled(140, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        price_label = QLabel(f"Gs. {price:,.0f}")
        price_label.setObjectName("price_label")
        layout.addWidget(price_label)

        name_label = QLabel(name)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        stock_label = QLabel(f"{stock} disponibles")
        stock_label.setObjectName("stock_label")
        layout.addWidget(stock_label)

        # Botón para editar producto
        edit_button = QPushButton("Editar")
        edit_button.clicked.connect(lambda: self.edit_product(name))
        layout.addWidget(edit_button)

        # Botón para eliminar producto
        delete_button = QPushButton("Eliminar")
        delete_button.clicked.connect(lambda: self.delete_product(name))
        layout.addWidget(delete_button)

        return widget

    def edit_product(self, name):
        product = database.get_product_by_name(name)
        if product:
            id, current_name, category, stock, purchase_price, sale_price, image_path = product
            edit_dialog = QDialog(self)
            edit_dialog.setWindowTitle("Editar producto")

            layout = QVBoxLayout(edit_dialog)

            # Nombre
            name_label = QLabel("Nombre:")
            name_edit = QLineEdit(current_name)
            layout.addWidget(name_label)
            layout.addWidget(name_edit)

            # Categoría
            category_label = QLabel("Categoría:")
            category_combo = QComboBox()
            category_combo.addItems(database.get_categories())
            category_combo.setCurrentText(category)
            layout.addWidget(category_label)
            layout.addWidget(category_combo)

            # Stock
            stock_label = QLabel("Stock:")
            stock_edit = QSpinBox()
            stock_edit.setMaximum(2147483647)
            stock_edit.setValue(int(stock))
            layout.addWidget(stock_label)
            layout.addWidget(stock_edit)

            # Precio de compra
            purchase_price_label = QLabel("Precio de compra:")
            purchase_price_edit = QDoubleSpinBox()
            purchase_price_edit.setMaximum(9999999999)
            purchase_price_edit.setValue(purchase_price)
            purchase_price_edit.setMaximum(9999999999)
            
            layout.addWidget(purchase_price_label)
            layout.addWidget(purchase_price_edit)

            # Precio de venta
            sale_price_label = QLabel("Precio de venta:")
            sale_price_edit = QDoubleSpinBox()
            sale_price_edit.setMaximum(9999999999)
            sale_price_edit.setValue(sale_price)
            sale_price_edit.setMaximum(9999999999)
            layout.addWidget(sale_price_label)
            layout.addWidget(sale_price_edit)

            # Imagen
            image_label = QLabel("Imagen:")
            image_button = QPushButton("Seleccionar imagen")
            image_preview = QLabel()
            pixmap = QPixmap(image_path)
            image_preview.setPixmap(pixmap.scaled(140, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            layout.addWidget(image_label)
            layout.addWidget(image_button)
            layout.addWidget(image_preview)

            def select_image():
                new_image_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)")
                if new_image_path:
                    pixmap = QPixmap(new_image_path)
                    image_preview.setPixmap(pixmap.scaled(140, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    image_preview.setProperty('image_path', new_image_path)

            image_button.clicked.connect(select_image)

            # Botón de guardar
            save_button = QPushButton("Guardar cambios")
            layout.addWidget(save_button)

            def save_changes():
                new_name = name_edit.text()
                new_category = category_combo.currentText()
                new_stock = stock_edit.value()
                new_purchase_price = purchase_price_edit.value()
                new_sale_price = sale_price_edit.value()
                new_image_path = image_preview.property('image_path') if image_preview.property('image_path') else image_path

                database.update_product(current_name, new_name, new_category, new_stock, new_purchase_price, new_sale_price, new_image_path)
                self.load_products()
                edit_dialog.accept()

            save_button.clicked.connect(save_changes)

            edit_dialog.exec()

    def delete_product(self, name):
        confirmation = QMessageBox.question(self, "Eliminar producto", f"¿Estás seguro de que deseas eliminar '{name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmation == QMessageBox.StandardButton.Yes:
            database.delete_product(name)
            self.load_products()

    def update_totals(self, products):
        total_references = len(products)
        total_cost = sum(product[2] * product[3] for product in products)
        self.total_references.setText(f"Total de referencias: {total_references}")
        self.total_cost.setText(f"Costo total de inventario: Gs. {total_cost:,.0f}")

    def load_stylesheet(self):
        with open("resources/listadeproductos.css", "r") as f:
            self.setStyleSheet(f.read())

    def on_resize(self, event):
        self.adjust_product_layout()

    def adjust_product_layout(self):
        width = self.width()
        column_width = 160
        self.max_columns = max(1, width // column_width)
        self.clear_products()
        self.load_products()


class ButtonSection(QHBoxLayout):
    def __init__(self, parent):
        super().__init__()

        self.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Botón para agregar productos
        self.add_product_button = QPushButton("Agregar Producto")
        self.add_product_button.setStyleSheet("""
            QPushButton {
                background-color: #90EE90;
                border-top-right-radius: 10px;
                padding: 10px;
            }
        """)
        self.add_product_button.clicked.connect(parent.showProductDialog)

        # Botón para agregar categorías
        self.add_category_button = QPushButton("Agregar Categoría")
        self.add_category_button.setStyleSheet("""
            QPushButton {
                background-color: #90EE90;
                border-top-right-radius: 10px;
                padding: 10px;
            }
        """)
        self.add_category_button.clicked.connect(parent.showCategoryDialog)

        # Agregar los botones al layout
        self.addWidget(self.add_product_button)
        self.addWidget(self.add_category_button)


# Diálogo para agregar categorías
class AddCategoryDialog(QDialog):
    # Definir la señal que será emitida cuando se agregue una categoría
    category_added = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  # Referencia al padre (ProductosView)
        self.setWindowTitle("Agregar Categoría")
        self.setGeometry(100, 100, 300, 400)

        layout = QVBoxLayout(self)

        # Campo de texto para ingresar el nombre de la categoría
        self.category_input = QLineEdit(placeholderText="Nombre de la categoría")
        layout.addWidget(self.category_input)

        # Lista de categorías existentes
        self.category_list = QListWidget()
        self.category_list.itemClicked.connect(self.on_item_clicked)
        self.update_category_list()
        layout.addWidget(self.category_list)

        # Botones para agregar y eliminar categorías
        button_layout = QHBoxLayout()
        add_button = QPushButton("Agregar")
        add_button.clicked.connect(self.add_category)
        button_layout.addWidget(add_button)

        delete_button = QPushButton("Eliminar")
        delete_button.clicked.connect(self.delete_category)
        button_layout.addWidget(delete_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    # Evento que resalta la categoría seleccionada en verde
    def on_item_clicked(self, item):
        item.setBackground(QColor(Qt.GlobalColor.green))

    # Función para agregar una categoría
    def add_category(self):
        category_name = self.category_input.text().strip()
        if category_name:
            try:
                add_category(category_name)  # Agrega la categoría a la base de datos
                self.category_input.clear()  # Limpia el campo de texto
                self.update_category_list()  # Actualiza la lista de categorías
                self.parent.product_dialog.populate_categories()  # Refresca las categorías en el diálogo de productos
                self.category_added.emit(category_name)  # Emitir la señal cuando se agregue una categoría
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Ocurrió un error al agregar la categoría: {str(e)}")
        else:
            QMessageBox.warning(self, "Advertencia", "El nombre de la categoría no puede estar vacío.")

    # Función para eliminar la categoría seleccionada
    def delete_category(self):
        selected_items = self.category_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Advertencia", "Seleccione una categoría para eliminar.")
            return

        for item in selected_items:
            category_name = item.text()
            delete_category(category_name)  # Eliminar la categoría de la base de datos
            self.update_category_list()  # Actualiza la lista de categorías
            self.parent.product_dialog.populate_categories()  # Refresca las categorías en el diálogo de productos

    # Función para actualizar la lista de categorías
    def update_category_list(self):
        self.category_list.clear()
        categories = get_categories()
        self.category_list.addItems(categories)


class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Agregar Producto")
        self.setGeometry(100, 100, 300, 400)

        # Cargar el archivo de estilo CSS
        self.load_stylesheet()

        layout = QVBoxLayout(self)

        # Campos para ingresar detalles del producto
        self.name_input = QLineEdit(placeholderText="Nombre del producto")
        layout.addWidget(self.name_input)

        self.category_combo = QComboBox()
        self.populate_categories()
        layout.addWidget(self.category_combo)

        self.quantity_input = QLineEdit(placeholderText="Cantidad")
        layout.addWidget(self.quantity_input)

        self.purchase_price_input = QLineEdit(placeholderText="Precio de compra (Gs.)")
        layout.addWidget(self.purchase_price_input)

        self.sale_price_input = QLineEdit(placeholderText="Precio de venta (Gs.)")
        layout.addWidget(self.sale_price_input)

        self.image_path = None
        self.image_label = QLabel(self)
        self.image_label.setObjectName("image_label")  # Para aplicar estilo CSS
        layout.addWidget(self.image_label)

        self.image_button = QPushButton("Seleccionar imagen")
        self.image_button.clicked.connect(self.select_image)
        layout.addWidget(self.image_button)

        self.add_button = QPushButton("Agregar Producto")
        self.add_button.clicked.connect(self.add_product)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def load_stylesheet(self):
        """Carga el archivo CSS desde la carpeta resources."""
        file = QFile("resources/addproduct.css")
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            self.setStyleSheet(stream.readAll())
        file.close()

    def populate_categories(self):
        """Rellena el combo box con las categorías desde la base de datos."""
        self.category_combo.clear()
        categories = database.get_categories()
        self.category_combo.addItems(categories)

    def select_image(self):
        """Permite al usuario seleccionar una imagen y la muestra en el QLabel."""
        self.image_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Imágenes (*.png *.jpg *.jpeg *.bmp)")
        if self.image_path:
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                self.image_label.setPixmap(pixmap.scaled(100, 100))
            else:
                QMessageBox.warning(self, "Error", "No se pudo cargar la imagen.")
        else:
            QMessageBox.warning(self, "Advertencia", "No se seleccionó ninguna imagen.")

    def add_product(self):
        """Valida la entrada y agrega el producto a la base de datos."""
        name = self.name_input.text().strip()
        category = self.category_combo.currentText()
        quantity = self.quantity_input.text().strip()
        purchase_price = self.purchase_price_input.text().strip()
        sale_price = self.sale_price_input.text().strip()

        if not all([name, category, quantity]):
            QMessageBox.warning(self, "Advertencia", "Nombre, categoría y cantidad son obligatorios.")
            return

        try:
            quantity = int(quantity)

            # Verificar si el producto ya existe con el mismo nombre, categoría, imagen, precios de compra y venta
            existing_product = database.get_product_by_name(name)

            if (existing_product and existing_product[2] == category and existing_product[4] == float(purchase_price)
                    and existing_product[5] == float(sale_price) and existing_product[6] == self.image_path):
                # Actualizar la cantidad del producto existente
                new_quantity = int(existing_product[3]) + quantity  # El stock está en la cuarta posición
                database.update_product_stock(name, new_quantity)
                QMessageBox.information(self, "Éxito", f"Stock actualizado para '{name}'. Nueva cantidad: {new_quantity}")
            else:
                # Crear un nuevo producto
                if not all([purchase_price, sale_price, self.image_path]):
                    QMessageBox.warning(self, "Advertencia", "Para nuevos productos, todos los campos son obligatorios.")
                    return

                try:
                    purchase_price = float(purchase_price)
                    sale_price = float(sale_price)
                except ValueError:
                    QMessageBox.warning(self, "Advertencia", "Los precios deben ser números válidos.")
                    return

                database.add_product(name, category, quantity, purchase_price, sale_price, self.image_path)
                QMessageBox.information(self, "Éxito", f"Nuevo producto '{name}' agregado con éxito.")

            self.close()
            if hasattr(self.parent, 'product_list') and hasattr(self.parent.product_list, 'load_products'):
                self.parent.product_list.load_products()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al procesar el producto: {str(e)}")


# Código para inicializar la aplicación
if __name__ == '__main__':
    import sys
    initialize_db()  # Inicializar la base de datos al inicio
    app = QApplication(sys.argv)
    window = ProductosView()
    window.show()
    sys.exit(app.exec())