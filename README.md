# DDL Validator

**DDL Validator** es un script en Python que analiza archivos DDL (Data Definition Language) y genera un informe detallado sobre la estructura de las tablas, sus claves primarias, claves foráneas e índices. El objetivo es identificar errores y advertencias comunes en el diseño de la base de datos y producir un reporte en texto o en formato HTML para su fácil lectura.

## Características

- Detecta tablas sin claves primarias.
- Verifica que las claves foráneas referencien columnas válidas en tablas relacionadas.
- Identifica columnas clave que no están indexadas.
- Reconoce posibles relaciones de uno a muchos y muchos a muchos.
- Genera un reporte en formato de texto o HTML, con colores distintivos para errores, advertencias e información adicional.

## Requisitos

- Python 3.6 o superior

## Instalación

1. Clona este repositorio del proyecto. 
```bash
git clone 
```
2. Asegúrate de instalar requirements.txt

## Uso

### Ejecución del Script

El script se ejecuta desde la línea de comandos y acepta como entrada el archivo DDL que deseas analizar.

```bash
python DDL_VALIDATOR.py <ruta/al/archivo_ddl.sql> --output <formato_de_salida>

```

### Output

El script generará un reporte con la siguiente información:

        1. Errores: problemas críticos, como tablas sin clave primaria o claves foráneas que refieren a columnas inexistentes (en rojo).
        2. Advertencias: problemas que podrían indicar deficiencias en el diseño, como columnas de claves no indexadas (en naranja).
        3. Información: datos útiles sobre la estructura, como posibles relaciones uno a muchos o muchos a muchos (en azul).
El reporte HTML será guardado en el archivo ddl_analysis_report.html en el mismo directorio en el que se ejecuta el script, a menos que se especifique otro directorio.
## Contribuciones
Las contribuciones son bienvenidas. Si deseas mejorar este script, por favor abre un issue o envía un pull request.
## Licencia