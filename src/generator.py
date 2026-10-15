"""
AuraHash ID - Generador Universal v2.4.0
==========================================

Este script lee un archivo JSON con escenarios organizados en 3 capas:
  - capa_publica:         Visible con Google Lens. Cero datos sensibles.
  - capa_medica:          Datos de salud (cifrados AES-256-GCM + zlib al vuelo).
  - capa_administrativa:  Datos legales/financieros (cifrados AES-256-GCM + zlib).

Para cada escenario genera una imagen AuraHash con:
  - Un codigo Data Matrix real (ISO/IEC 16022), escaneable por Google Lens.
  - Un "Aura Estocastica" (patron de ruido determinista) alrededor.
  - Los hashes SHA-256 de cada capa visibles/embebidos para verificacion.
  - Una firma digital Ed25519 sobre el payload completo (integridad end-to-end).

Cifrado:
  - AES-256-GCM (cifrado autenticado: confidencialidad + integridad).
  - zlib.compress ANTES de cifrar capas sensibles (reduce ~40% el ciphertext).
  - Clave maestra en keys/aes.key (32 bytes), ignorada por .gitignore.
  - Formato del ciphertext v2.3.0:
        "AES256GCMZ:" + base64(nonce(12) || AES-GCM(zlib(texto)) || tag(16))
    Formato antiguo (retrocompatible en reader):
        "AES256GCM:"  + base64(nonce(12) || AES-GCM(texto) || tag(16))
  - La capa publica NUNCA se cifra (es info de emergencia).

Firma digital (v2.4.0, pendiente #5):
  - Ed25519 sobre el mensaje:
        "PUB:{pub}|MED:{med}|ADM:{adm}|SHA:{sha}"
    (NO se firma el bloque SIG: para evitar recursion).
  - Llave privada en keys/ed25519_private.key (32 bytes, NUNCA va a git).
  - Llave publica en keys/ed25519_public.key  (32 bytes, SI va a git).
  - Firma (64 bytes) codificada en base64 y anexada al final:
        "...|SIG:{base64(64 bytes)}"
  - Si no existen llaves, el payload se genera SIN firma (retrocompatible).

Optimizaciones v2.2.0/v2.3.0 (pendiente #4):
  - La capa publica se MINIFICA (claves cortas). Sigue legible por Google Lens.
  - El SHA maestro en payload se trunca a 32 hex (128 bits).
    El hash completo (64 hex) se sigue usando para el Aura interna.
  - MED y ADM se comprimen con zlib antes de cifrar (v2.3.0).
  - MED y ADM NO se debilitan: mismo AES-256-GCM, mismo nonce 12, mismo tag 16.

Uso:
    python src/generator.py

Entrada:
    data/example_data.json
    keys/aes.key
    keys/ed25519_private.key   (opcional; si falta, se omite la firma)

Salida:
    output/aura_<id_escenario>.png
"""

import json
import hashlib
import io
import base64
import secrets
import zlib
from pathlib import Path

import numpy as np
import segno
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


# =====================================================================
# CONFIGURACION GLOBAL
# =====================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "example_data.json"
OUTPUT_DIR = BASE_DIR / "output"
KEY_FILE = BASE_DIR / "keys" / "aes.key"
ED25519_PRIV_FILE = BASE_DIR / "keys" / "ed25519_private.key"

# Cifrado AES-256-GCM
AES_KEY_BYTES = 32
GCM_NONCE_BYTES = 12
PREFIJO_CIFRADO = "AES256GCM:"        # payload antiguo, sin comprimir
PREFIJO_CIFRADO_ZLIB = "AES256GCMZ:"  # payload nuevo, con zlib

# Longitud del SHA maestro embebido en el payload (32 hex = 128 bits)
SHA_PAYLOAD_HEX = 32

# --- Dimensiones de la imagen final ---
IMG_WIDTH = 800
IMG_HEIGHT = 800
AURA_SIZE = 600
DM_SIZE = 360
DM_QUIET_ZONE = 4

