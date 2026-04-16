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

---

## Parte 2

El proxy tiene 2 funcionalidades principales:

+ Bloquear tráfico hacia páginas no permitidas
+ Reemplazar contenido inapropiado (reemplazar strings)

### Antes de comenzar

Dibujar un diagrama de flujo de funcionamiento para el proxy, identificar cuales y cuantos sockets ocupar. __ADJUNTAR DIAGRAMA EN EL INFORME__.

### Pasos a seguir:

#### De servidor a proxy

Transforme el servidor de la parte 1, a un proxy, que no modifica nada, solo recibe un requerimiento del cliente, se lo envía al servidor, toma la respuesta del servidor y se la envía al cliente. (Seguir diagrama de flujo)

---

#### Test (curl sin/con proxy)

Use `curl` para ver que su proxy logra transferir mensajes de forma exitosa. Para ello verifique que pedir la página `example.com` con `curl` sin usar proxy, entrega lo mismo que al usar curl con su código como proxy. Para probar esto ejecute los siguientes comandos:

```bash
 %%%%% petición SIN proxy:
curl example.com
 %%%%% petición CON proxy:
curl example.com -x IP_VM:8000
```

---

#### Revisar sitios bloqueados

Al recibir la URI del servidor, si esta blacklisted debe devolver un `error 403` junto a un html con una imagen. Para ver el blacklist ocupe el archivo JSON.

---

#### Test (Probando el Blacklist)

Utilizando su proxy con curl intente acceder a una página prohibida y verifique que este retorna error 403 junto al código HTML que usted implementó. Verifique que al ingresar a páginas que no están prohibidas, como cc4303.bachmann.cl, su código sigue funcionando como antes.

---

#### Request válida

En caso de que la dirección del servidor final no sea una dirección prohibida, agregue a la request que va desde el proxy al servidor el header X-ElQuePregunta con su nombre.

---

#### Test (curl a través del proxy)

Utilizando curl, pruebe acceder al dominio cc4303.bachmann.cl a través de su proxy y verifique que el mensaje de bienvenida mostrado por la página cambia al pasar por su proxy, versus el mensaje mostrado al usar curl sin pasar por su proxy.

---

#### Reemplazar palabras prohibídas

Configure su proxy para que reemplace contenido inadecuado. Para esto busque las palabras prohibidas y reemplace dichas palabras.

---

#### Test (reemplazo correcto)

Utilizando curl pruebe acceder a cc4303.bachmann.cl/replace a través de su proxy y verifique que las palabras son reemplazadas y que no hay errores en el contenido.

---

#### Mensajes mayores que el buffer

Como en la actividad de ejemplo, reponder las siguientes preguntas __EN EL INFORME__.

+ ¿Cómo sé si llegó el mensaje completo?
+ ¿Qué pasa si los headers no caben en mi buffer?
+ ¿Cómo sé que el HEAD llegó completo?
+ ¿Y el BODY?

---

#### Test (buffer_size)

Pruebe que su proxy sigue funcionando cuando el tamaño del buffer de recepción es pequeño (ejemplo: recv_buffer = 50).

---
