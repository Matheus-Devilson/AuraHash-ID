"""
AuraHash ID — Reader (v1.0.0)
==============================

Lee un payload AuraHash (el texto que devuelve escanear el Data Matrix),
descifra las capas médica y administrativa con AES-256-GCM,
verifica la integridad con SHA-256 y muestra todo formateado.

Uso:
    python src/reader.py

Flujo:
    1. El script te pide pegar el payload escaneado.
    2. Lo partes en bloques PUB:, MED:, ADM:, SHA:.
    3. Descifra MED: y ADM: con keys/aes.key.
    4. Verifica el hash maestro (SHA-256).
    5. Imprime todo con formato legible.

Notas:
    - Solo la capa pública es legible sin la clave.
    - Sin keys/aes.key, MED: y ADM: son ilegibles (cifrado real).
"""

import sys
import json
import base64
import hashlib
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# =====================================================================
# CONFIGURACIÓN
# =====================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
KEY_FILE = BASE_DIR / "keys" / "aes.key"

AES_KEY_BYTES = 32
GCM_NONCE_BYTES = 12
PREFIJO_CIFRADO = "AES256GCM:"


# =====================================================================
# CLAVE AES
# =====================================================================

def cargar_clave_aes() -> bytes:
    """Lee y valida keys/aes.key (32 bytes)."""
    if not KEY_FILE.exists():
        raise FileNotFoundError(f"No se encontró la clave AES en: {KEY_FILE}")
    clave = KEY_FILE.read_bytes()
    if len(clave) != AES_KEY_BYTES:
        raise ValueError(
            f"La clave AES debe tener {AES_KEY_BYTES} bytes, tiene {len(clave)}."
        )
    return clave


# =====================================================================
# DESCIFRADO
# =====================================================================

def descifrar_capa(texto_cifrado: str) -> str:
    """
    Descifra un string con formato "AES256GCM:" + base64(nonce || ct || tag).
    Devuelve el texto plano original.
    """
    if not texto_cifrado:
        return ""

    if not texto_cifrado.startswith(PREFIJO_CIFRADO):
        raise ValueError(
            f"El texto no empieza con '{PREFIJO_CIFRADO}'. "
            f"Primeros 30 caracteres: {texto_cifrado[:30]}"
        )

    b64 = texto_cifrado[len(PREFIJO_CIFRADO):]
    paquete = base64.b64decode(b64)

    if len(paquete) < GCM_NONCE_BYTES + 16:  # nonce + tag mínimo
        raise ValueError("El paquete cifrado es demasiado corto.")

    nonce = paquete[:GCM_NONCE_BYTES]
    ct_con_tag = paquete[GCM_NONCE_BYTES:]

    aesgcm = AESGCM(cargar_clave_aes())
    plano_bytes = aesgcm.decrypt(nonce, ct_con_tag, None)
    return plano_bytes.decode("utf-8")


# =====================================================================
# PARSEO DEL PAYLOAD
# =====================================================================

def parsear_payload(payload: str) -> dict:
    """
    Parte el payload en bloques: PUB, MED, ADM, SHA.
    Formato esperado:
        PUB:...|MED:...|ADM:...|SHA:...
    """
    bloques = {"PUB": "", "MED": "", "ADM": "", "SHA": ""}

    # Separar por '|' pero cuidado: los JSON de PUB pueden contener '|'?
    # En nuestro caso no, porque serializamos con separators=(',', ':')
    # y los valores no incluyen '|'.
    partes = payload.strip().split("|")
    for parte in partes:
        if ":" not in parte:
            continue
        prefijo, _, contenido = parte.partition(":")
        prefijo = prefijo.strip().upper()
        if prefijo in bloques:
            bloques[prefijo] = contenido

    return bloques


# =====================================================================
# PRESENTACIÓN
# =====================================================================

def imprimir_seccion(titulo: str) -> None:
    print()
    print(f"--- {titulo} ---")


def imprimir_dict(d: dict, indent: int = 2) -> None:
    if not isinstance(d, dict):
        print(" " * indent + str(d))
        return
    ancho = max((len(k) for k in d.keys()), default=0)
    for k, v in d.items():
        if isinstance(v, list):
            v_str = ", ".join(str(x) for x in v)
        else:
            v_str = str(v)
        print(" " * indent + f"{k:<{ancho}} : {v_str}")


