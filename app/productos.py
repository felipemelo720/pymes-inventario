import csv
from contextlib import closing

from conexion import obtener_conexion


def consultar_uno(conexion, sql, parametros=()):
    cursor = conexion.cursor()
    cursor.execute(sql, parametros)
    fila = cursor.fetchone()
    cursor.close()
    return fila


def consultar_todos(conexion, sql, parametros=()):
    cursor = conexion.cursor()
    cursor.execute(sql, parametros)
    filas = cursor.fetchall()
    cursor.close()
    return filas


def ejecutar(conexion, sql, parametros=()):
    cursor = conexion.cursor()
    cursor.execute(sql, parametros)
    conexion.commit()
    cursor.close()


def existe_sku(conexion, sku):
    return consultar_uno(conexion, "SELECT id FROM productos WHERE sku = %s", (sku,)) is not None


def registrar_producto(conexion, sku, nombre, categoria, stock_inicial, stock_minimo):
    if not sku or not nombre or not categoria:
        return False, "Faltan datos: nombre, código y categoría son obligatorios."
    if stock_inicial is None or stock_minimo is None:
        return False, "Faltan datos: stock inicial y stock mínimo son obligatorios."
    if stock_inicial < 0 or stock_minimo < 0:
        return False, "El stock no puede ser negativo."
    if existe_sku(conexion, sku):
        return False, f"Ya existe un producto con el código {sku}."

    ejecutar(
        conexion,
        "INSERT INTO productos (sku, nombre, categoria, stock_actual, stock_minimo) VALUES (%s, %s, %s, %s, %s)",
        (sku, nombre, categoria, stock_inicial, stock_minimo),
    )
    return True, f"Producto '{nombre}' registrado correctamente."


def listar_productos(conexion, busqueda=""):
    patron = "%" + busqueda + "%"
    return consultar_todos(
        conexion,
        "SELECT sku, nombre, categoria, stock_actual, stock_minimo FROM productos "
        "WHERE activo = 1 AND (nombre LIKE %s OR sku LIKE %s) ORDER BY nombre",
        (patron, patron),
    )


def buscar_producto_activo(conexion, sku):
    return consultar_uno(
        conexion,
        "SELECT id, sku, nombre, categoria, stock_minimo FROM productos WHERE sku = %s AND activo = 1",
        (sku,),
    )


def sku_usado_por_otro(conexion, sku, producto_id):
    fila = consultar_uno(conexion, "SELECT id FROM productos WHERE sku = %s AND id != %s", (sku, producto_id))
    return fila is not None


def editar_producto(conexion, sku_actual, nuevo_sku, nombre, categoria, stock_minimo):
    if not nuevo_sku or not nombre or not categoria:
        return False, "No se permiten campos vacíos: código, nombre y categoría son obligatorios."
    if stock_minimo is None:
        return False, "No se permiten campos vacíos: el stock mínimo es obligatorio."
    if stock_minimo < 0:
        return False, "El stock mínimo no puede ser negativo."

    producto = buscar_producto_activo(conexion, sku_actual)
    if producto is None:
        return False, f"No existe un producto activo con el código {sku_actual}."
    producto_id = producto[0]

    if sku_usado_por_otro(conexion, nuevo_sku, producto_id):
        return False, f"Ya existe otro producto con el código {nuevo_sku}."

    ejecutar(
        conexion,
        "UPDATE productos SET sku = %s, nombre = %s, categoria = %s, stock_minimo = %s WHERE id = %s",
        (nuevo_sku, nombre, categoria, stock_minimo, producto_id),
    )
    return True, f"Producto '{nombre}' actualizado correctamente."


def dar_de_baja_producto(conexion, sku, confirmado):
    if not confirmado:
        return False, "Operación cancelada. No se hizo ningún cambio."

    producto = buscar_producto_activo(conexion, sku)
    if producto is None:
        return False, f"No existe un producto activo con el código {sku}."

    ejecutar(conexion, "UPDATE productos SET activo = 0 WHERE id = %s", (producto[0],))
    return True, f"Producto '{producto[2]}' dado de baja. Ya no aparecerá en el listado."


def productos_bajo_stock(conexion):
    return consultar_todos(
        conexion,
        "SELECT sku, nombre, stock_actual, stock_minimo FROM productos "
        "WHERE activo = 1 AND stock_actual <= stock_minimo ORDER BY nombre",
    )


