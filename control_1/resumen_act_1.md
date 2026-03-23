# Actividad 1: Proxy

IMPORTANTE ENTREGAR INFORME COMO PDF NO COMO MARKDOWN PORFAVORRRRRRRRRR gracias

## Recordatorio

+ Ocupar maquina virtual
+ HTTP es orientado a connección
+ Comando `curl` util para cliente HTTP
+ Puerto 80, a menos que se indique lo contrario

## Parte 1

### Pasos a seguir:

#### 1. IP de la VM
Revisar IP de la VM, se referira como `IP_VM`.

---

#### 2. Interpretar HTTP

El servidor tiene que leer, interpretar y crear mensajes HTTP, crear las funciones:
```python
# parsea un mensaje http y lo transforma a un objeto http
def parse_HTTP_message(http_message: str)-> HTTP_Obj:
  ...

# crea un mensaje http a partir de un objeto http
def create_HTTP_message(http_obj: HTTP_Obj)-> str:
  ...
```
---
#### Test (probar funcionalidades)

Utilice su navegador para obtener un 'request' y use dicho request para probar que las funciones que acaba de programar funcionen como corresponde.

Para obtener la request cree un socket servidor que escuche en `(IP_VM, 8000)` en su __máquina virtual__, e intente acceder a `http://IP_VM:8000` desde un navegador en su __máquina local__.

Al hacer esto su socket recibirá la 'request' HTTP que está haciendo el navegador a su socket servidor. Para ver la request imprima lo que recibió su socket en pantalla usando `print` __antes__ de invocar a `decode`. 

---

#### 3. curl y GET
Utilizar `curl` para obtener un response __GET__, ocupar:

```bash
curl -i cc4303.bachmann.cl
```

__IMPORTANTE__ : cada salto de línea tiene la forma `"\r\n"`

___Utilice esta response o respuesta HTTP como guía para crear su propia response a la petición que estaba recibiendo en el paso (1).___

---

#### Test (probando la respuesta)

Haga que su código *(corriendo en su máquina virtual)* le responda al navegador con la respuesta que acaba de crear y verifique que el navegador logra mostrarla. Luego utilice `curl` desde su máquina local como se muestra a continuación y verifique que `curl` también recibe una respuesta satisfactoria.

```bash
curl -i IP_VM:8000
```

---

#### 4. Modificar header
Modifique su servidor para que al momento de responder le agregue el header `X-ElQuePregunta` con su nombre como valor. __(Esto nos va a servir en la parte 2, no cambie el nombre del header)__.

---

#### Test (probar header)

Pruebe que se agrega de forma correcta el header utilizando `curl` como se muestra a continuación.

```bash
curl IP_VM:[puerto_server_http] -i
```

---

#### 5. Lectura JSON
Modifique su servidor para que pueda leer archivos JSON o archivos de configuración. 
 
Haga que el nombre y ubicación del archivo JSON pueda ser recibido como argumento al ejecutar su código.

___Estos archivos serán necesarios más adelante en la parte 2.___

Por mientras úselo para dejar en una variable su nombre, así el servidor quedará con un usuario parametrizable.

---

#### Test (probar JSON)

Pruebe que su servidor puede tomar su nombre desde su archivo JSON y lo puede utilizar para añadir el header `X-ElQuePregunta`.