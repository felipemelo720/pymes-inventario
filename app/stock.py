from contextlib import closing

from conexion import obtener_conexion
from productos import mostrar_resultado, pedir_entero


def buscar_por_sku(conexion, sku):
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, stock_actual FROM productos WHERE sku = %s AND activo = 1", (sku,))
    fila = cursor.fetchone()
    cursor.close()
    return fila


def entrada_stock(conexion, sku, cantidad):
    if cantidad is None or cantidad <= 0:
        return False, "La cantidad debe ser un número mayor que 0."
    producto = buscar_por_sku(conexion, sku)
    if producto is None:
        return False, f"No existe un producto con el código {sku}."
    producto_id = producto[0]
    nombre = producto[1]
    stock_actual = producto[2]

    cursor = conexion.cursor()
    cursor.execute("UPDATE productos SET stock_actual = stock_actual + %s WHERE id = %s", (cantidad, producto_id))
    cursor.execute(
        "INSERT INTO movimientos (producto_id, tipo, cantidad) VALUES (%s, 'entrada', %s)",
        (producto_id, cantidad),
    )
    conexion.commit()
    cursor.close()
    nuevo = stock_actual + cantidad
    return True, f"Entrada registrada. '{nombre}': {stock_actual} -> {nuevo} unidades."


def salida_stock(conexion, sku, cantidad):
    if cantidad is None or cantidad <= 0:
        return False, "La cantidad debe ser un número mayor que 0."
    producto = buscar_por_sku(conexion, sku)
    if producto is None:
        return False, f"No existe un producto con el código {sku}."
    producto_id = producto[0]
    nombre = producto[1]
    stock_actual = producto[2]
    if cantidad > stock_actual:
        return False, f"No hay stock suficiente. '{nombre}' tiene {stock_actual} unidades y se intentó sacar {cantidad}. El stock no cambió."

    cursor = conexion.cursor()
    # el WHERE evita stock negativo si otra venta llegó entre la lectura y este UPDATE
    cursor.execute(
        "UPDATE productos SET stock_actual = stock_actual - %s WHERE id = %s AND stock_actual >= %s",
        (cantidad, producto_id, cantidad),
    )
    if cursor.rowcount == 0:
        cursor.close()
        return False, f"No hay stock suficiente para '{nombre}'. El stock no cambió."
    cursor.execute(
        "INSERT INTO movimientos (producto_id, tipo, cantidad) VALUES (%s, 'salida', %s)",
        (producto_id, cantidad),
    )
    conexion.commit()
    cursor.close()
    nuevo = stock_actual - cantidad
    return True, f"Salida registrada. '{nombre}': {stock_actual} -> {nuevo} unidades."


def pantalla_entrada():
    print("\n--- Entrada de stock (llegó mercadería) ---")
    sku = input("Código (SKU) del producto: ").strip()
    cantidad = pedir_entero("Cantidad: ")
    with closing(obtener_conexion()) as conexion:
        ok, mensaje = entrada_stock(conexion, sku, cantidad)
    mostrar_resultado(ok, mensaje)


def pantalla_salida():
    print("\n--- Salida de stock (venta) ---")
    sku = input("Código (SKU) del producto: ").strip()
    cantidad = pedir_entero("Cantidad: ")
    with closing(obtener_conexion()) as conexion:
        ok, mensaje = salida_stock(conexion, sku, cantidad)
    mostrar_resultado(ok, mensaje)
