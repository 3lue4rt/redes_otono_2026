# Proxy

## Pasos para utilizar
Primero cambiar la variable `IP_VM` en el archivo `proxy.py` a la ip de su máquina virtual.

Correr el servidor con `python proxy.py`

## Proxy en el navegador web
En nuestro caso usamos Firefox, en settings, proxy settings, configure proxy, manual proxy configuration y rellenar __HTTP Proxy__ con el ip (`IP_VM`) y el puerto (variable `port` en `proxy.py`)

## Problemas

No puede recibir ni mandar imagenes, por lo que solo puede procesar páginas de solo texto (las imágenes por url las procesa bien, el problema es con imagenes dentro del proxy).

