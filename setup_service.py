#!/usr/bin/env python3
"""Instalador interactivo del Sistema de Timbres Escolar.

Configura rutas, genera .env, instala servicio systemd.
Uso:
    python3 setup_service.py              # Modo interactivo
    python3 setup_service.py --quick      # Solo mostrar configuración actual
    python3 setup_service.py --install    # Instalar servicio systemd
"""

import argparse
import getpass
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ── Nosotros mismos detectamos rutas (sin importar src.config aún) ──
PROJECT_DIR = Path(__file__).resolve().parent


def print_header(text: str):
    """Print a section header."""
    print("")
    print("=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_step(num: int, text: str):
    """Print a step."""
    print(f"\n  📌 Paso {num}: {text}")


def ask(question: str, default: str = "") -> str:
    """Ask the user a question with an optional default."""
    if default:
        result = input(f"  💬 {question} [{default}]: ").strip()
        return result if result else default
    return input(f"  💬 {question}: ").strip()


def confirm(question: str, default: bool = True) -> bool:
    """Ask yes/no."""
    suffix = " (S/n)" if default else " (s/N)"
    result = input(f"  💬 {question}{suffix}: ").strip().lower()
    if not result:
        return default
    return result in ("s", "si", "y", "yes")


def detect_current_config() -> dict:
    """Detect current project configuration."""
    config = {
        "project_dir": PROJECT_DIR,
        "user": getpass.getuser(),
        "music_dir": Path.home() / "musica",
        "static_dir": PROJECT_DIR / "static",
        "state_dir": PROJECT_DIR / "state",
    }

    # Try to load from existing .env
    env_file = PROJECT_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key, value = key.strip(), value.strip()
                if key == "MUSIC_DIR":
                    config["music_dir"] = Path(value)
                elif key == "STATIC_DIR":
                    config["static_dir"] = Path(value)
                elif key in ("USER", "WEB_USER"):
                    config["web_user"] = value
                elif key in ("PASSWORD", "WEB_PASSWORD"):
                    config["web_password"] = value

    return config


def show_config(config: dict):
    """Display current configuration."""
    print("\n  ┌─────────────────────────────────────────────┐")
    print("  │         CONFIGURACIÓN ACTUAL                │")
    print("  ├─────────────────────────────────────────────┤")
    print(f"  │  Proyecto:    {str(config['project_dir']):<29} │")
    print(f"  │  Usuario:     {config['user']:<29} │")
    print(f"  │  Música:      {str(config['music_dir']):<29} │")
    print(f"  │  Estáticos:   {str(config['static_dir']):<29} │")
    print(f"  │  Estado:      {str(config['state_dir']):<29} │")
    if config.get("web_user"):
        print(f"  │  Web usuario: {config['web_user']:<29} │")
    if config.get("web_password"):
        print(f"  │  Web pass:    {'*' * len(str(config['web_password'])):<29} │")
    print("  └─────────────────────────────────────────────┘")


def interactive_setup(config: dict) -> dict:
    """Run interactive configuration."""
    print_header("CONFIGURACIÓN DEL SISTEMA DE TIMBRES")
    print("\n  Vamos a configurar el sistema paso a paso.")
    print("  En cada paso podés aceptar el valor por defecto")
    print("  apretando Enter, o escribir tu propio valor.\n")

    # Paso 1: Carpeta de música
    print_step(1, "¿DÓNDE ESTÁN TUS CARPETAS DE MÚSICA?")
    print("     El sistema busca carpetas como 'entrada', 'salida',")
    print("     'cambio', 'recreo' con archivos de audio.")
    music = ask("Ruta de la música", str(config["music_dir"]))
    config["music_dir"] = Path(music)

    # Paso 2: Carpeta de archivos estáticos
    print_step(2, "¿DÓNDE VAN LOS ARCHIVOS ESTÁTICOS?")
    print("     Acá van imágenes, CSS, JS. Si no sabés, dejá el default.")
    static = ask("Ruta de archivos estáticos", str(config["static_dir"]))
    config["static_dir"] = Path(static)

    # Paso 3: Usuario web
    print_step(3, "USUARIO Y CONTRASEÑA PARA LA WEB")
    print("     Con esto vas a iniciar sesión en la interfaz web.")
    web_user = ask("Usuario", config.get("web_user", "admin"))
    web_pass = ask("Contraseña", config.get("web_password", "eit2021"))
    config["web_user"] = web_user
    config["web_password"] = web_pass

    # Paso 4: Servicio systemd
    print_step(4, "SERVICIO WEB (INICIO AUTOMÁTICO)")
    print("     Esto hace que la web arranque sola al encender la PC.")
    install_svc = confirm("¿Instalar el servicio web ahora?")

    print("")
    return config


MUSIC_SUBDIRS = ["entrada", "salida", "cambio", "recreo"]


def ensure_all_dirs(config: dict) -> None:
    """Create all necessary directories (music, state, static)."""
    print("\n  ─── Verificando carpetas necesarias ───")

    # State dir
    state_dir = config["state_dir"]
    if not state_dir.exists():
        state_dir.mkdir(parents=True)
        print(f"  ✅ Creada: {state_dir}")
    else:
        print(f"  • Ya existe: {state_dir}")

    # Static dir
    static_dir = config["static_dir"]
    if not static_dir.exists():
        static_dir.mkdir(parents=True)
        print(f"  ✅ Creada: {static_dir}")
    else:
        print(f"  • Ya existe: {static_dir}")

    # Music subdirectories (entrada, salida, cambio, recreo)
    music_dir = config["music_dir"]
    for subdir in ["entrada", "salida", "cambio", "recreo"]:
        path = music_dir / subdir
        if not path.exists():
            path.mkdir(parents=True)
            print(f"  ✅ Creada: {path}")
        else:
            print(f"  • Ya existe: {path}")

    print("  ─── Todas las carpetas listas ───")


def save_env(config: dict) -> Path:
    """Save configuration to .env file."""
    env_path = PROJECT_DIR / ".env"
    content = f"""# Configuración del Sistema de Timbres Escolar
# Generado por setup_service.py el {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')}

# Usuario y contraseña para la interfaz web
WEB_USER={config["web_user"]}
WEB_PASSWORD={config["web_password"]}

# Ruta a las carpetas de música (entrada, salida, cambio, recreo)
MUSIC_DIR={config["music_dir"]}

# Ruta a archivos estáticos (imágenes, CSS, JS)
STATIC_DIR={config["static_dir"]}
"""
    env_path.write_text(content)
    print(f"\n  ✅ Configuración guardada en: {env_path}")
    return env_path


def generate_service(config: dict) -> str:
    """Generate systemd service file content."""
    return f"""[Unit]
Description=School Bell System - Flask Web Interface
After=network.target

[Service]
Type=simple
User={config["user"]}
WorkingDirectory={config["project_dir"]}
ExecStart=/usr/bin/python3 {config["project_dir"]}/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""


def install_service(config: dict) -> bool:
    """Install the systemd service file."""
    content = generate_service(config)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.service', delete=False) as f:
        f.write(content)
        tmp_path = f.name

    try:
        shutil.copy(tmp_path, '/etc/systemd/system/bell-server.service')
        subprocess.run(['systemctl', 'daemon-reload'], check=True)
        return True
    except PermissionError:
        print("  ❌ No tengo permisos para instalar el servicio.")
        print("     Ejecutá estos comandos manualmente:")
        print(f"       sudo cp bell-server.service /etc/systemd/system/")
        print(f"       sudo systemctl daemon-reload")
        return False
    except subprocess.CalledProcessError:
        print("  ⚠️  Servicio copiado pero no se pudo recargar systemd.")
        return False
    finally:
        os.unlink(tmp_path)


def main():
    parser = argparse.ArgumentParser(
        description="Instalador interactivo del Sistema de Timbres Escolar"
    )
    parser.add_argument('--install', action='store_true',
                        help="Instalar servicio systemd directamente")
    parser.add_argument('--quick', action='store_true',
                        help="Mostrar configuración actual y salir")
    args = parser.parse_args()

    config = detect_current_config()

    if args.quick:
        show_config(config)
        return

    if args.install:
        content = generate_service(config)
        tmp = "/tmp/bell-server.service"
        Path(tmp).write_text(content)
        ret = os.system(f"cp {tmp} /etc/systemd/system/bell-server.service && systemctl daemon-reload 2>/dev/null")
        os.unlink(tmp)
        if ret == 0:
            print("✅ Servicio instalado en /etc/systemd/system/bell-server.service")
            if confirm("¿Activarlo ahora?"):
                os.system("systemctl enable --now bell-server.service")
                print("✅ Servicio activado, la web arranca sola al prender la PC")
        else:
            print("❌ No tengo permisos. Ejecutá con sudo:")
            print(f"   sudo python3 {__file__} --install")
        return

    # ── Modo interactivo ──
    print_header("INSTALADOR DEL SISTEMA DE TIMBRES ESCOLAR")

    show_config(config)

    if confirm("¿Querés modificar la configuración?"):
        config = interactive_setup(config)
        show_config(config)
    else:
        print("\n  → Se usará la configuración actual.")

    # Guardar .env
    save_env(config)

    # Crear todas las carpetas necesarias
    ensure_all_dirs(config)

    # Servicio systemd
    if confirm("¿Querés instalar el servicio web (inicio automático)?"):
        content = generate_service(config)
        tmp_path = "/tmp/bell-server.service"
        Path(tmp_path).write_text(content)
        result = os.system(f"sudo cp {tmp_path} /etc/systemd/system/bell-server.service && sudo systemctl daemon-reload")
        os.unlink(tmp_path)
        if result == 0:
            print("\n  ✅ Servicio web instalado!")
            if confirm("¿Activarlo ahora para que arranque al prender la PC?"):
                os.system("sudo systemctl enable --now bell-server.service")
                print("\n  ✅ Servicio activado! La web arranca sola al prender la PC.")
                print(f"     Abrí http://localhost:5000 en el navegador")
        else:
            print("\n  ⚠️  No se pudo instalar. Hacelo manual:")
            print(f"       sudo python3 {__file__} --install")
    else:
        print("\n  → Omitido. Para instalarlo después:")
        print(f"       sudo python3 {__file__} --install")

    # Resumen final
    print_header("INSTALACIÓN COMPLETADA 🎉")
    print(f"""
  Resumen:
  📁 Proyecto:   {config['project_dir']}
  🎵 Música:     {config['music_dir']}
  🖼️  Estáticos: {config['static_dir']}
  🔐 Web:        {config['web_user']} / {'*' * len(config['web_password'])}
  ⚙️  Servicio:   {'Instalado' if False else 'Pendiente'}

  Próximos pasos:
  1. Copiá tus archivos de audio a las carpetas en {config['music_dir']}
     (entrada/, salida/, cambio/, recreo/)

  2. Configurá los horarios de los timbres:
       python3 bell.py --setup-cron

  3. Probá que funcione:
       python3 bell.py cambio
       python3 app.py  (abrí http://localhost:5000)

  4. Ejecutá los tests para verificar:
       python3 -m unittest discover -s tests

  5. Si todo funciona, activá el servicio web:
       sudo systemctl enable --now bell-server.service
""")


if __name__ == "__main__":
    main()