def mostrar_alertas(productos):
    if len(productos) == 0:
        return
    print("\n--- ALERTA: productos con stock bajo ---")
    for producto in productos:
        print(f"  {producto[1]} ({producto[0]}): quedan {producto[2]} y el mínimo es {producto[3]}.")


def pantalla_alertas():
    with closing(obtener_conexion()) as conexion:
        productos = productos_bajo_stock(conexion)
    mostrar_alertas(productos)


def exportar_inventario_csv(conexion, ruta):
    productos = listar_productos(conexion)
    try:
        with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.writer(archivo, delimiter=";")
            escritor.writerow(["Código", "Nombre", "Categoría", "Stock", "Mínimo"])
            escritor.writerows(productos)
    except OSError:
        return False, f"No se pudo escribir el archivo {ruta}."
    return True, f"Inventario exportado a '{ruta}' ({len(productos)} productos)."


def mostrar_resultado(ok, mensaje):
    print(("OK: " if ok else "ERROR: ") + mensaje)


def pedir_entero(mensaje):
    try:
        return int(input(mensaje).strip())
    except ValueError:
        return None


def mostrar_tabla(productos):
    if len(productos) == 0:
        print("No se encontraron productos.")
        return
    print("\nCÓDIGO | NOMBRE | CATEGORÍA | STOCK | MÍNIMO")
    print("-" * 50)
    for sku, nombre, categoria, stock, minimo in productos:
        aviso = "  <- bajo mínimo" if stock <= minimo else ""
        print(sku, "|", nombre, "|", categoria, "|", stock, "|", minimo, aviso)
    print()


def pantalla_registrar():
    print("\n--- Registrar producto nuevo ---")
    sku = input("Código (SKU): ").strip()
    nombre = input("Nombre: ").strip()
    categoria = input("Categoría: ").strip()
    stock_inicial = pedir_entero("Stock inicial: ")
    stock_minimo = pedir_entero("Stock mínimo: ")
    with closing(obtener_conexion()) as conexion:
        ok, mensaje = registrar_producto(conexion, sku, nombre, categoria, stock_inicial, stock_minimo)
    mostrar_resultado(ok, mensaje)


def pantalla_listado():
    print("\n--- Listado de productos ---")
    busqueda = input("Buscar por nombre o código (Enter para ver todos): ").strip()
    with closing(obtener_conexion()) as conexion:
        productos = listar_productos(conexion, busqueda)
    mostrar_tabla(productos)


def pedir_texto_o_actual(mensaje, actual):
    return input(f"{mensaje} [{actual}]: ").strip() or actual


def pantalla_editar():
    print("\n--- Editar producto ---")
    sku_actual = input("Código (SKU) del producto a editar: ").strip()
    with closing(obtener_conexion()) as conexion:
        producto = buscar_producto_activo(conexion, sku_actual)
        if producto is None:
            print(f"ERROR: No existe un producto activo con el código {sku_actual}.")
            return

        print("Escribe el dato nuevo, o presiona Enter para dejar el actual.")
        nuevo_sku = pedir_texto_o_actual("Código (SKU)", producto[1])
        nuevo_nombre = pedir_texto_o_actual("Nombre", producto[2])
        nueva_categoria = pedir_texto_o_actual("Categoría", producto[3])
        texto_minimo = pedir_texto_o_actual("Stock mínimo", producto[4])
        try:
            nuevo_minimo = int(texto_minimo)
        except ValueError:
            nuevo_minimo = None

        ok, mensaje = editar_producto(conexion, producto[1], nuevo_sku, nuevo_nombre, nueva_categoria, nuevo_minimo)
    mostrar_resultado(ok, mensaje)


def pantalla_baja():
    print("\n--- Dar de baja producto ---")
    sku = input("Código (SKU) del producto a dar de baja: ").strip()
    with closing(obtener_conexion()) as conexion:
        producto = buscar_producto_activo(conexion, sku)
        if producto is None:
            print(f"ERROR: No existe un producto activo con el código {sku}.")
            return

        respuesta = input(f"¿Seguro que quieres dar de baja '{producto[2]}'? (s/n): ").strip()
        ok, mensaje = dar_de_baja_producto(conexion, sku, respuesta.lower() == "s")
    mostrar_resultado(ok, mensaje)


def pantalla_exportar_csv():
    print("\n--- Exportar inventario a CSV ---")
    ruta = input("Archivo de destino [inventario.csv]: ").strip() or "inventario.csv"
    with closing(obtener_conexion()) as conexion:
        ok, mensaje = exportar_inventario_csv(conexion, ruta)
    mostrar_resultado(ok, mensaje)
