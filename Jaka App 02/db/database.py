import sqlite3
from datetime import datetime

# Inicializa la base de datos
def initialize_db():
    connection = sqlite3.connect('productos.db')
    cursor = connection.cursor()

    # Crear tabla de categorías
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    ''')

    # Crear tabla de productos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        stock INTEGER NOT NULL,
        purchase_price REAL NOT NULL,
        sale_price REAL NOT NULL,
        image_path TEXT
    )
    ''')

    # Crear tabla de ventas con el nuevo campo 'concepto'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        total REAL NOT NULL,
        concepto TEXT NOT NULL  -- Campo agregado para el concepto de la venta
    )
    ''')

    # Crear tabla de detalles de ventas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ventas_detalles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER NOT NULL,
        producto_name TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (venta_id) REFERENCES ventas(id)
    )
    ''')

    # Crear tabla de gastos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        total REAL NOT NULL,
        concepto TEXT NOT NULL
    )
    ''')

    # Si la tabla 'ventas' ya existe, agregar la columna 'concepto' si no está presente
    try:
        cursor.execute('ALTER TABLE ventas ADD COLUMN concepto TEXT')
    except sqlite3.OperationalError:
        # La columna ya existe
        pass

    connection.commit()
    connection.close()

# Función para agregar una nueva venta
def add_venta(fecha, total, concepto, items):
    connection = sqlite3.connect('productos.db')
    cursor = connection.cursor()
    # Insertar en la tabla de ventas con el concepto
    cursor.execute('INSERT INTO ventas (fecha, total, concepto) VALUES (?, ?, ?)', (fecha, total, concepto))
    venta_id = cursor.lastrowid

    # Insertar los detalles de la venta
    for item in items:
        producto_name, subtotal = item.split(' - Gs. ')
        cantidad = 1  # Asumimos cantidad 1 por cada item agregado a la canasta
        cursor.execute('INSERT INTO ventas_detalles (venta_id, producto_name, cantidad, subtotal) VALUES (?, ?, ?, ?)',
                       (venta_id, producto_name, cantidad, float(subtotal.replace(',', ''))))

    connection.commit()
    connection.close()

# Función para agregar una categoría
def add_category(category_name):
    connection = sqlite3.connect('productos.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO categories (name) VALUES (?)', (category_name,))
    connection.commit()
    connection.close()

# Función para obtener todas las categorías
def get_categories():
    connection = sqlite3.connect('productos.db')
    cursor = connection.cursor()
    cursor.execute('SELECT name FROM categories')
    categories = [row[0] for row in cursor.fetchall()]
    connection.close()
    return categories

# Función para eliminar una categoría
def delete_category(category_name):
    connection = sqlite3.connect('productos.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM categories WHERE name = ?', (category_name,))
    connection.commit()
    connection.close()

# Función para agregar un producto
def add_product(name, category, stock, purchase_price, sale_price, image_path):
    connection = sqlite3.connect('productos.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO products (name, category, stock, purchase_price, sale_price, image_path) VALUES (?, ?, ?, ?, ?, ?)',
                   (name, category, stock, purchase_price, sale_price, image_path))
    connection.commit()
    connection.close()

# Función para obtener todos los productos
def get_products():
    connection = sqlite3.connect('productos.db')
    cursor = connection.cursor()
    cursor.execute('SELECT name, image_path, sale_price, stock FROM products')
    products = cursor.fetchall()
    connection.close()
    return products

# Función para obtener productos por categoría
def get_products_by_category(category):
    connection = sqlite3.connect('productos.db')
    cursor = connection.cursor()
    cursor.execute('SELECT name, image_path, sale_price, stock FROM products WHERE category = ?', (category,))
    products = cursor.fetchall()
    connection.close()
    return products

# Función para obtener un producto por su nombre
def get_product_by_name(name):
    connection = sqlite3.connect('productos.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM products WHERE name = ?', (name,))
    product = cursor.fetchone()
    connection.close()
    return product

# Función para actualizar el stock de un producto
def update_product_stock(name, new_quantity):
    with sqlite3.connect('productos.db') as connection:
        cursor = connection.cursor()
        cursor.execute('UPDATE products SET stock = ? WHERE name = ?', (new_quantity, name))
        connection.commit()

# Función para actualizar los detalles de un producto
def update_product(name, new_name, new_category, new_stock, new_purchase_price, new_sale_price, new_image_path):
    connection = sqlite3.connect('productos.db')
    cursor = connection.cursor()
    cursor.execute('''UPDATE products SET name = ?, category = ?, stock = ?, purchase_price = ?, sale_price = ?, image_path = ? WHERE name = ?''',
                   (new_name, new_category, new_stock, new_purchase_price, new_sale_price, new_image_path, name))
    connection.commit()
    connection.close()

# Función para eliminar un producto
def delete_product(name):
    connection = sqlite3.connect('productos.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM products WHERE name = ?', (name,))
    connection.commit()
    connection.close()

# Nueva función para agregar una venta libre
def add_venta_libre(total, concepto):
    # Obtener la fecha y hora actuales
    fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    connection = sqlite3.connect('productos.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO gastos (fecha, total, concepto) VALUES (?, ?, ?)', (fecha_hora, total, concepto))
    connection.commit()
    connection.close()
