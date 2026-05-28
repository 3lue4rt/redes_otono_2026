# Actividad: Sockets orientados a conexión con Stop & Wait

## Archivos:

Todos los archivos de testing tienen el parametro `-h` o `--help` para ver los parametros disponibles.

### SocketTCP.py

Contiene las clases `SocketTCP` y `Segment` junto a varias constantes como `TIMEOUT_TIME` y `PACKET_SIZE_MAX`, etc. Está todo documentado en código.

### servidor.py

Contiene testing para SocketTCP del lado del servidor, se conecta siempre a `(localhost, 8000)`, el funcionamiento de este es:

```bash
python servidor.py [*FLAGS ...]
```

Donde se conecta con un cliente, recibe un mensaje y se cierra.

Contiene 3 flags opcionales:

+ `-d` o `--debug`: activa el modo debug, muestra a más detalle el comportamiento interno de los SocketTCP funcionando.

+ `-t` o `--test`: activa el modo debug, desactiva el funcionamiento normal y ejecuta los tests del enunciado.

+ `-s` o `--stress`: activa el modo debug, desactiva el funcionamiento normal y ejecuta un stress tests de 10 sockets que:
  + Acepta un cliente
  + Recibe un mensaje
  + Manda un mensaje a su cliente
  + Cierra la conección

  Es recomendable bajar la constante `TIMEOUT_TIME` en `SocketTCP` a 0.01s y no ocupar delay en `netem`.

### cliente.py

Contiene testing para SocketTCP del lado del cliente, el funcionamiento de este es:

```bash
python cliente.py [IP] [PUERTO] [*FLAGS ...]
```

Donde toma por stdin texto plano para enviar al servidor ubicado en `(IP, PUERTO)`.

Contiene 3 flags opcionales:

+ `-d` o `--debug`: activa el modo debug, muestra a más detalle el comportamiento interno de los SocketTCP funcionando.

+ `-t` o `--test`: activa el modo debug, desactiva el stdin y ejecuta los tests del enunciado.

+ `-s` o `--stress`: activa el modo debug, desactiva el fstdin y ejecuta un stress tests de 10 sockets que:
  + Acepta un cliente
  + Recibe un mensaje
  + Manda un mensaje a su cliente
  + Cierra la conección

  Es recomendable bajar la constante `TIMEOUT_TIME` en `SocketTCP` a 0.01s y no ocupar delay en `netem`.

## Modo de uso para testing:

Abra dos terminales, ejecute primero `servidor.py` en una y luego `cliente.py` en la otra.

Es __MUY IMPORTANTE__ que ocupe las mismas flags en `servidor.py` como en `cliente.py`.