# --- Colores ---
COLOR_BG = (255, 255, 255)
COLOR_DM = (0, 0, 0)
COLOR_AURA_BG = (10, 10, 20)
COLOR_TEXT = (30, 30, 30)
COLOR_TEXT_HASH = (80, 80, 80)

AURA_PALETTE = [
    (0, 200, 255),
    (255, 0, 180),
    (120, 0, 255),
    (0, 255, 150),
    (255, 180, 0),
]

# --- Mapa de minificacion de la capa publica ---
MAPA_CLAVES_PUB = {
    "tipo": "t",
    "instruccion": "i",
    "nombre_pila": "n",
    "alergias_criticas": "a",
    "id_visual": "v",
    "evento": "e",
}


# =====================================================================
# CIFRADO AES-256-GCM + ZLIB
# =====================================================================

def cargar_clave_aes() -> bytes:
    """Lee la clave AES de keys/aes.key y valida que sean 32 bytes."""
    if not KEY_FILE.exists():
        raise FileNotFoundError(
            f"No se encontro la clave AES en: {KEY_FILE}\n"
            f"Generala con:\n"
            f"  python -c \"import secrets, pathlib; "
            f"pathlib.Path('keys').mkdir(exist_ok=True); "
            f"pathlib.Path('keys/aes.key').write_bytes(secrets.token_bytes(32))\""
        )
    clave = KEY_FILE.read_bytes()
    if len(clave) != AES_KEY_BYTES:
        raise ValueError(
            f"La clave AES debe tener {AES_KEY_BYTES} bytes, "
            f"pero tiene {len(clave)}."
        )
    return clave


def cifrar_capa(texto: str) -> str:
    """
    Cifra un texto con AES-256-GCM tras comprimirlo con zlib.

    Pipeline:
        texto (utf-8) -> zlib.compress(level=9) -> AES-256-GCM -> base64
    Salida:
        "AES256GCMZ:" + base64(nonce(12) || ciphertext || tag(16))
    Si el texto esta vacio, devuelve cadena vacia.
    """
    if not texto:
        return ""

    clave = cargar_clave_aes()
    aesgcm = AESGCM(clave)

    # 1. Comprimir el texto plano. reduce ~40% en JSONs repetitivos.
    plano_comprimido = zlib.compress(texto.encode("utf-8"), level=9)

    # 2. Cifrar el comprimido con AES-256-GCM.
    nonce = secrets.token_bytes(GCM_NONCE_BYTES)
    ciphertext_con_tag = aesgcm.encrypt(nonce, plano_comprimido, None)

    # 3. Empaquetar nonce + (ciphertext || tag) y codificar en base64.
    paquete = nonce + ciphertext_con_tag
    b64 = base64.b64encode(paquete).decode("ascii")

    return PREFIJO_CIFRADO_ZLIB + b64


# =====================================================================
# FIRMA DIGITAL ED25519
# =====================================================================

def cargar_llave_ed25519_privada():
    """
    Carga la llave privada Ed25519 desde keys/ed25519_private.key.
    Devuelve el objeto Ed25519PrivateKey, o None si el archivo no existe.
    """
    if not ED25519_PRIV_FILE.exists():
        return None
    priv_bytes = ED25519_PRIV_FILE.read_bytes()
    if len(priv_bytes) != 32:
        raise ValueError(
            f"La llave privada Ed25519 debe tener 32 bytes, "
            f"pero tiene {len(priv_bytes)}."
        )
    return Ed25519PrivateKey.from_private_bytes(priv_bytes)


def firmar_payload(mensaje: str, priv_key) -> str:
    """
    Firma 'mensaje' (str utf-8) con Ed25519 y devuelve "SIG:{base64}".
    Si priv_key es None, devuelve cadena vacia (sin firma).
    """
    if priv_key is None:
        return ""
    firma_bytes = priv_key.sign(mensaje.encode("utf-8"))  # 64 bytes
    b64 = base64.b64encode(firma_bytes).decode("ascii")
    return f"|SIG:{b64}"


# =====================================================================
# MINIFICACION DE LA CAPA PUBLICA
# =====================================================================

