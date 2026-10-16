"""
AuraHash ID - Barrido de opacidades 7x6
========================================

Genera 42 imagenes: 7 escenarios x 6 opacidades (0, 1, 2, 3, 4, 5).

Objetivo: encontrar la opacidad del Aura que haga que los 7 escenarios
sean legibles por zxing-js en la PWA.

Salida: pwa/batch/b7_<id_escenario>_op<NN>.png

Uso:
    cd C:\\Users\\erasn\\Proyectos\\AuraHash-ID
    python pwa\\test_barrido_7x7.py
"""

import json
import hashlib
import base64
import zlib
import io
import sys
from pathlib import Path

import numpy as np
import segno
from PIL import Image, ImageDraw, ImageFont
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


# =====================================================================
# RUTAS (robustas, basadas en la ubicacion de este archivo)
# =====================================================================

BASE = Path(__file__).resolve().parent.parent  # raiz del proyecto
DATA_FILE = BASE / "data" / "example_data.json"
KEY_FILE = BASE / "keys" / "aes.key"
PRIV_FILE = BASE / "keys" / "ed25519_private.key"
OUT_DIR = BASE / "pwa" / "batch"


# =====================================================================
# CONSTANTES (copia fiel de generator.py v3.0.1)
# =====================================================================

IMG_W = 1200
IMG_H = 1400
DM_SIZE = 800
QUIET_ZONE = 40

AURA_PALETTE = [
    (0, 200, 255),
    (255, 0, 180),
    (120, 0, 255),
    (0, 255, 150),
    (255, 180, 0),
]

MAPA_CLAVES_PUB = {
    "perfil": "p",
    "tipo": "t",
    "instruccion": "i",
    "nombre_pila": "n",
    "alergias_criticas": "a",
    "id_visual": "v",
    "evento": "e",
}

OPACIDADES_PCT = [0, 1, 2, 3, 4, 5]


# =====================================================================
# UTILIDADES
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


