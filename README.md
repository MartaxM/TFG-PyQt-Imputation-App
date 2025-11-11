# TFG-PyQt-Imputation-App

Esta herramienta de código abierto permite la visualización, a través de una interfaz gráfica de usuario creada utilizando la biblioteca PyQT5, de series temporales obtenidas de un sensor móvil de partículas en suspensión y la imputación de valores faltantes utilizando uno de seis algoritmos. La herramienta posee otras funciones de manipulación como la creación de una serie temporal con valores perdidos a partir de una original, de forma que se puede comparar el resultado de la imputación y la serie temporal original, y asi estudiar la efectividad de la imputación.

## Documentación
En la carpeta "/documentation" se puede encontrar la memoria y el manual de uso.

## Código
El código fuente se encuentra en la carpeta "/src". Se puede ejecutar, teniendo python instalado, desde la consola utilizando el comando: `pytest app.py` (versión sin pantalla de carga) o `pytest launcher.py` (con pantalla de carga).

### Dependencias
Este proyecto tiene las siguientes dependencias en "requirements.txt":
- folium==0.19.4 : Visualización en mapa
- matplotlib==3.8.4 : Visualización en gráfico de líneas
- numpy==2.3.4 : Manipulación de datos
- pandas==2.3.3 : Almacenaje y manipulación de series
- pypots==1.0 : Utilizar los métodos de imputación SAITS y TRANSFORMERS
- PyQt5==5.15.11 : GUI
- PyQt5_sip==12.17.0 : GUI

Además se hace uso de *pyinstaller* para la compilación y *pytest* para las pruebas automatizadas.

### Aplicación compilada
En "/src/dist" se puede encontrar la aplicación portable para windows almacenada en un archivo .rar, que contiene un exe y una carpeta, ya compilada utilizando el comando:

```bash
pyinstaller launcher.py --name windows_tool --noconfirm --add-data "config.ini;." --add-data "assets/loadingSplash.png;assets" --add-data "assets/loadingAnimation.gif;assets" --hidden-import tsdb.utils.file --hidden-import pygrinder.block_missing.block_missing --hidden-import pypots.imputation.brits.model --hidden-import pypots.imputation.saits --collect-all tsdb --collect-all pypots --collect-all pygrinder
```

Esto, además de generar el ejectuable y la carpeta "_internal" que necesita para correr, genera un archivo .spec, de forma que `pyinstaller windows_tool.spec` permite reproducir la compilación.

## Pruebas
Las pruebas automatizadas se encuentran en "/tests". Las pruebas unitarias de caja blanca del modelo se encuentran en los archivos de la carpeta "/unit", mientras que las pruebas de integración entre el modelo-vista-controlador de caja negra se encuentran en "/integration".

Para ejecutarlas se hace uso del comando:
`pytest [ruta de la prueba]`.