def minificar_capa_publica(capa: dict) -> dict:
    """
    Renombra las claves largas de la capa publica a claves cortas.
    Si una clave no esta en el mapa, se conserva tal cual.
    """
    if not isinstance(capa, dict):
        return capa
    return {MAPA_CLAVES_PUB.get(k, k): v for k, v in capa.items()}


# =====================================================================
# AURA ESTOCASTICA
# =====================================================================

def generar_aura(hash_hex: str, tamano: int) -> Image.Image:
    """
    Genera el patron de ruido determinista (Aura) a partir de un hash SHA-256.
    El mismo hash SIEMPRE produce el mismo patron (determinismo).
    Un cambio de un solo bit produce un patron completamente distinto.
    """
    semilla = int(hash_hex[:16], 16)

    rng = np.random.default_rng(semilla)

    ruido_brillo = rng.random((tamano, tamano))
    ruido_color = rng.random((tamano, tamano))

    indice_color = semilla % len(AURA_PALETTE)
    color_base = AURA_PALETTE[indice_color]

    fondo = np.array(COLOR_AURA_BG, dtype=float)
    color = np.array(color_base, dtype=float)

    factor = ruido_brillo[..., np.newaxis] ** 2
    matriz_rgb = fondo + (color - fondo) * factor

    indice_color2 = (semilla // 7) % len(AURA_PALETTE)
    color_secundario = np.array(AURA_PALETTE[indice_color2], dtype=float)
    mascara_secundaria = (ruido_color > 0.75)[..., np.newaxis]
    matriz_rgb = np.where(
        mascara_secundaria,
        matriz_rgb * 0.5 + color_secundario * 0.5,
        matriz_rgb
    )

    matriz_rgb = np.clip(matriz_rgb, 0, 255).astype(np.uint8)

    aura_img = Image.fromarray(matriz_rgb, mode="RGB")

    mascara = Image.new("L", (tamano, tamano), 0)
    draw_mask = ImageDraw.Draw(mascara)
    radio = int(tamano * 0.48)
    centro = tamano // 2
    draw_mask.ellipse(
        (centro - radio, centro - radio, centro + radio, centro + radio),
        fill=255
    )
    mascara = mascara.filter(ImageFilter.GaussianBlur(radius=tamano // 30))

    fondo_blanco = Image.new("RGB", (tamano, tamano), COLOR_BG)
    aura_final = Image.composite(aura_img, fondo_blanco, mascara)

    return aura_final


# =====================================================================
# DATA MATRIX
# =====================================================================

def generar_data_matrix(texto: str, tamano: int) -> Image.Image:
    """Genera un Data Matrix real (ISO/IEC 16022) a partir de un texto."""
    qr = segno.make(texto, micro=False)

    buffer = io.BytesIO()
    qr.save(
        buffer,
        kind="png",
        scale=10,
        border=DM_QUIET_ZONE,
        dark="black",
        light="white",
    )
    buffer.seek(0)

    dm_img = Image.open(buffer).convert("RGB")
    dm_img = dm_img.resize((tamano, tamano), Image.LANCZOS)

    return dm_img


# =====================================================================
# FUENTE
# =====================================================================

def obtener_fuente(tamano: int) -> ImageFont.ImageFont:
    """Intenta cargar una fuente monoespaciada del sistema."""
    candidatas = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    for ruta in candidatas:
        try:
            return ImageFont.truetype(ruta, tamano)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


# =====================================================================
# COMPOSICION DE LA IMAGEN FINAL
# =====================================================================

def componer_imagen(
    aura: Image.Image,
    data_matrix: Image.Image,
    hash_publico: str,
    id_escenario: str,
    sector: str,
) -> Image.Image:
    """Compone la imagen final: fondo blanco + aura + data matrix + texto."""
    lienzo = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), COLOR_BG)
    draw = ImageDraw.Draw(lienzo)

    aura_x = (IMG_WIDTH - AURA_SIZE) // 2
    aura_y = (IMG_HEIGHT - AURA_SIZE) // 2
    lienzo.paste(aura, (aura_x, aura_y))

    dm_x = (IMG_WIDTH - DM_SIZE) // 2
    dm_y = (IMG_HEIGHT - DM_SIZE) // 2
    lienzo.paste(data_matrix, (dm_x, dm_y))

    fuente_titulo = obtener_fuente(38)
    texto_titulo = "AuraHash ID"
    bbox = draw.textbbox((0, 0), texto_titulo, font=fuente_titulo)
    ancho_titulo = bbox[2] - bbox[0]
    draw.text(
        ((IMG_WIDTH - ancho_titulo) // 2, 30),
        texto_titulo,
        fill=COLOR_TEXT,
        font=fuente_titulo,
    )

    fuente_sector = obtener_fuente(18)
    texto_sector = f"[{sector.upper()}]"
    draw.text((IMG_WIDTH - 160, 40), texto_sector, fill=COLOR_TEXT, font=fuente_sector)

    fuente_hash = obtener_fuente(22)
    hash_truncado = hash_publico[:20].upper()
    hash_formateado = " ".join(
        hash_truncado[i:i + 4] for i in range(0, len(hash_truncado), 4)
    )
    bbox = draw.textbbox((0, 0), hash_formateado, font=fuente_hash)
    ancho_hash = bbox[2] - bbox[0]
    draw.text(
        ((IMG_WIDTH - ancho_hash) // 2, IMG_HEIGHT - 130),
        hash_formateado,
        fill=COLOR_TEXT_HASH,
        font=fuente_hash,
    )

    fuente_id = obtener_fuente(16)
    texto_id = f"ID: {id_escenario}"
    bbox = draw.textbbox((0, 0), texto_id, font=fuente_id)
    ancho_id = bbox[2] - bbox[0]
    draw.text(
        ((IMG_WIDTH - ancho_id) // 2, IMG_HEIGHT - 95),
        texto_id,
        fill=COLOR_TEXT_HASH,
        font=fuente_id,
    )

    fuente_instr = obtener_fuente(15)
    texto_instr = "Escanee con Google Lens / WeChat"
    bbox = draw.textbbox((0, 0), texto_instr, font=fuente_instr)
    ancho_instr = bbox[2] - bbox[0]
    draw.text(
        ((IMG_WIDTH - ancho_instr) // 2, IMG_HEIGHT - 60),
        texto_instr,
        fill=COLOR_TEXT,
        font=fuente_instr,
    )

    return lienzo


# =====================================================================
# SERIALIZACION CANONICA
# =====================================================================

def serializar_capa(capa) -> str:
    """Serializa una capa a JSON canonico. None -> cadena vacia."""
    if capa is None:
        return ""
    return json.dumps(capa, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


# =====================================================================
# PROCESAR UN ESCENARIO
# =====================================================================

def procesar_escenario(escenario: dict, priv_key) -> Path:
    """
    Procesa un unico escenario (3 capas) y devuelve la ruta PNG.
    Aplica AES-256-GCM + zlib a capa_medica y capa_administrativa.
    La capa_publica se minifica (claves cortas) pero sigue en claro.
    Firma el payload completo con Ed25519 si priv_key esta disponible.
    """
    id_escenario = escenario["id"]
    sector = escenario.get("sector", "general")
    capa_publica = escenario.get("capa_publica")
    capa_medica = escenario.get("capa_medica")
    capa_administrativa = escenario.get("capa_administrativa")

    # 1. Minificar la capa publica (claves cortas) y serializar
    capa_publica_min = minificar_capa_publica(capa_publica) if capa_publica else None
    json_publica = serializar_capa(capa_publica_min)

    # 2. Serializar capas sensibles en claro (para hashes)
    json_medica_plano = serializar_capa(capa_medica)
    json_admin_plano = serializar_capa(capa_administrativa)

    # 3. Cifrar capas sensibles con AES-256-GCM + zlib
    json_medica = cifrar_capa(json_medica_plano)
    json_admin = cifrar_capa(json_admin_plano)

    # 4. Hash SHA-256 de cada capa (sobre el texto plano ORIGINAL, no comprimido,
    #    para que el hash sea estable independientemente del formato de salida)
    hash_publica = hashlib.sha256(json_publica.encode("utf-8")).hexdigest()
    hash_medica = (
        hashlib.sha256(json_medica_plano.encode("utf-8")).hexdigest()
        if json_medica_plano else ""
    )
    hash_admin = (
        hashlib.sha256(json_admin_plano.encode("utf-8")).hexdigest()
        if json_admin_plano else ""
    )

    # 5. Hash maestro (64 hex, uso interno para el Aura)
    hash_maestro = hashlib.sha256(
        (hash_publica + hash_medica + hash_admin).encode("utf-8")
    ).hexdigest()

    # 6. Aura usando el hash maestro COMPLETO
    aura = generar_aura(hash_maestro, AURA_SIZE)

    # 7. Construir payload v2.4.0 con firma Ed25519
    sha_payload = hash_maestro[:SHA_PAYLOAD_HEX]
    mensaje_a_firmar = (
        f"PUB:{json_publica}"
        f"|MED:{json_medica}"
        f"|ADM:{json_admin}"
        f"|SHA:{sha_payload}"
    )
    bloque_sig = firmar_payload(mensaje_a_firmar, priv_key)
    contenido_dm = mensaje_a_firmar + bloque_sig

    data_matrix = generar_data_matrix(contenido_dm, DM_SIZE)

    # 8. Componer imagen final
    imagen_final = componer_imagen(
        aura=aura,
        data_matrix=data_matrix,
        hash_publico=hash_publica,
        id_escenario=id_escenario,
        sector=sector,
    )

    # 9. Guardar
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ruta_salida = OUTPUT_DIR / f"aura_{id_escenario}.png"
    imagen_final.save(ruta_salida, "PNG", optimize=True)

    return ruta_salida


# =====================================================================
# FUNCION PRINCIPAL
# =====================================================================

def main() -> None:
    print("=" * 60)
    print("  AuraHash ID - Generador Universal v2.4.0")
    print("  (AES-256-GCM + zlib + PUB minif + SHA32 + Ed25519)")
    print("=" * 60)
    print()

    if not DATA_FILE.exists():
        print(f"[ERROR] No se encontro el archivo: {DATA_FILE}")
        return

    try:
        cargar_clave_aes()
        print(f"[INFO] Clave AES cargada: {KEY_FILE.name} ({AES_KEY_BYTES} bytes)")
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] Problema con la clave AES:\n{e}")
        return

    priv_key = None
    try:
        priv_key = cargar_llave_ed25519_privada()
        if priv_key is not None:
            print(f"[INFO] Llave Ed25519 privada cargada: {ED25519_PRIV_FILE.name}")
        else:
            print("[AVISO] No hay llave Ed25519 privada. Payload se generara SIN firma.")
            print(f"        Generala con: python src/keys_manager.py")
    except ValueError as e:
        print(f"[ERROR] Problema con la llave Ed25519:\n{e}")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        datos = json.load(f)

    escenarios = datos.get("escenarios", [])
    if not escenarios:
        print("[ERROR] El archivo JSON no contiene la clave 'escenarios'.")
        return

    print(f"[INFO] Escenarios encontrados: {len(escenarios)}")
    print()

    resultados = []
    for i, escenario in enumerate(escenarios, start=1):
        print(f"[{i}/{len(escenarios)}] Procesando: {escenario['id']} ({escenario['sector']})")
        try:
            ruta = procesar_escenario(escenario, priv_key)
            resultados.append((escenario["id"], ruta))
            print(f"        OK Generado: {ruta.name}")
        except Exception as e:
            print(f"        ERROR: {e}")

    print()
    print("=" * 60)
    print(f"  Generacion completada: {len(resultados)}/{len(escenarios)} imagenes")
    print("=" * 60)
    for id_esc, ruta in resultados:
        print(f"  * {id_esc:<30} -> {ruta.name}")


if __name__ == "__main__":
    main()