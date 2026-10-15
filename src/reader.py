"""
AuraHash ID - Reader (v1.3.0)
==============================

Lee un payload AuraHash (el texto que devuelve escanear el Data Matrix),
descifra las capas medica y administrativa con AES-256-GCM,
verifica la integridad con SHA-256, verifica la firma digital Ed25519
(si esta presente) y muestra todo formateado.

Uso:
    python src/reader.py

Flujo:
    1. El script te pide pegar el payload escaneado.
    2. Lo parte en bloques PUB:, MED:, ADM:, SHA:, SIG:.
    3. Descifra MED: y ADM: con keys/aes.key (soporta zlib y sin zlib).
    4. Reconstruye la capa publica (desminifica claves cortas).
    5. Verifica el hash maestro (SHA-256 completo o truncado).
    6. Verifica la firma Ed25519 con keys/ed25519_public.key si existe.
    7. Imprime todo con formato legible.

Cambios v1.3.0:
    - Verifica firma Ed25519 sobre el mensaje "PUB|MED|ADM|SHA".
    - La firma es INFORMATIVA, no bloqueante: nunca revienta el reader.
    - Casos manejados:
        * Con SIG y llave publica disponible -> "FIRMA OK" / "FIRMA FALLO"
        * Sin SIG -> "(payload sin firma, formato legacy)"
        * Con SIG pero sin llave publica -> "[AVISO] No hay llave publica"

Cambios v1.2.0:
    - Soporta prefijos "AES256GCMZ:" (zlib, v2.3.0) y "AES256GCM:" (sin zlib, legacy).
    - Retrocompatible con payloads generados por generator v2.1.0/v2.2.0.

Cambios v1.1.0:
    - Arreglado bug de indentacion en main().
    - Soporta SHA truncado (32 hex) ademas de SHA completo (64 hex).
    - Desminifica las claves cortas de PUB para mostrarlas legibles.
"""

import json
import base64
import hashlib
import zlib
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature


# =====================================================================
# CONFIGURACION
# =====================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
KEY_FILE = BASE_DIR / "keys" / "aes.key"
ED25519_PUB_FILE = BASE_DIR / "keys" / "ed25519_public.key"

AES_KEY_BYTES = 32
GCM_NONCE_BYTES = 12
PREFIJO_CIFRADO = "AES256GCM:"        # legacy, sin zlib
PREFIJO_CIFRADO_ZLIB = "AES256GCMZ:"  # v2.3.0, con zlib

# Mapa inverso al de generator.py: clave corta -> clave larga
MAPA_CLAVES_PUB_INV = {
    "t": "tipo",
    "i": "instruccion",
    "n": "nombre_pila",
    "a": "alergias_criticas",
    "v": "id_visual",
    "e": "evento",
}


# =====================================================================
# CLAVE AES
# =====================================================================

def cargar_clave_aes() -> bytes:
    """Lee y valida keys/aes.key (32 bytes)."""
    if not KEY_FILE.exists():
        raise FileNotFoundError(f"No se encontro la clave AES en: {KEY_FILE}")
    clave = KEY_FILE.read_bytes()
    if len(clave) != AES_KEY_BYTES:
        raise ValueError(
            f"La clave AES debe tener {AES_KEY_BYTES} bytes, tiene {len(clave)}."
        )
    return clave


# =====================================================================
# LLAVE PUBLICA ED25519
# =====================================================================

def cargar_llave_ed25519_publica():
    """
    Carga la llave publica Ed25519 desde keys/ed25519_public.key.
    Devuelve un Ed25519PublicKey, o None si el archivo no existe.
    Lanza ValueError si el archivo existe pero no tiene 32 bytes.
    """
    if not ED25519_PUB_FILE.exists():
        return None
    pub_bytes = ED25519_PUB_FILE.read_bytes()
    if len(pub_bytes) != 32:
        raise ValueError(
            f"La llave publica Ed25519 debe tener 32 bytes, tiene {len(pub_bytes)}."
        )
    return Ed25519PublicKey.from_public_bytes(pub_bytes)


