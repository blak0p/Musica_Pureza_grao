# 🏫 Guía de instalación — Sistema de Timbres Escolar

> **¿Para quién es esta guía?**
> Para cualquier persona que quiera instalar este sistema en una computadora
> con Linux, aunque no sepa nada de Linux. Cada paso está explicado con
> QUÉ va a pasar, CÓMO se hace (comando exacto para copiar y pegar),
> POR QUÉ se hace, y qué hacer si algo sale mal.

---

## 📋 Índice

1. [Antes de empezar](#1-antes-de-empezar)
2. [Instalar el programa](#2-instalar-el-programa)
3. [Configurar el sistema (fácil)](#3-configurar-el-sistema-fácil)
4. [Configurar el sistema (manual)](#4-configurar-el-sistema-manual)
5. [Poner la música](#5-poner-la-música)
6. [Programar los horarios](#6-programar-los-horarios)
7. [La interfaz web](#7-la-interfaz-web)
8. [Hacer que arranque solo](#8-hacer-que-arranque-solo)
9. [Probar que funciona](#9-probar-que-funciona)
10. [Problemas comunes](#10-problemas-comunes)
11. [Referencia técnica](#11-referencia-técnica)

---

## 1. Antes de empezar

### ¿Qué necesitás?

| Qué | Para qué |
|-----|----------|
| Una computadora con Linux | El sistema funciona en cualquier Linux (Ubuntu, Mint, Debian...) |
| Conexión a Internet | Solo para la instalación inicial |
| Parlantes | Para que se escuchen los timbres |
| Archivos de música | MP3, WAV, OGG — los que quieras para cada timbre |

### ¿Qué se va a instalar?

| Programa | Para qué sirve |
|----------|---------------|
| **mpv** | Reproduce los archivos de música |
| **Python 3** | El lenguaje en el que está hecho el sistema |
| **Flask** | Programa que hace funcionar la interfaz web |
| **Servicio web** | Hace que la interfaz web arranque sola al prender la PC |

---

## 2. Instalar el programa

> ⏱ Tiempo estimado: 5 minutos

### Opción 1: Instalación automática (recomendada)

Abrí una terminal (ventana negra con letras blancas). Copiá y pegá esto:

```bash
curl -sSL https://raw.githubusercontent.com/Alejandro-M-P/Music_Carousel_Hours/main/install.sh | bash
```

**Qué hace**: descarga todo, instala las dependencias, y te guía paso a paso.

**Posibles errores**:

| Error | Causa | Solución |
|-------|-------|----------|
| `curl: command not found` | No tenés curl instalado | Escribí `sudo apt-get install curl` y volvé a intentar |
| `bash: línea X: sudo: comando no encontrado` | No tenés sudo | Tenés que estar logueado como usuario normal con sudo |
| Te pide contraseña | Es normal | Es la contraseña de tu usuario de Linux |

### Opción 2: Instalación manual

Si la automática no funciona, seguí estos pasos:

```bash
# 1. Instalar el reproductor de música
sudo apt-get update
sudo apt-get install -y mpv

# 2. Descargar el programa
git clone https://github.com/Alejandro-M-P/Music_Carousel_Hours.git
cd Music_Carousel_Hours

# 3. Instalar las dependencias de Python
pip3 install -r requirements.txt

# 4. Ejecutar el instalador interactivo
python3 setup_service.py
```

---

## 3. Configurar el sistema (fácil)

> ⏱ Tiempo estimado: 2 minutos

El instalador incluye un programa de configuración que te va preguntando.
Ejecutalo así:

```bash
python3 setup_service.py
```

Te va a preguntar:

### 📌 Paso 1: Ruta de la música

```
💬 Ruta de la música [/home/tu-usuario/musica]:
```

**¿Qué significa?**: Es la carpeta donde vas a poner los archivos de audio
de los timbres (entrada, salida, cambio, recreo).

**¿Qué poner?**: Apretá **Enter** para dejar la que viene por defecto.
Si querés otra carpeta, escribí la ruta completa, por ejemplo:
`/home/tu-usuario/Música` o `/media/disco/timbres`.

**⚠️ IMPORTANTE**: Después tenés que copiar tus canciones a las subcarpetas
que se crean automáticamente (explicado en el [Paso 5](#5-poner-la-música)).

### 📌 Paso 2: Archivos estáticos

```
💬 Ruta de archivos estáticos [/home/tu-usuario/colegio/static]:
```

**¿Qué significa?**: Carpeta para imágenes, logos, etc. de la página web.

**¿Qué poner?**: Apretá **Enter** (dejá el valor por defecto). Solo
cambiala si sabés lo que estás haciendo.

### 📌 Paso 3: Usuario y contraseña de la web

```
💬 Usuario [admin]:
💬 Contraseña [eit2021]:
```

**¿Qué significa?**: Con estos datos vas a iniciar sesión en la interfaz web
del sistema (para ver horarios, canciones, etc.).

**¿Qué poner?**: Cambialos si querés. Escribí el usuario que quieras,
después la contraseña que quieras. **Acordátelos**.

### 📌 Paso 4: Servicio de inicio automático

```
💬 ¿Instalar el servicio web ahora? (S/n):
```

**¿Qué significa?**: Hace que la página web del sistema arranque sola
cuando encendés la computadora. Si no lo hacés ahora, lo podés hacer
después (está explicado en el [Paso 8](#8-hacer-que-arranque-solo)).

**¿Qué poner?**: Escribí **S** (de Sí) y apretá Enter.

> ⚠️ Te va a pedir la contraseña de sudo (tu contraseña de Linux) porque
> necesita permisos para instalar el servicio.

### ✅ Después del instalador

El instalador crea automáticamente TODAS las carpetas necesarias:

| Carpeta | Para qué |
|---------|----------|
| `~/musica/entrada/` | Música para la entrada de los alumnos |
| `~/musica/salida/` | Música para la salida |
| `~/musica/cambio/` | Música para los cambios de hora |
| `~/musica/recreo/` | Música para el recreo |
| `colegio/state/` | Guarda el estado del sistema (no tocar) |
| `colegio/static/` | Archivos de la web (no tocar) |
| `.env` | Archivo con la configuración (usuario, contraseña, rutas) |

---

## 4. Configurar el sistema (manual)

Si preferís configurar todo a mano en vez de usar el instalador,
editá el archivo `.env`:

```bash
nano .env
```

Adentro tiene que verse así:

```
USER=admin                 # Usuario para la web
PASSWORD=eit2021           # Contraseña para la web
MUSIC_DIR=/home/tu-usuario/musica   # Carpeta de música
STATIC_DIR=/home/tu-usuario/colegio/static   # Archivos de la web
```

Cambiá lo que necesites. Después guardá con `Ctrl+O`, Enter, y salí con `Ctrl+X`.

---

## 5. Poner la música

> ⏱ Tiempo estimado: depende de cuánta música tengas

El sistema necesita carpetas con archivos de audio. Las carpetas ya fueron
creadas en el paso anterior. Ahora tenés que copiar tus canciones.

### Estructura de carpetas

```
~/musica/              ← (o la ruta que hayas puesto)
├── entrada/           ← Música para la ENTRADA de los alumnos
│   ├── cancion1.mp3
│   └── cancion2.mp3
├── salida/            ← Música para la SALIDA
│   └── cancion1.mp3
├── cambio/            ← Música para CAMBIO DE HORA
│   ├── tema1.mp3
│   ├── tema2.mp3
│   └── tema3.mp3
└── recreo/            ← Música para el RECREO
    └── musica.mp3
```

**Formatos soportados**: MP3, WAV, OGG, FLAC, M4A, y casi cualquier
formato de audio.

> **💡 Tip**: No necesita tener muchas canciones. Con 1 o 2 por tipo alcanza.
> Si tiene varias, las va mezclando sin repetir hasta que las escucha todas.

### Cómo copiar la música

Si tenés la música en un pendrive:

```bash
# Primero conectá el pendrive
# Después averiguá dónde se montó:
lsblk

# Te va a mostrar algo como /media/tu-usuario/NOMBRE_DEL_PENDRIVE
# Copiá las canciones:
cp /media/tu-usuario/NOMBRE_DEL_PENDRIVE/*.mp3 ~/musica/entrada/
cp /media/tu-usuario/NOMBRE_DEL_PENDRIVE/*.mp3 ~/musica/salida/
# ... y así para cada tipo
```

Si las canciones están en otra carpeta:

```bash
cp /ruta/de/tus/canciones/*.mp3 ~/musica/entrada/
```

**Posibles errores**:

| Error | Causa | Solución |
|-------|-------|----------|
| `No such file or directory` | La carpeta no existe | Corré `python3 setup_service.py` para crearlas |
| No se escucha nada después | Los archivos están dañados | Probá con otro archivo |

---

## 6. Programar los horarios

> ⏱ Tiempo estimado: 1 minuto

### Configuración rápida (con valores ya definidos)

```bash
python3 bell.py --setup-cron
```

Esto programa los timbres con los horarios típicos de un colegio:

| Horario | Tipo de timbre |
|---------|---------------|
| 08:05 | Entrada |
| 09:00 | Cambio de hora |
| 09:55 | Cambio de hora |
| 12:00 | Cambio de hora |
| 12:55 | Cambio de hora |
| 13:30 | Salida (mediodía) |
| 15:15 | Entrada (tarde) |
| 16:10 | Cambio de hora |
| 17:00 | Cambio de hora |
| 17:55 | Cambio de hora |
| 18:30 | Salida |

Los timbres suenan de lunes a viernes. Los fines de semana no suenan.

### ⚠️ ADVERTENCIA IMPORTANTE

El comando `--setup-cron` **BORRA todas las tareas programadas** que tengas
en el crontab (incluyendo las que no sean de los timbres) y las reemplaza
por las del sistema. Si tenés otras tareas programadas en la computadora,
guardalas antes.

### Ver los horarios actuales

```bash
python3 bell.py --status
```

### Sacar los timbres

```bash
python3 bell.py --remove-cron
```

### Cambiar los horarios (para avanzados)

Los horarios se definen en el archivo `src/cron_helper.py`, en la parte
que dice `BELL_TIMES`. Tenés que editar ese archivo y después volver a
ejecutar `python3 bell.py --setup-cron`.

---

## 7. La interfaz web

> ⏱ Tiempo estimado: 5 minutos

La interfaz web te permite ver los horarios, controlar la música,
y silenciar el sistema desde el navegador (Chrome, Firefox, Edge).

### 7.1 Iniciar la web (manual, para probar)

```bash
python3 app.py
```

**Qué tiene que pasar**: Aparece un mensaje que dice algo como:

```
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

Después abrí el navegador y escribí en la barra de direcciones:

```
http://localhost:5000
```

Te va a aparecer una pantalla de **inicio de sesión**. Poné el usuario
y la contraseña que configuraste en el [Paso 3 de configuración](#-paso-3-usuario-y-contraseña-de-la-web).

> 💡 **Importante**: Mientras la terminal esté abierta, la web funciona.
> Si cerrás la terminal, la web se apaga. Para que quede siempre prendida,
> seguí el [Paso 8](#8-hacer-que-arranque-solo).

### 7.2 ¿Qué se puede hacer en la web?

| Función | Descripción |
|---------|-------------|
| Ver horarios | Mostrá los horarios de entrada, salida, cambios, recreo |
| Ver cola de música | Sabé qué canción va a sonar después |
| Última canción | Mostrá cuál fue la última que sonó |
| Duración | Controlá cuánto dura cada tipo de música (en segundos) |
| Silenciar | Apagá todos los timbres temporalmente desde la web |

### 7.3 Cómo ver la IP de la computadora

Para acceder desde OTRA computadora o desde el celular, necesitás saber
la **dirección IP** de la PC donde corre el sistema.

**La IP es como la dirección de tu casa, pero de la computadora.**
Sirve para que otros dispositivos en la misma red la encuentren.

#### Método 1: Con un comando (recomendado)

Abrí una terminal y ejecutá:

```bash
ip addr show | grep "inet "
```

Te va a mostrar algo como esto:

```
    inet 127.0.0.1/8 scope host lo
    inet 192.168.1.100/24 brd 192.168.1.255 scope global wlp2s0
```

**La IP que te sirve** es la que **NO** empieza con `127.`. Buscá un número
como `192.168.x.x` o `10.x.x.x` o `172.x.x.x`. En este ejemplo es
`192.168.1.100`.

#### Método 2: Con un atajo

```bash
hostname -I
```

Te muestra solo las IPs, sin vueltas. La primera que aparece (si empieza
con 192, 10 o 172) es la que necesitás.

#### Método 3: Fijate en el ícono de red

En la mayoría de los Linux, haciendo click en el ícono de WiFi o red
(arriba a la derecha) podés ver la IP.

### 7.4 Acceder desde OTRA computadora o celular

Una vez que tenés la IP (por ejemplo `192.168.1.100`):

**Desde otra computadora en la MISMA red**: abrí el navegador y poné:

```
http://192.168.1.100:5000
```

(Reemplazá `192.168.1.100` por la IP que viste en tu PC)

**Desde un celular**: conectado al mismo WiFi, abrí el navegador y poné
la misma dirección.

> ✅ **Funciona en cualquier dispositivo**: Windows, Mac, celular, tablet.
> Mientras estén en la MISMA red (mismo WiFi), van a poder abrir la web.

### 7.5 Solucionar problemas de conexión

| Problema | Causa | Solución |
|----------|-------|----------|
| "No se puede conectar" | La web no está corriendo | Ejecutá `python3 app.py` |
| "Conexión rechazada" | El puerto no está abierto | Revisá el firewall (ver abajo) |
| "Tarda en cargar" | Red lenta | Esperá, o conectate por cable |
| No aparece en el celular | No está en el mismo WiFi | Conectate al mismo WiFi |

#### Firewall (si tenés uno activo)

Algunas computadoras tienen un **cortafuegos (firewall)** que bloquea
el puerto 5000. Si no podés acceder desde otra PC, abrí el puerto:

```bash
sudo ufw allow 5000
```

> Este comando usa `ufw` (Uncomplicated Firewall). Si no lo tenés,
> ignorá este paso — probablemente no tengas firewall activo.

#### IP dinámica (cambia cada vez que reiniciás)

Cada vez que reiniciás la computadora, puede cambiarte la IP. Si te pasa,
tomá nota de la nueva IP con `ip addr show` o `hostname -I`.

Para solucionarlo de raíz, poné una **IP fija** (ver [7.6](#76-poner-ip-fija-recomendado)).

### 7.6 Poner IP fija (recomendado)

Por defecto, la computadora obtiene una IP automática que **puede cambiar**
cada vez que reiniciás. Si querés que siempre tenga la misma IP (así no
tenés que estar averiguándola cada vez), configurale una IP fija.

> ⚠️ Esto es opcional pero muy recomendado para un sistema de timbres
> que tiene que estar siempre funcionando.

#### Opción A: IP fija desde el router (más fácil)

1. Abrí el navegador en cualquier computadora
2. En la barra de direcciones poné: `http://192.168.1.1` o `http://192.168.0.1`
   (Si no funciona, preguntá cuál es la IP del router)
3. Iniciá sesión con el usuario y contraseña del router
   (suele estar escrito en una etiqueta abajo del router)
4. Buscá una opción que diga "DHCP Reservation", "Static DHCP" o
   "Asignación de IP fija"
5. Agregá tu computadora por su dirección MAC (dirección física de la
   tarjeta de red — no cambia nunca)
6. Poné la IP que quieras (ej: `192.168.1.200`)
7. Guardá y reiniciá la computadora

Para saber la dirección MAC de tu computadora:

```bash
ip link show | grep "link/ether"
```

Te va a mostrar algo como: `link/ether aa:bb:cc:dd:ee:ff`. Eso es la MAC.

#### Opción B: IP fija desde la computadora (más técnica)

Si no podés entrar al router, configurás la IP fija en la computadora:

```bash
# Averiguá el nombre de tu conexión de red
nmcli connection show

# Te va a mostrar algo como "WiFi" o "Conexión cableada"
# Reemplazá "WiFi" por el nombre que aparezca:
sudo nmcli connection modify "WiFi" ipv4.method manual \
  ipv4.addresses 192.168.1.200/24 \
  ipv4.gateway 192.168.1.1 \
  ipv4.dns 8.8.8.8

# Reiniciá la conexión
sudo nmcli connection down "WiFi" && sudo nmcli connection up "WiFi"
```

> 💡 Cambiá `192.168.1.200` por la IP que quieras, y `192.168.1.1` por
> la IP de tu router (puede ser `192.168.0.1` u otra).

### 7.7 ¿Se puede acceder desde fuera de la escuela? (Internet)

> ⚠️ **Importante**: El sistema está diseñado para funcionar en la RED LOCAL
> (mismo WiFi). NO recomendamos abrirlo a Internet por seguridad.

Si igual necesitás acceder desde afuera, necesitás:

1. Una **IP fija pública** (contratada con el proveedor de Internet)
2. Configurar el router para que **redirija el puerto 5000** (Port Forwarding)
3. Configurar HTTPS con un certificado SSL

**No cubrimos esto en esta guía porque requiere conocimientos avanzados
de redes y compromete la seguridad del sistema.**

---

## 8. Hacer que arranque solo

> ⏱ Tiempo estimado: 1 minuto

Si **no** instalaste el servicio en el [Paso 4 de configuración](#-paso-4-servicio-de-inicio-automático),
o si querés hacerlo de nuevo:

```bash
sudo python3 setup_service.py --install
```

Después de instalarlo, lo activás:

```bash
sudo systemctl enable --now bell-server.service
```

### Para ver si está funcionando

```bash
sudo systemctl status bell-server.service
```

Deberías ver algo como `active (running)` en color verde.

También podés probar abriendo `http://localhost:5000` desde el navegador.

> 💡 **Con el servicio activo**, la web arranca automáticamente al prender
> la computadora. Ya no necesitás ejecutar `python3 app.py` manualmente.
> La IP para acceder desde otros dispositivos es la misma que la de la
> computadora (ver [7.3](#73-cómo-ver-la-ip-de-la-computadora)).

### Para apagarlo

```bash
sudo systemctl stop bell-server.service
```

### Para prenderlo de nuevo

```bash
sudo systemctl start bell-server.service
```

### Para sacarlo definitivamente

```bash
sudo systemctl disable --now bell-server.service
sudo rm /etc/systemd/system/bell-server.service
```

---

## 9. Probar que funciona

### Prueba 1: Reproducir un timbre

```bash
cd /home/tu-usuario/Music_Carousel_Hours
python3 bell.py cambio
```

**¿Qué tiene que pasar?**: Se tiene que escuchar música de la carpeta
`cambio/`. Si no se escucha nada, revisá el [Paso 5](#5-poner-la-música).

### Prueba 2: Ver el estado

```bash
python3 bell.py --status
```

**¿Qué tiene que pasar?**: Muestra qué canción se reprodujo última y
cuál sigue en la cola.

### Prueba 3: La página web

```bash
python3 app.py
```

Y abrí `http://localhost:5000` en el navegador.

**¿Qué tiene que pasar?**: Aparece la página de inicio de sesión.
Poné tu usuario y contraseña. Después ves el panel de control.

**Probá también desde el celular**: conectate al mismo WiFi y poné
`http://IP-DE-TU-PC:5000` (averiguá la IP con `hostname -I`).

### Prueba 4: Los tests

```bash
python3 -m unittest discover -s tests
```

**¿Qué tiene que pasar?**: Muestra que pasaron más de 140 tests.
Si algunos fallan, no es grave — puede ser por diferencias de horarios.
Lo importante es que la mayoría pasen.

---

## 10. Problemas comunes

### ❌ "No se escucha nada"

| Causa posible | Solución |
|--------------|----------|
| Los parlantes están apagados | Prendelos y subí el volumen |
| Las carpetas de música están vacías | Poné archivos en las carpetas (ver [Paso 5](#5-poner-la-música)) |
| mpv no está instalado | `sudo apt-get install mpv` |
| El sonido está silenciado en la web | Entrá a la web y desactivá el silencio |
| El sistema detectó que es fin de semana | Los timbres no suenan sábado ni domingo |

### ❌ "La página web no carga"

```
Error: conexión rechazada
```

| Causa posible | Solución |
|--------------|----------|
| La web no está corriendo | Ejecutá `python3 app.py` |
| El servicio no arrancó | `sudo systemctl start bell-server.service` |
| El puerto 5000 está ocupado | Cambiá el puerto o reiniciá la PC |

### ❌ "Error: No module named flask"

```
ModuleNotFoundError: No module named 'flask'
```

**Causa**: Faltan las dependencias de Python.
**Solución**:

```bash
pip3 install -r requirements.txt
```

Si no tenés pip:

```bash
sudo apt-get install python3-pip
pip3 install -r requirements.txt
```

### ❌ "Error de permisos en /var/log"

```
PermissionError: [Errno 13] Permission denied: '/var/log/colegio-bell.log'
```

**Causa**: El sistema intenta escribir en un archivo de sistema que
requiere permisos de administrador.

**Solución**: No es grave. El sistema ya usa automáticamente la carpeta
`state/` dentro del proyecto como alternativa.

### ❌ "No se encontraron canciones"

```
WARNING: Folder missing or empty: /.../recreo
```

**Causa**: La carpeta de música para ese tipo de timbre está vacía
o no existe.

**Solución**: Poné al menos un archivo de música en esa carpeta.

### ❌ "Ya hay un servicio corriendo"

```
Error: Could not start service: Unit bell-server.service already running
```

**Causa**: El servicio ya está activo.
**Solución**: No hagas nada, ya funciona. Si querés reiniciarlo:

```bash
sudo systemctl restart bell-server.service
```

---

## 11. Referencia técnica

### Estructura del proyecto

```
colegio/
├── app.py                    → Servidor web (Flask)
├── bell.py                   → Programa principal (timbres)
├── setup_service.py          → Instalador interactivo
├── install.sh                → Instalador automático
├── CONFIGURACION.md          → Esta guía
├── requirements.txt          → Dependencias de Python
├── .env                      → Configuración (usuario, rutas)
├── bell-server.service       → Servicio systemd (plantilla)
├── start_server.sh           → Inicio rápido del servidor
│
├── src/                      → Código del sistema
│   ├── config.py             → Configuración centralizada
│   ├── state.py              → Guarda el estado del sistema
│   ├── library.py            → Busca archivos de música
│   ├── carousel.py           → Mezcla canciones sin repetir
│   ├── player.py             → Reproduce la música
│   ├── cron_helper.py        → Programa los horarios
│   └── web_utils.py          → Utilidades para la web
│
├── static/                   → Archivos de la web (imágenes, etc.)
├── state/                    → Datos del sistema (no tocar)
│   ├── carousel.json         → Cola de canciones
│   ├── server.log            → Registro de la web
│   └── colegio-bell.log      → Registro de los timbres
│
├── templates/
│   └── index.html            → Página web
│
└── tests/                    → Tests del sistema
    ├── test_config.py        → Tests de configuración
    ├── test_state.py         → Tests de estado
    ├── test_library.py       → Tests de búsqueda
    ├── test_carousel.py      → Tests de mezcla
    ├── test_player.py        → Tests de reproducción
    ├── test_cron_helper.py   → Tests de horarios
    └── test_web_api.py       → Tests de la web
```

### Archivo `.env` (configuración)

Este archivo guarda tu configuración. Está en la raíz del proyecto
(`colegio/.env`). Se ve así:

```
USER=admin                    # Tu usuario para la web
PASSWORD=eit2021              # Tu contraseña para la web
MUSIC_DIR=/home/tu-usuario/musica   # Carpeta con la música
STATIC_DIR=/home/tu-usuario/colegio/static   # Archivos de la web
```

Las variables de entorno `MUSIC_DIR` y `STATIC_DIR` se pueden usar
para cambiar rutas sin editar archivos.

---

### 🎉 ¡Ya está todo listo!

Si llegaste hasta acá, el sistema de timbres debería estar funcionando.
Los timbres van a sonar automáticamente en los horarios programados,
y podés controlar todo desde la web.

**¿Algo no funciona?**: Revisá la sección de [Problemas comunes](#10-problemas-comunes).
Si el problema persiste, buscá en el archivo `state/server.log` o
`state/colegio-bell.log` que registran todo lo que hace el sistema.
