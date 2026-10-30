from productos import pantalla_registrar, pantalla_listado, pantalla_editar
from productos import pantalla_baja, pantalla_alertas, pantalla_exportar_csv
from stock import pantalla_entrada, pantalla_salida

ACCIONES = {
    "1": pantalla_registrar,
    "2": pantalla_listado,
    "3": pantalla_entrada,
    "4": pantalla_salida,
    "5": pantalla_editar,
    "6": pantalla_baja,
    "7": pantalla_exportar_csv,
}


def menu():
    while True:
        try:
            pantalla_alertas()
        except Exception as error:
            print(f"Ocurrió un error con la base de datos: {error}")
        print("\nINVENTARIO PYMES")
        print("1. Registrar producto nuevo")
        print("2. Ver listado / buscar producto")
        print("3. Entrada de stock (llegó mercadería)")
        print("4. Salida de stock (venta)")
        print("5. Editar los datos de un producto")
        print("6. Dar de baja producto")
        print("7. Exportar inventario a CSV")
        print("0. Salir")
        opcion = input("Elige una opción: ").strip()

        if opcion == "0":
            print("Hasta luego.")
            break
        if opcion not in ACCIONES:
            print("Opción no válida.")
            continue
        try:
            ACCIONES[opcion]()
        except Exception as error:
            print(f"Ocurrió un error con la base de datos: {error}")


if __name__ == "__main__":
    menu()