# =====================================================================
# DESCIFRADO (soporta zlib y legacy)
# =====================================================================

def descifrar_capa(texto_cifrado: str) -> str:
    """
    Descifra un string con uno de estos formatos:
        "AES256GCMZ:" + base64(nonce(12) || AES-GCM(zlib(plano)) || tag(16))
        "AES256GCM:"  + base64(nonce(12) || AES-GCM(plano)        || tag(16))
    Devuelve el texto plano original.
    """
    if not texto_cifrado:
        return ""

    if texto_cifrado.startswith(PREFIJO_CIFRADO_ZLIB):
        usar_zlib = True
        b64 = texto_cifrado[len(PREFIJO_CIFRADO_ZLIB):]
    elif texto_cifrado.startswith(PREFIJO_CIFRADO):
        usar_zlib = False
        b64 = texto_cifrado[len(PREFIJO_CIFRADO):]
    else:
        raise ValueError(
            f"El texto no empieza con '{PREFIJO_CIFRADO_ZLIB}' ni '{PREFIJO_CIFRADO}'. "
            f"Primeros 30 caracteres: {texto_cifrado[:30]}"
        )

    paquete = base64.b64decode(b64)

    if len(paquete) < GCM_NONCE_BYTES + 16:
        raise ValueError("El paquete cifrado es demasiado corto.")

    nonce = paquete[:GCM_NONCE_BYTES]
    ct_con_tag = paquete[GCM_NONCE_BYTES:]

    aesgcm = AESGCM(cargar_clave_aes())
    plano_bytes = aesgcm.decrypt(nonce, ct_con_tag, None)

    if usar_zlib:
        plano_bytes = zlib.decompress(plano_bytes)

    return plano_bytes.decode("utf-8")


# =====================================================================
# DESMINIFICACION DE LA CAPA PUBLICA
# =====================================================================

def desminificar_capa_publica(capa: dict) -> dict:
    """
    Reconstruye las claves largas de la capa publica a partir de las cortas.
    Si una clave ya es larga (payload viejo), se conserva tal cual.
    """
    if not isinstance(capa, dict):
        return capa
    return {MAPA_CLAVES_PUB_INV.get(k, k): v for k, v in capa.items()}


# =====================================================================
# PARSEO DEL PAYLOAD
# =====================================================================

def parsear_payload(payload: str) -> dict:
    """
    Parte el payload en bloques: PUB, MED, ADM, SHA, SIG.
    Formato esperado: PUB:...|MED:...|ADM:...|SHA:...|SIG:...
    El bloque SIG es opcional (payloads legacy no lo tienen).
    """
    bloques = {"PUB": "", "MED": "", "ADM": "", "SHA": "", "SIG": ""}

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
# VERIFICACION DE FIRMA ED25519
# =====================================================================

def verificar_firma(bloques: dict) -> str:
    """
    Verifica la firma Ed25519 del payload (si esta presente).

    Reglas:
        - Sin SIG -> "(payload sin firma, formato legacy)"
        - Con SIG pero sin llave publica -> "[AVISO] No hay llave publica"
        - Con SIG y llave publica -> "FIRMA OK" o "FIRMA FALLO"

    NUNCA lanza excepcion. Devuelve un string con el resultado.
    """
    sig_b64 = bloques.get("SIG", "")
    if not sig_b64:
        return "(payload sin firma, formato legacy)"

    # Reconstruir el mensaje firmado: PUB|MED|ADM|SHA (sin SIG)
    mensaje = (
        f"PUB:{bloques['PUB']}"
        f"|MED:{bloques['MED']}"
        f"|ADM:{bloques['ADM']}"
        f"|SHA:{bloques['SHA']}"
    )

    try:
        pub_key = cargar_llave_ed25519_publica()
    except ValueError as e:
        return f"[AVISO] Llave publica invalida: {e}"

    if pub_key is None:
        return "[AVISO] No hay llave publica (keys/ed25519_public.key)"

    try:
        firma_bytes = base64.b64decode(sig_b64)
    except Exception as e:
        return f"FIRMA FALLO (base64 invalido: {e})"

    if len(firma_bytes) != 64:
        return f"FIRMA FALLO (longitud incorrecta: {len(firma_bytes)} bytes, esperado 64)"

    try:
        pub_key.verify(firma_bytes, mensaje.encode("utf-8"))
        return "FIRMA OK"
    except InvalidSignature:
        return "FIRMA FALLO (la firma no coincide con el contenido)"
    except Exception as e:
        return f"FIRMA FALLO (error inesperado: {e})"


