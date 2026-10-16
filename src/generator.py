"""
AuraHash ID - Generador Universal v3.0.0
==========================================

Cambios v3.0.0 (rediseno mayor):
  - Aura DECORATIVA de fondo, opacidad al 15%.
    Descubrimiento: el Aura alrededor del Data Matrix impedia que
    zxing-js (PWA) lo leyera. Con opacidad al 15%, zxing-js lee
    el payload completo (~789 chars).
  - Data Matrix con zona de silencio blanca amplia (QUIET_ZONE=40px).
  - Payload COMPLETO siempre (PUB + MED + ADM + SHA + SIG).
    zxing-js lee hasta ~1500 chars en Data Matrix limpio. Cabe de sobra.
  - Eliminado el modo --demo.
  - Una sola imagen por escenario: aura_<id>.png

Arquitectura de la imagen:
  - Fondo: Aura estocastica al 15% de opacidad (ruido determinista).
  - Centro: Data Matrix limpio con zona blanca alrededor.
  - Debajo: texto informativo (ID, sector, hash, instruccion).

Uso:
    python src/generator.py
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
from PIL import Image, ImageDraw, ImageFont
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
PREFIJO_CIFRADO_ZLIB = "AES256GCMZ:"

# Longitud del SHA maestro embebido en el payload (32 hex = 128 bits)
SHA_PAYLOAD_HEX = 32

# --- Dimensiones de la imagen final ---
IMG_WIDTH = 1200
IMG_HEIGHT = 1400
DM_SIZE = 800
DM_QUIET_ZONE_PX = 40

# --- Opacidad del Aura de fondo ---
# Validado: 15% es el maximo que zxing-js tolera sin perder legibilidad.
# 18% falla. 15% funciona con margen de seguridad.
AURA_OPACIDAD = 0.10

# --- Colores ---
COLOR_BG = (255, 255, 255)
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
    "perfil": "p",
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
    if not KEY_FILE.exists():
        raise FileNotFoundError(f"No se encontro la clave AES en: {KEY_FILE}")
    clave = KEY_FILE.read_bytes()
    if len(clave) != AES_KEY_BYTES:
        raise ValueError(
            f"La clave AES debe tener {AES_KEY_BYTES} bytes, tiene {len(clave)}."
        )
    return clave


def cifrar_capa(texto: str) -> str:
    if not texto:
        return ""
    clave = cargar_clave_aes()
    aesgcm = AESGCM(clave)
    plano_comprimido = zlib.compress(texto.encode("utf-8"), level=9)
    nonce = secrets.token_bytes(GCM_NONCE_BYTES)
    ciphertext_con_tag = aesgcm.encrypt(nonce, plano_comprimido, None)
    paquete = nonce + ciphertext_con_tag
    b64 = base64.b64encode(paquete).decode("ascii")
    return PREFIJO_CIFRADO_ZLIB + b64


# =====================================================================
# FIRMA DIGITAL ED25519
# =====================================================================

def cargar_llave_ed25519_privada():
    if not ED25519_PRIV_FILE.exists():
        return None
    priv_bytes = ED25519_PRIV_FILE.read_bytes()
    if len(priv_bytes) != 32:
        raise ValueError(
            f"La llave privada Ed25519 debe tener 32 bytes, tiene {len(priv_bytes)}."
        )
    return Ed25519PrivateKey.from_private_bytes(priv_bytes)


def firmar_payload(mensaje: str, priv_key) -> str:
    if priv_key is None:
        return ""
    firma_bytes = priv_key.sign(mensaje.encode("utf-8"))
    b64 = base64.b64encode(firma_bytes).decode("ascii")
    return f"|SIG:{b64}"


# =====================================================================
# MINIFICACION DE LA CAPA PUBLICA
# =====================================================================

def minificar_capa_publica(capa: dict) -> dict:
    if not isinstance(capa, dict):
        return capa
    return {MAPA_CLAVES_PUB.get(k, k): v for k, v in capa.items()}


# =====================================================================
# AURA ESTOCASTICA (DECORATIVA - FONDO AL 15%)
# =====================================================================

def generar_aura_fondo(hash_hex: str, ancho: int, alto: int) -> Image.Image:
    """
    Genera el Aura decorativa de fondo al 15% de opacidad.
    El ruido es determinista (SHA-256) pero la opacidad lo hace
    lo suficientemente sutil como para no interferir con zxing-js.
    """
    semilla = int(hash_hex[:16], 16)
    rng = np.random.default_rng(semilla)

    ruido_brillo = rng.random((alto, ancho))

    indice_color = semilla % len(AURA_PALETTE)
    color_base = AURA_PALETTE[indice_color]

    fondo_oscuro = np.array((10, 10, 20), dtype=float)
    color = np.array(color_base, dtype=float)

    factor = ruido_brillo[..., np.newaxis] ** 2.5
    aura_full = fondo_oscuro + (color - fondo_oscuro) * factor

    # Mezclar con blanco segun AURA_OPACIDAD (15%)
    aura_mezclada = (
        np.array((255, 255, 255), dtype=float) * (1 - AURA_OPACIDAD)
        + aura_full * AURA_OPACIDAD
    )
    matriz_rgb = np.clip(aura_mezclada, 0, 255).astype(np.uint8)

    return Image.fromarray(matriz_rgb, mode="RGB")


# =====================================================================
# DATA MATRIX
# =====================================================================

def generar_data_matrix(texto: str, tamano: int) -> Image.Image:
    qr = segno.make(texto, micro=False)
    buffer = io.BytesIO()
    qr.save(
        buffer,
        kind="png",
        scale=20,
        border=4,
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
    aura_fondo: Image.Image,
    data_matrix: Image.Image,
    hash_publico: str,
    id_escenario: str,
    sector: str,
) -> Image.Image:
    lienzo = aura_fondo.copy()
    draw = ImageDraw.Draw(lienzo)

    # Cuadrado blanco detras del Data Matrix (zona de silencio)
    dm_total = DM_SIZE + 2 * DM_QUIET_ZONE_PX
    dm_x = (IMG_WIDTH - dm_total) // 2
    dm_y = 60

    draw.rectangle(
        [(dm_x, dm_y), (dm_x + dm_total, dm_y + dm_total)],
        fill=COLOR_BG,
    )

    # Pegar el Data Matrix
    lienzo.paste(data_matrix, (dm_x + DM_QUIET_ZONE_PX, dm_y + DM_QUIET_ZONE_PX))

    # --- Texto debajo ---
    texto_y = dm_y + dm_total + 30

    fuente_titulo = obtener_fuente(36)
    texto_titulo = "AuraHash ID"
    bbox = draw.textbbox((0, 0), texto_titulo, font=fuente_titulo)
    ancho_titulo = bbox[2] - bbox[0]
    draw.text(
        ((IMG_WIDTH - ancho_titulo) // 2, texto_y),
        texto_titulo,
        fill=COLOR_TEXT,
        font=fuente_titulo,
    )
    texto_y += 55

    fuente_sector = obtener_fuente(22)
    texto_sector = f"[{sector.upper()}]"
    bbox = draw.textbbox((0, 0), texto_sector, font=fuente_sector)
    ancho_sector = bbox[2] - bbox[0]
    draw.text(
        ((IMG_WIDTH - ancho_sector) // 2, texto_y),
        texto_sector,
        fill=COLOR_TEXT,
        font=fuente_sector,
    )
    texto_y += 40

    fuente_id = obtener_fuente(20)
    texto_id = f"ID: {id_escenario}"
    bbox = draw.textbbox((0, 0), texto_id, font=fuente_id)
    ancho_id = bbox[2] - bbox[0]
    draw.text(
        ((IMG_WIDTH - ancho_id) // 2, texto_y),
        texto_id,
        fill=COLOR_TEXT_HASH,
        font=fuente_id,
    )
    texto_y += 35

    fuente_hash = obtener_fuente(18)
    hash_truncado = hash_publico[:32].upper()
    hash_formateado = " ".join(
        hash_truncado[i:i + 4] for i in range(0, len(hash_truncado), 4)
    )
    bbox = draw.textbbox((0, 0), hash_formateado, font=fuente_hash)
    ancho_hash = bbox[2] - bbox[0]
    draw.text(
        ((IMG_WIDTH - ancho_hash) // 2, texto_y),
        hash_formateado,
        fill=COLOR_TEXT_HASH,
        font=fuente_hash,
    )
    texto_y += 30

    fuente_instr = obtener_fuente(16)
    texto_instr = "Escanee con Google Lens / WeChat / AuraHash PWA"
    bbox = draw.textbbox((0, 0), texto_instr, font=fuente_instr)
    ancho_instr = bbox[2] - bbox[0]
    draw.text(
        ((IMG_WIDTH - ancho_instr) // 2, texto_y),
        texto_instr,
        fill=COLOR_TEXT,
        font=fuente_instr,
    )

    return lienzo


# =====================================================================
# SERIALIZACION CANONICA
# =====================================================================

def serializar_capa(capa) -> str:
    if capa is None:
        return ""
    return json.dumps(capa, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


# =====================================================================
# PROCESAR UN ESCENARIO
# =====================================================================

def procesar_escenario(escenario: dict, priv_key) -> Path:
    """
    Procesa un escenario. Siempre genera el payload COMPLETO
    (PUB + MED + ADM + SHA + SIG) para el Data Matrix.
    """
    id_escenario = escenario["id"]
    sector = escenario.get("sector", "general")
    capa_publica = escenario.get("capa_publica")
    capa_medica = escenario.get("capa_medica")
    capa_administrativa = escenario.get("capa_administrativa")

    # 1. Minificar la capa publica
    capa_publica_min = minificar_capa_publica(capa_publica) if capa_publica else None
    json_publica = serializar_capa(capa_publica_min)

    # 2. Serializar capas sensibles en claro
    json_medica_plano = serializar_capa(capa_medica)
    json_admin_plano = serializar_capa(capa_administrativa)

    # 3. Cifrar capas sensibles
    json_medica = cifrar_capa(json_medica_plano)
    json_admin = cifrar_capa(json_admin_plano)

    # 4. Hashes
    hash_publica = hashlib.sha256(json_publica.encode("utf-8")).hexdigest()
    hash_medica = (
        hashlib.sha256(json_medica_plano.encode("utf-8")).hexdigest()
        if json_medica_plano else ""
    )
    hash_admin = (
        hashlib.sha256(json_admin_plano.encode("utf-8")).hexdigest()
        if json_admin_plano else ""
    )

    # 5. Hash maestro
    hash_maestro = hashlib.sha256(
        (hash_publica + hash_medica + hash_admin).encode("utf-8")
    ).hexdigest()

    # 6. Aura de fondo (decorativa, 15% opacidad)
    aura_fondo = generar_aura_fondo(hash_maestro, IMG_WIDTH, IMG_HEIGHT)

    # 7. Payload completo con firma
    sha_payload = hash_maestro[:SHA_PAYLOAD_HEX]
    mensaje_a_firmar = (
        f"PUB:{json_publica}"
        f"|MED:{json_medica}"
        f"|ADM:{json_admin}"
        f"|SHA:{sha_payload}"
    )
    bloque_sig = firmar_payload(mensaje_a_firmar, priv_key)
    contenido_dm = mensaje_a_firmar + bloque_sig
    print(f"        DEBUG payload ({len(contenido_dm)} chars): {contenido_dm[:100]}...")

    # 8. Data Matrix
    data_matrix = generar_data_matrix(contenido_dm, DM_SIZE)

    # 9. Componer imagen
    imagen_final = componer_imagen(
        aura_fondo=aura_fondo,
        data_matrix=data_matrix,
        hash_publico=hash_publica,
        id_escenario=id_escenario,
        sector=sector,
    )

    # 10. Guardar
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ruta_salida = OUTPUT_DIR / f"aura_{id_escenario}.png"
    imagen_final.save(ruta_salida, "PNG", optimize=True)

    return ruta_salida


# =====================================================================
# FUNCION PRINCIPAL
# =====================================================================

def main() -> None:
    print("=" * 60)
    print("  AuraHash ID - Generador Universal v3.0.0")
    print(f"  (Payload completo + Aura {int(AURA_OPACIDAD*100)}% opacidad)")
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
        perfil = "?"
        capa_pub = escenario.get("capa_publica") or {}
        if isinstance(capa_pub, dict):
            perfil = capa_pub.get("perfil", "?")
        print(f"[{i}/{len(escenarios)}] Procesando: {escenario['id']} ({escenario['sector']}) [perfil: {perfil}]")
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