def mostrar_payload(bloques: dict) -> None:
    print()
    print("=" * 60)
    print("  AuraHash ID — Reader v1.0.0")
    print("=" * 60)

    # --- CAPA PÚBLICA ---
    imprimir_seccion("CAPA PÚBLICA (texto claro)")
    if bloques["PUB"]:
        try:
            d = json.loads(bloques["PUB"])
            imprimir_dict(d)
        except json.JSONDecodeError:
            print("  (no se pudo parsear como JSON, mostrando crudo)")
            print("  " + bloques["PUB"])
    else:
        print("  (vacía)")

    # --- CAPA MÉDICA ---
    imprimir_seccion("CAPA MÉDICA (descifrada)")
    if bloques["MED"]:
        try:
            plano = descifrar_capa(bloques["MED"])
            d = json.loads(plano)
            imprimir_dict(d)
        except Exception as e:
            print(f"  [ERROR] No se pudo descifrar: {e}")
    else:
        print("  (vacía)")

    # --- CAPA ADMINISTRATIVA ---
    imprimir_seccion("CAPA ADMINISTRATIVA (descifrada)")
    if bloques["ADM"]:
        try:
            plano = descifrar_capa(bloques["ADM"])
            d = json.loads(plano)
            imprimir_dict(d)
        except Exception as e:
            print(f"  [ERROR] No se pudo descifrar: {e}")
    else:
        print("  (vacía)")

    # --- INTEGRIDAD ---
    imprimir_seccion("INTEGRIDAD (SHA-256)")
    if bloques["SHA"]:
        print(f"  Hash en payload : {bloques['SHA']}")
        print(f"  Longitud        : {len(bloques['SHA'])} caracteres")

        # Recalcular hash maestro a partir de las capas descifradas
        try:
            pub_json = bloques["PUB"]
            med_json = descifrar_capa(bloques["MED"]) if bloques["MED"] else ""
            adm_json = descifrar_capa(bloques["ADM"]) if bloques["ADM"] else ""

            h_pub = hashlib.sha256(pub_json.encode("utf-8")).hexdigest()
            h_med = hashlib.sha256(med_json.encode("utf-8")).hexdigest() if med_json else ""
            h_adm = hashlib.sha256(adm_json.encode("utf-8")).hexdigest() if adm_json else ""

            h_maestro = hashlib.sha256((h_pub + h_med + h_adm).encode("utf-8")).hexdigest()
            print(f"  Hash recalculado: {h_maestro}")

            if len(bloques["SHA"]) == 64:
                if h_maestro == bloques["SHA"]:
                    print("  Estado          : OK (integridad verificada)")
                else:
                    print("  Estado          : FALLO (el contenido fue alterado)")
            else:
                # Hash truncado: comparar solo el prefijo
                if h_maestro.startswith(bloques["SHA"]):
                    print(f"  Estado          : OK (prefijo coincide, hash truncado)")
                else:
                    print(f"  Estado          : FALLO (prefijo no coincide)")
        except Exception as e:
            print(f"  [ERROR] No se pudo verificar: {e}")
    else:
        print("  (no hay hash en el payload)")


# =====================================================================
# PRINCIPAL
# =====================================================================

def main() -> None:
    print()
    print("Pega el payload escaneado (una sola línea) y pulsa Enter:")
    print("(Ejemplo: PUB:{...}|MED:AES256GCM:...|ADM:AES256GCM:...|SHA:...)")
    print()

    try:
        payload = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelado.")
        return

    if not payload:
        print("[ERROR] No pegaste nada.")
        return

    bloques = parsear_payload(payload)

    # Validación mínima
    if not bloques["PUB"] and not bloques["MED"] and not bloques["ADM"]:
        print("[ERROR] El payload no parece válido (no se detectaron bloques PUB/MED/ADM).")
        print(f"Primeros 120 caracteres recibidos: {payload[:120]}")
        return

    mostrar_payload(bloques)


if __name__ == "__main__":
    main()