# =====================================================================
# PRESENTACION
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
    print("  AuraHash ID - Reader v1.3.0")
    print("=" * 60)

    # --- CAPA PUBLICA ---
    imprimir_seccion("CAPA PUBLICA (texto claro)")
    if bloques["PUB"]:
        try:
            d = json.loads(bloques["PUB"])
            d = desminificar_capa_publica(d)
            imprimir_dict(d)
        except json.JSONDecodeError:
            print("  (no se pudo parsear como JSON, mostrando crudo)")
            print("  " + bloques["PUB"])
    else:
        print("  (vacia)")

    # --- CAPA MEDICA ---
    imprimir_seccion("CAPA MEDICA (descifrada)")
    if bloques["MED"]:
        try:
            plano = descifrar_capa(bloques["MED"])
            d = json.loads(plano)
            imprimir_dict(d)
        except Exception as e:
            print(f"  [ERROR] No se pudo descifrar: {e}")
    else:
        print("  (vacia)")

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
        print("  (vacia)")

    # --- INTEGRIDAD SHA-256 ---
    imprimir_seccion("INTEGRIDAD (SHA-256)")
    if bloques["SHA"]:
        print(f"  Hash en payload : {bloques['SHA']}")
        print(f"  Longitud        : {len(bloques['SHA'])} caracteres")

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
                    print("  Estado          : OK (integridad verificada, SHA completo)")
                else:
                    print("  Estado          : FALLO (el contenido fue alterado)")
            else:
                if h_maestro.startswith(bloques["SHA"]):
                    print(f"  Estado          : OK (prefijo coincide, SHA truncado a {len(bloques['SHA'])} hex)")
                else:
                    print("  Estado          : FALLO (prefijo no coincide)")
        except Exception as e:
            print(f"  [ERROR] No se pudo verificar: {e}")
    else:
        print("  (no hay hash en el payload)")

    # --- FIRMA DIGITAL ED25519 ---
    imprimir_seccion("FIRMA DIGITAL (Ed25519)")
    if bloques["SIG"]:
        print(f"  Firma en payload: {bloques['SIG'][:32]}...")
        print(f"  Longitud firma  : {len(bloques['SIG'])} caracteres (base64)")
    else:
        print("  (no hay firma en el payload)")
    resultado = verificar_firma(bloques)
    print(f"  Estado          : {resultado}")


# =====================================================================
# PRINCIPAL
# =====================================================================

def main() -> None:
    print()
    print("Pega el payload escaneado (una sola linea) y pulsa Enter:")
    print("(Ejemplo: PUB:{...}|MED:AES256GCMZ:...|ADM:AES256GCMZ:...|SHA:...|SIG:...)")
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

    if not bloques["PUB"] and not bloques["MED"] and not bloques["ADM"]:
        print("[ERROR] El payload no parece valido (no se detectaron bloques PUB/MED/ADM).")
        print(f"Primeros 120 caracteres recibidos: {payload[:120]}")
        return

    mostrar_payload(bloques)


if __name__ == "__main__":
    main()