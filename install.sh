#!/bin/bash
# Instalador COMPLETO del Sistema de Timbres Escolar
# Descarga el código, prepara permisos e instala todo
# Ejecutar: curl -sSL https://raw.githubusercontent.com/blak0p/Musica_Pureza_grao/main/install.sh | bash

set -e

echo "🎵 Sistema de Timbres Escolar - Instalador Completo"
echo "===================================================="
echo ""

# ─── Crear directorio de trabajo ───
INSTALL_DIR="${INSTALL_DIR:-/opt/musica-pureza-grao}"
TEMP_DIR=$(mktemp -d)

echo "[1/7] Descargando código..."
cd "$TEMP_DIR"

# Descargar archivos individuales del repositorio
echo "      Descargando archivos del repositorio..."

# Crear estructura de directorios
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/src"
mkdir -p "$INSTALL_DIR/tests"
mkdir -p "$INSTALL_DIR/templates"

# Archivos raíz
curl -sSL "https://raw.githubusercontent.com/blak0p/Musica_Pureza_grao/main/bell.py" -o "$INSTALL_DIR/bell.py"
curl -sSL "https://raw.githubusercontent.com/blak0p/Musica_Pureza_grao/main/app.py" -o "$INSTALL_DIR/app.py" 2>/dev/null || true
curl -sSL "https://raw.githubusercontent.com/blak0p/Musica_Pureza_grao/main/setup_service.py" -o "$INSTALL_DIR/setup_service.py" 2>/dev/null || true
curl -sSL "https://raw.githubusercontent.com/blak0p/Musica_Pureza_grao/main/requirements.txt" -o "$INSTALL_DIR/requirements.txt" 2>/dev/null || true
curl -sSL "https://raw.githubusercontent.com/blak0p/Musica_Pureza_grao/main/README.md" -o "$INSTALL_DIR/README.md"

# Archivos src/
for file in library.py state.py carousel.py player.py cron_helper.py; do
    curl -sSL "https://raw.githubusercontent.com/blak0p/Musica_Pureza_grao/main/src/$file" -o "$INSTALL_DIR/src/$file" 2>/dev/null || true
done

# Archivos templates/
curl -sSL "https://raw.githubusercontent.com/blak0p/Musica_Pureza_grao/main/templates/index.html" -o "$INSTALL_DIR/templates/index.html" 2>/dev/null || true

echo "      Código descargado ✅"

# ─── Detector de gestor de paquetes ───
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
# 2. Reproducto de audio (mpv)
# ─────────────────────────────────────────────
echo "[2/7] Reproductor de audio..."
if command -v mpv &> /dev/null; then
    echo "      mpv ya instalado ✅"
else
    echo "      Instalando mpv..."
    if [ "$PKG" = "apt" ]; then sudo apt-get update -qq; fi
    instalar "mpv" "mpv" "mpv" "mpv" || echo "      ⚠️  Instalá mpv manualmente según tu distro"
    command -v mpv &> /dev/null && echo "      mpv instalado ✅"
fi

# ─────────────────────────────────────────────
# 3. Dependencias Python
# ─────────────────────────────────────────────
echo "[3/7] Dependencias Python..."
cd "$INSTALL_DIR"

YA_INSTALADO=false
if python3 -c "import flask; import flask_cors; import flask_socketio" 2>/dev/null; then
    echo "      Flask y dependencias ya instalados ✅"
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
        fi
    fi
fi

# ─────────────────────────────────────────────
# 4. Preparar archivos necesarios
# ─────────────────────────────────────────────
echo "[4/7] Preparando archivos..."
mkdir -p static
if [ -f templates/index.html ] && [ ! -f static/index.html ]; then
    cp templates/index.html static/index.html
    echo "      index.html copiado a static/ ✅"
fi
if [ ! -f static/socket.io.min.js ]; then
    echo "      Descargando socket.io..."
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
# 5. Crear script uninstall.sh
# ─────────────────────────────────────────────
echo "[5/7] Creando desinstalador..."
cat > "$INSTALL_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
# Desinstalador del Sistema de Timbres Escolar

echo "⚠️  Desinstalando Sistema de Timbres..."

# Remover cron entries si existen
python3 bell.py --remove-cron 2>/dev/null || true

# Remover directorio
INSTALL_DIR="${INSTALL_DIR:-/opt/musica-pureza-grao}"
sudo rm -rf "$INSTALL_DIR"

echo "✅ Desinstalado"
EOF

chmod +x "$INSTALL_DIR/uninstall.sh"
echo "      uninstall.sh creado ✅"

# ─────────────────────────────────────────────
# 6. Configuración interactiva
# ─────────────────────────────────────────────
echo "[6/7] Configuración del sistema..."
echo ""
echo "  Se te va a preguntar:"
echo "  • Ruta de las carpetas de música"
echo "  • Usuario y contraseña para la web"
echo "  • Si querés que arranque solo"
echo ""

if [ -f "$INSTALL_DIR/setup_service.py" ]; then
    cd "$INSTALL_DIR"
    python3 setup_service.py 2>/dev/null || true
fi

# ─────────────────────────────────────────────
# 7. Verificación final
# ─────────────────────────────────────────────
echo "[7/7] Verificando instalación..."
cd "$INSTALL_DIR"

if [ -f bell.py ]; then
    echo "      bell.py ✅"
fi

if command -v mpv &> /dev/null; then
    echo "      mpv ✅"
fi

if python3 -c "import flask" 2>/dev/null; then
    echo "      Flask ✅"
fi

# Limpiar temporal
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "  📁 Ubicación: $INSTALL_DIR"
echo ""
echo "  Para probar un timbre:"
echo "    cd $INSTALL_DIR"
echo "    python3 bell.py cambio"
echo ""
echo "  Para la web:"
echo "    cd $INSTALL_DIR"
echo "    python3 app.py     → http://localhost:5000"
echo ""
echo "  Para desinstalar:"
echo "    $INSTALL_DIR/uninstall.sh"
echo ""