def serializar(capa) -> str:
    if capa is None:
        return ""
    return json.dumps(capa, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def minificar(capa: dict) -> dict:
    if not isinstance(capa, dict):
        return capa
    return {MAPA_CLAVES_PUB.get(k, k): v for k, v in capa.items()}


# =====================================================================
# CIFRADO (nonce determinista, identico a generator v3.0.1)
# =====================================================================

def cargar_clave_aes() -> bytes:
    clave = KEY_FILE.read_bytes()
    if len(clave) != 32:
        raise ValueError(f"aes.key debe tener 32 bytes, tiene {len(clave)}")
    return clave


def cifrar_capa(texto: str, id_escenario: str, aes_key: bytes) -> str:
    if not texto:
        return ""
    plano = texto.encode("utf-8")
    comprimido = zlib.compress(plano, level=9)
    nonce = hashlib.sha256(
        (id_escenario + '::').encode('utf-8') + comprimido
    ).digest()[:12]
    aesgcm = AESGCM(aes_key)
    ct = aesgcm.encrypt(nonce, comprimido, None)
    return "AES256GCMZ:" + base64.b64encode(nonce + ct).decode("ascii")


# =====================================================================
# GENERACION DE UN ESCENARIO A UNA OPACIDAD DADA
# =====================================================================

def generar_variante(
    escenario: dict,
    opacidad_pct: int,
    aes_key: bytes,
    priv_key,
    ruta_salida: Path,
) -> None:
    id_esc = escenario["id"]
    sector = escenario.get("sector", "general")

    capa_pub = escenario.get("capa_publica")
    capa_med = escenario.get("capa_medica")
    capa_adm = escenario.get("capa_administrativa")

    pub_min = minificar(capa_pub) if capa_pub else None
    json_pub = serializar(pub_min)
    json_med_plano = serializar(capa_med)
    json_adm_plano = serializar(capa_adm)

    json_med = cifrar_capa(json_med_plano, id_esc, aes_key)
    json_adm = cifrar_capa(json_adm_plano, id_esc, aes_key)

    h_pub = hashlib.sha256(json_pub.encode("utf-8")).hexdigest()
    h_med = hashlib.sha256(json_med_plano.encode("utf-8")).hexdigest() if json_med_plano else ""
    h_adm = hashlib.sha256(json_adm_plano.encode("utf-8")).hexdigest() if json_adm_plano else ""
    h_maestro = hashlib.sha256((h_pub + h_med + h_adm).encode("utf-8")).hexdigest()

    sha32 = h_maestro[:32]
    mensaje = (
        f"PUB:{json_pub}"
        f"|MED:{json_med}"
        f"|ADM:{json_adm}"
        f"|SHA:{sha32}"
    )
    firma_bytes = priv_key.sign(mensaje.encode("utf-8"))
    firma_b64 = base64.b64encode(firma_bytes).decode("ascii")
    payload = mensaje + "|SIG:" + firma_b64

    qr = segno.make(payload, micro=False)
    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=20, border=4, dark="black", light="white")
    buf.seek(0)
    dm_img = Image.open(buf).convert("RGB").resize((DM_SIZE, DM_SIZE), Image.LANCZOS)

    opacidad = opacidad_pct / 100.0

    if opacidad == 0.0:
        fondo = Image.new("RGB", (IMG_W, IMG_H), (255, 255, 255))
    else:
        semilla = int(h_maestro[:16], 16)
        rng = np.random.default_rng(semilla)
        ruido = rng.random((IMG_H, IMG_W))
        color_base = AURA_PALETTE[semilla % len(AURA_PALETTE)]
        color = np.array(color_base, dtype=float)
        fondo_oscuro = np.array((10, 10, 20), dtype=float)
        factor = ruido[..., np.newaxis] ** 2.5
        aura_full = fondo_oscuro + (color - fondo_oscuro) * factor
        mezclada = (
            np.array((255, 255, 255), dtype=float) * (1 - opacidad)
            + aura_full * opacidad
        )
        matriz = np.clip(mezclada, 0, 255).astype(np.uint8)
        fondo = Image.fromarray(matriz, mode="RGB")

    lienzo = fondo.copy()
    draw = ImageDraw.Draw(lienzo)

    dm_total = DM_SIZE + 2 * QUIET_ZONE
    dm_x = (IMG_W - dm_total) // 2
    dm_y = 60

    draw.rectangle(
        [(dm_x, dm_y), (dm_x + dm_total, dm_y + dm_total)],
        fill=(255, 255, 255),
    )
    lienzo.paste(dm_img, (dm_x + QUIET_ZONE, dm_y + QUIET_ZONE))

    y = dm_y + dm_total + 30
    etiquetas = [
        ("AuraHash ID", 36),
        (f"[{sector.upper()}]", 22),
        (f"ID: {id_esc}", 20),
        (f"opacidad: {opacidad_pct}%", 20),
    ]
    for texto, tam in etiquetas:
        f = obtener_fuente(tam)
        bbox = draw.textbbox((0, 0), texto, font=f)
        ancho = bbox[2] - bbox[0]
        draw.text(((IMG_W - ancho) // 2, y), texto, fill=(30, 30, 30), font=f)
        y += tam + 15

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    lienzo.save(ruta_salida, "PNG", optimize=True)


# =====================================================================
# MAIN
# =====================================================================

def main() -> None:
    print("=" * 60)
    print("  AuraHash ID - Barrido de opacidades 7x6")
    print(f"  Opacidades: {OPACIDADES_PCT}")
    print(f"  Salida: {OUT_DIR}")
    print("=" * 60)

    if not DATA_FILE.exists():
        print(f"[ERROR] No existe: {DATA_FILE}")
        sys.exit(1)
    if not KEY_FILE.exists():
        print(f"[ERROR] No existe: {KEY_FILE}")
        sys.exit(1)
    if not PRIV_FILE.exists():
        print(f"[ERROR] No existe: {PRIV_FILE}")
        sys.exit(1)

    aes_key = cargar_clave_aes()
    priv_key = Ed25519PrivateKey.from_private_bytes(PRIV_FILE.read_bytes())

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        datos = json.load(f)

    escenarios = datos.get("escenarios", [])
    if not escenarios:
        print("[ERROR] El JSON no contiene 'escenarios'.")
        sys.exit(1)

    total = len(escenarios) * len(OPACIDADES_PCT)
    print(f"[INFO] Escenarios: {len(escenarios)} | Opacidades: {len(OPACIDADES_PCT)} | Total: {total}")
    print()

    contador = 0
    for esc in escenarios:
        id_esc = esc["id"]
        for pct in OPACIDADES_PCT:
            contador += 1
            nombre = f"b7_{id_esc}_op{pct:02d}.png"
            ruta = OUT_DIR / nombre
            try:
                generar_variante(esc, pct, aes_key, priv_key, ruta)
                print(f"  [{contador:02d}/{total}] OK {nombre}")
            except Exception as e:
                print(f"  [{contador:02d}/{total}] ERROR {nombre}: {e}")

    print()
    print("=" * 60)
    print(f"  Listo. {contador} imagenes en {OUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()