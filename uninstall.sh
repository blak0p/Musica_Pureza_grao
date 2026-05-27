#!/bin/bash
# Desinstalador del Sistema de Timbres Escolar
# Borra TODO: servicio, crontab, dependencias, carpeta de música, .env
# Ejecutar desde la carpeta del proyecto:
#   bash uninstall.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🗑️  Desinstalando Sistema de Timbres Escolar"
echo "============================================"
echo ""
echo "  Esto va a BORRAR:"
echo "  • Servicio web (systemd)"
echo "  • Tareas programadas (crontab)"
echo "  • Dependencias Python"
echo "  • Carpeta de música (~/musica)"
echo "  • Archivo .env (usuario y contraseña)"
echo "  • El proyecto completo"
echo ""
read -r -p "  ¿Estás seguro? (escribí 'BORRAR' para confirmar): " confirmacion

if [ "$confirmacion" != "BORRAR" ]; then
    echo "  Cancelado."
    exit 0
fi

echo ""

# 1. Detener y borrar servicio systemd
echo "[1/6] Deteniendo servicio web..."
if [ -f /etc/systemd/system/bell-server.service ]; then
    sudo systemctl stop bell-server.service 2>/dev/null || true
    sudo systemctl disable bell-server.service 2>/dev/null || true
    sudo rm /etc/systemd/system/bell-server.service
    sudo systemctl daemon-reload
    echo "      Servicio eliminado ✅"
else
    echo "      No había servicio ✅"
fi

# 2. Eliminar crontab de timbres
echo "[2/6] Eliminando tareas programadas..."
if [ -f "$SCRIPT_DIR/bell.py" ]; then
    python3 "$SCRIPT_DIR/bell.py" --remove-cron 2>/dev/null && echo "      Crontab eliminado ✅" || echo "      No había crontab ✅"
else
    echo "      (no se encontró bell.py, se omite)"
fi

# 3. Eliminar carpeta de música
echo "[3/6] Eliminando carpeta de música..."
MUSIC_DIR="${MUSIC_DIR:-$HOME/musica}"
if [ -f "$SCRIPT_DIR/.env" ]; then
    MUSIC_DIR=$(grep "^MUSIC_DIR=" "$SCRIPT_DIR/.env" 2>/dev/null | cut -d= -f2-)
    MUSIC_DIR="${MUSIC_DIR:-$HOME/musica}"
fi

if [ -d "$MUSIC_DIR" ]; then
    rm -rf "$MUSIC_DIR"
    echo "      Carpeta de música eliminada: $MUSIC_DIR ✅"
else
    echo "      No había carpeta de música ✅"
fi

# 4. Eliminar .env
echo "[4/6] Eliminando configuración (.env)..."
if [ -f "$SCRIPT_DIR/.env" ]; then
    rm -f "$SCRIPT_DIR/.env"
    echo "      .env eliminado ✅"
else
    echo "      No había .env ✅"
fi

# 5. Revertir dependencias Python (desinstalar Flask)
echo "[5/6] Desinstalando dependencias Python..."
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    DEPS=$(grep -v "^#" "$SCRIPT_DIR/requirements.txt" | grep -v "^\s*$" | cut -d'>' -f1 | cut -d'=' -f1 | tr '\n' ' ')
    for dep in $DEPS; do
        pip3 uninstall -y "$dep" 2>/dev/null || pip3 uninstall --break-system-packages -y "$dep" 2>/dev/null || true
    done
fi
echo "      Dependencias eliminadas ✅"

# 6. Borrar el proyecto
echo "[6/6] Eliminando el proyecto..."
cd "$HOME"
rm -rf "$SCRIPT_DIR"
echo "      Proyecto eliminado ✅"

echo ""
echo "🗑️  Desinstalación completada!"
echo "============================================"
echo ""
echo "  mpv NO se desinstaló (por si lo usás para otra cosa)."
echo "  Si querés sacarlo: sudo apt-get remove mpv"
echo ""
