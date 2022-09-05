# allsky_TFG
Desde la superficie terrestre es posible observar meteoros o “estrellas 
fugaces”, como se les conoce popularmente. Para registrar estos fenómenos suelen 
usarse cámaras all-sky, que debido a su gran ángulo de visión son ideales para 
observar la bóveda celeste. Sin embargo, la cámara es incapaz de reconocer y 
diferenciar los objetos capturados dentro de sus imágenes. Para ello es requerido 
diseñar un software que permita el reconocimiento de dichos cuerpos celestes. 

Este repositorio contiene el código desarrollado para el TFG "Diseño y construcción
de una cámara all-sky para la detección de meteoros". El código está escrito en 
Python, haciendo uso de la librería OpenCV. El objetivo del programa es indicar la
presencia de meteoros en imágenes o vídeos.


## Requisitos
El programa hace uso de la librería OpenCV, que a su vez utiliza NumPy.
Los paquetes se pueden instalar con pip:
```
pip install numpy
pip install opencv-python
```
## Funcionamiento
### Programa principal
Para iniciar la ejecución del software, se ejecuta el script main.py. Al
pasarle la opción -h muestra una ayuda para su utilización. Como
resultado de su ejecución, se genera un fichero con los resultados obtenidos 
denominado results.txt. Su contenido consiste en dos columnas, una con la ruta del 
fichero analizado y otra con las palabras True o False, dependiendo de si se ha detectado 
o no un meteoro.
A este script se le debe pasar un argumento obligatorio: la ruta de la imagen, 
vídeo o directorio que se va a analizar. Además, se le pueden pasar 5 argumentos 
opcionales para:
- utilizar una máscara durante el procesamiento (por defecto no se usa ninguna 
máscara);
- mover los ficheros analizados a dos directorios diferentes, uno conteniendo los 
ficheros con detecciones y otro donde se almacenarán los demás;
- volcar los resultados en un fichero elegido por el usuario (por defecto el fichero 
results.txt se genera en el directorio desde donde se ejecute el script);
- generar un fichero .csv en una ruta especificada por el usuario con los datos de 
los meteoros detectados;
- enviar los ficheros con detecciones a un canal de trabajo en Slack, y
- si la ruta que se le pasa al script es un directorio, se puede elegir entre analizar 
solo el contenido de este o, si el directorio contiene a su vez más directorios;
recorrerlos recursivamente y analizar todos los ficheros.

Al pasar la opción -h, se muestra la siguiente ayuda:
![help](./imgs/help.png?raw=true "help")

### Procesamiento
El procesamiento consta de las siguientes etapas:
- Difuminado (blur): se utiliza la técnica de desenfoque gaussiano.
- Detección de bordes: se utiliza el algoritmo de Canny para detección de bordes. 
- Enmascarado: tras detectar los bordes de la imagen, se le aplica una máscara 
para ignorar los bordes de cuerpos cercanos en el entorno de la cámara.
- Cerrado morfológico: su objetivo es unir discontinuidades que puedan tener los bordes.
- Identificación de líneas: se utiliza la transformada de Hough para encontrar 
líneas rectas en los bordes detectados.

### Postprocesado
En primer lugar, se genera el fichero de resultados, bien sea en la ruta por defecto 
o en una ruta especificada por el usuario.
Opcionalmente, se pueden enviar los ficheros con detecciones a un equipo de 
trabajo de Slack, y también se pueden mover los ficheros a directorios separados 
dependiendo de si contienen posibles meteoros o no.
