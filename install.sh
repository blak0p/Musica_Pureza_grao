#!/bin/bash
# Instalador LOCAL del Sistema de Timbres Escolar
# Funciona en Debian, Ubuntu, Mint, Fedora, Arch, openSUSE...
# Ejecutar: bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🎵 Sistema de Timbres Escolar - Instalador Local"
echo "================================================"
echo ""
echo "  Proyecto en: $SCRIPT_DIR"
echo ""

# ─── Detectar gestor de paquetes ───
detectar_pkg() {
    if command -v apt &> /dev/null; then
        echo "apt"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v yum &> /dev/null; then
        echo "yum"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    elif command -v zypper &> /dev/null; then
        echo "zypper"
    else
        echo "unknown"
    fi
}

PKG=$(detectar_pkg)

# ─── Instalar paquete según distro ───
instalar() {
    local pkg_apt="$1"
    local pkg_dnf="$2"
    local pkg_pacman="$3"
    local pkg_zypper="$4"

    case "$PKG" in
        apt)   sudo apt-get install -y $pkg_apt ;;
        dnf|yum) sudo dnf install -y ${pkg_dnf:-$pkg_apt} 2>/dev/null || sudo yum install -y ${pkg_dnf:-$pkg_apt} ;;
        pacman) sudo pacman -S --noconfirm ${pkg_pacman:-$pkg_apt} ;;
        zypper) sudo zypper install -y ${pkg_zypper:-$pkg_apt} ;;
        *)     return 1 ;;
    esac 2>/dev/null
}

# ─────────────────────────────────────────────
# 1. Reproductor de audio (mpv)
# ─────────────────────────────────────────────
echo "[1/5] Reproductor de audio..."
if command -v mpv &> /dev/null; then
    echo "      mpv ya instalado ✅"
else
    echo "      Instalando mpv..."
    if [ "$PKG" = "apt" ]; then sudo apt-get update -qq; fi
    instalar "mpv" "mpv" "mpv" "mpv" || echo "      ⚠️  Instalá mpv manualmente según tu distro"
    command -v mpv &> /dev/null && echo "      mpv instalado ✅"
fi

# ─────────────────────────────────────────────
# 2. Dependencias Python
# ─────────────────────────────────────────────
echo "[2/5] Dependencias Python..."
cd "$SCRIPT_DIR"

YA_INSTALADO=false
if python3 -c "import flask; import flask_cors; import flask_socketio" 2>/dev/null; then
    echo "      Flask, flask-cors, flask-socketio ya instalados ✅"
    YA_INSTALADO=true
fi

if [ "$YA_INSTALADO" = false ]; then
    # Asegurar pip3
    if ! command -v pip3 &> /dev/null; then
        echo "      Instalando pip3..."
        if [ "$PKG" = "apt" ]; then sudo apt-get update -qq; fi
        instalar "python3-pip" "python3-pip" "python-pip" "python3-pip" \
          || echo "      ⚠️  Instalá python3-pip manualmente"
    fi

    # Instalar dependencias Python
    echo "      Instalando Flask y dependencias..."
    if command -v pip3 &> /dev/null; then
        pip3 install --break-system-packages -r requirements.txt -q 2>/dev/null \
          || pip3 install --user -r requirements.txt -q 2>/dev/null \
          || pip3 install -r requirements.txt -q 2>/dev/null \
          || echo "      ⚠️  pip no funcionó, probando paquetes del sistema..."

        if python3 -c "import flask; import flask_cors; import flask_socketio" 2>/dev/null; then
            echo "      Dependencias instaladas ✅"
            YA_INSTALADO=true
        fi
    fi

    if [ "$YA_INSTALADO" = false ]; then
        echo "      Probando con paquetes del sistema..."
        if [ "$PKG" = "apt" ]; then
            sudo apt-get install -y python3-flask python3-flask-cors python3-flask-socketio -qq 2>/dev/null
        elif [ "$PKG" = "pacman" ]; then
            sudo pacman -S --noconfirm python-flask python-flask-cors python-flask-socketio 2>/dev/null
        elif [ "$PKG" = "dnf" ] || [ "$PKG" = "yum" ]; then
            sudo dnf install -y python3-flask python3-flask-cors python3-flask-socketio 2>/dev/null
        elif [ "$PKG" = "zypper" ]; then
            sudo zypper install -y python3-Flask python3-Flask-cors python3-Flask-SocketIO 2>/dev/null
        fi

        if python3 -c "import flask; import flask_cors; import flask_socketio" 2>/dev/null; then
            echo "      Dependencias instaladas ✅"
        else
            echo "      ⚠️  No se pudieron instalar automáticamente."
            echo "      En PC con Internet ejecutá:"
            echo "        pip3 install --break-system-packages -r requirements.txt"
        fi
    fi
fi

# ─────────────────────────────────────────────
# 3. Preparar archivos necesarios (static, socket.io)
# ─────────────────────────────────────────────
echo "[3/5] Preparando archivos..."
mkdir -p static
if [ -f templates/index.html ] && [ ! -f static/index.html ]; then
    cp templates/index.html static/index.html
    echo "      index.html copiado a static/ ✅"
fi
if [ ! -f static/socket.io.min.js ]; then
    echo "      Descargando socket.io local..."
    if command -v wget &> /dev/null; then
        wget -q "https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.min.js" -O static/socket.io.min.js \
          && echo "      socket.io descargado ✅" \
          || echo "      (opcional) No se pudo descargar socket.io"
    elif command -v curl &> /dev/null; then
        curl -sL "https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.min.js" -o static/socket.io.min.js \
          && echo "      socket.io descargado ✅" \
          || echo "      (opcional) No se pudo descargar socket.io"
    fi
fi
echo "      Archivos listos ✅"

# ─────────────────────────────────────────────
# 4. Configuración interactiva
# ─────────────────────────────────────────────
echo "[4/5] Configuración del sistema..."
echo ""
echo "  Se te va a preguntar:"
echo "  • Ruta de las carpetas de música"
echo "  • Usuario y contraseña para la web"
echo "  • Si querés que arranque solo"
echo ""
python3 setup_service.py

# ─────────────────────────────────────────────
# 5. Tests
# ─────────────────────────────────────────────
echo "[5/5] Verificando..."
cd "$SCRIPT_DIR"
python3 -m unittest discover -s tests > /dev/null 2>&1 && echo "      Tests: ✅" || echo "      Tests: ⚠️  Algunos fallaron, revisá manualmente"

echo ""
echo "🎉 Listo!"
echo ""
echo "  Para probar un timbre:"
echo "    python3 bell.py cambio"
echo ""
echo "  Para la web:"
echo "    python3 app.py     → http://localhost:5000"
echo ""
