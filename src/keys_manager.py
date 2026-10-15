"""
AuraHash ID - Gestor de llaves Ed25519
=======================================
Genera el par de llaves Ed25519 usado para firmar el payload.

Uso:
    python src/keys_manager.py           # genera si no existen, aborta si existen
    python src/keys_manager.py --force   # regenera (SOBRESCRIBE)

Archivos:
    keys/ed25519_private.key  (32 bytes raw, NUNCA va a git)
    keys/ed25519_public.key   (32 bytes raw, SI va a git)
"""

import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


# --- Rutas ---
RAIZ = Path(__file__).resolve().parent.parent
KEYS_DIR = RAIZ / "keys"
PRIV_PATH = KEYS_DIR / "ed25519_private.key"
PUB_PATH = KEYS_DIR / "ed25519_public.key"


def _imprimir_banner():
    print("=" * 60)
    print("  AuraHash ID - Gestor de llaves Ed25519")
    print("=" * 60)


def _abortar(msg: str, code: int = 1):
    print(f"[ERROR] {msg}")
    sys.exit(code)


def _existen_llaves() -> bool:
    return PRIV_PATH.exists() or PUB_PATH.exists()


def _generar_llaves():
    # Asegurar directorio
    KEYS_DIR.mkdir(parents=True, exist_ok=True)

    # Generar par
    priv = Ed25519PrivateKey.generate()
    priv_bytes = priv.private_bytes_raw()          # 32 bytes
    pub_bytes = priv.public_key().public_bytes_raw()  # 32 bytes

    # Validacion defensiva de longitud
    if len(priv_bytes) != 32 or len(pub_bytes) != 32:
        _abortar(
            f"Longitudes inesperadas: priv={len(priv_bytes)} pub={len(pub_bytes)}. "
            "Esperado 32 y 32."
        )

    # Escribir raw bytes
    PRIV_PATH.write_bytes(priv_bytes)
    PUB_PATH.write_bytes(pub_bytes)

    print(f"[OK] Llave privada -> {PRIV_PATH} ({len(priv_bytes)} bytes)")
    print(f"[OK] Llave publica -> {PUB_PATH} ({len(pub_bytes)} bytes)")
    print()
    print("ADVERTENCIA:")
    print("  - La llave PRIVADA NUNCA debe subirse a git.")
    print("  - Verifica que .gitignore incluya keys/ed25519_private.key")
    print("  - La llave PUBLICA SI debe trackearse en git.")
    print()
    print("Siguiente paso:")
    print("  git status  # confirma que solo ed25519_public.key es nueva")


def main():
    _imprimir_banner()

    force = "--force" in sys.argv[1:]

    if _existen_llaves() and not force:
        _abortar(
            "Ya existen llaves Ed25519 en keys/. "
            "No se sobrescriben por seguridad. "
            "Usa --force si de verdad quieres regenerarlas "
            "(esto invalida todas las firmas anteriores)."
        )

    if _existen_llaves() and force:
        print("[AVISO] --force detectado. Regenerando llaves existentes...")
        print("        Las firmas previas quedaran invalidas.")
        print()

    _generar_llaves()


if __name__ == "__main__":
    main()