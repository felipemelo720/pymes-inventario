# Inventario ligero para Pymes

Aplicación de terminal en Python y MySQL para controlar el inventario de una pyme: productos, entradas y salidas de stock, alertas de stock bajo y exportación a CSV.

Proyecto del ramo Metodología Ágil, INACAP (Scrum, octubre 2026).

## Funcionalidades

- Registrar, editar y dar de baja productos (baja lógica, se conserva el historial).
- Listar y buscar productos por nombre o código (SKU).
- Entrada de stock (llegó mercadería) y salida de stock (venta). La salida no permite stock negativo.
- Alerta automática de productos con stock menor o igual al mínimo.
- Exportar el inventario a CSV (separador `;`, compatible con Excel).

## Requisitos

- Python 3.8 o superior
- MySQL 8.0.16+ o MariaDB 10.4+
- `mysql-connector-python`

## Instalación

```bash
git clone https://github.com/felipemelo720/pymes-inventario.git
cd pymes-inventario
pip install mysql-connector-python

Crear la base de datos inventario_pymes (incluye 4 productos de prueba):

mysql -u root -p < db/inventario_pymes.sql

Este script borra las tablas productos y movimientos si ya existen. No lo ejecutes sobre una base con datos que quieras conservar.

Configuración

La conexión se configura con variables de entorno. Valores por defecto entre paréntesis:

- DB_HOST: servidor (localhost)
- DB_PORT: puerto (3306)
- DB_USER: usuario (root)
- DB_PASSWORD: contraseña (vacía)

export DB_USER=root
export DB_PASSWORD=tu_contraseña

El nombre de la base de datos (inventario_pymes) está fijo en app/conexion.py y no se configura por variable de entorno.

No guardes contraseñas en el código.

Uso

cd app
python main.py

Opciones del menú:

- 1: Registrar producto nuevo
- 2: Ver listado / buscar producto
- 3: Entrada de stock (llegó mercadería)
- 4: Salida de stock (venta)
- 5: Editar los datos de un producto
- 6: Dar de baja producto
- 7: Exportar inventario a CSV
- 0: Salir

Al exportar, el archivo por defecto es inventario.csv. La ruta es relativa a la carpeta desde donde ejecutas el programa (app/ si sigues los pasos de arriba).

Estructura

- app/conexion.py: conexión a MySQL.
- app/main.py: menú principal.
- app/productos.py: CRUD, listado, alertas y CSV.
- app/stock.py: entradas y salidas de stock.
- db/inventario_pymes.sql: esquema y datos de prueba.
- .github/workflows/ci.yml: CI que instala dependencias y compila en cada push.

Base de datos

La tabla productos guarda id, sku (único), nombre, categoria, stock_actual, stock_minimo y activo.

La tabla movimientos guarda id, producto_id (FK a productos), tipo (entrada o salida), cantidad y fecha.

Las restricciones CHECK impiden stock y cantidades negativas.

CI

GitHub Actions ejecuta en cada push la instalación de dependencias y python -m compileall app.

Equipo

- Product Owner: Anastasia Fuentes
- Scrum Master: José Oporto
- Desarrolladores: Antonella Pezzopane, Benjamín Ceballos y Felipe Melo
