"""
AuraHash ID — Generador Universal v2.0.0
==========================================

Este script lee un archivo JSON con escenarios organizados en 3 capas:
  - capa_publica:         Visible con Google Lens. Cero datos sensibles.
  - capa_medica:          Datos de salud (cifrado en producción).
  - capa_administrativa:  Datos legales/financieros (cifrado en producción).

Para cada escenario genera una imagen AuraHash con:
  - Un código Data Matrix real (ISO/IEC 16022), escaneable por Google Lens.
  - Un "Aura Estocástica" (patrón de ruido determinista) alrededor.
  - Los hashes SHA-256 de cada capa visibles/embebidos para verificación.

Uso:
    python src/generator.py

Entrada:
    data/example_data.json

Salida:
    output/aura_<id_escenario>.png
"""

import json
import hashlib
import io
from pathlib import Path

import numpy as np
import segno
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# =====================================================================
# CONFIGURACIÓN GLOBAL
# =====================================================================

# Rutas del proyecto (relativas a la raíz del repo)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "example_data.json"
OUTPUT_DIR = BASE_DIR / "output"

# --- Dimensiones de la imagen final (en píxeles) ---
IMG_WIDTH = 800
IMG_HEIGHT = 800

# Tamaño del "Aura" (marco de ruido que rodea al Data Matrix)
AURA_SIZE = 600

# Tamaño del Data Matrix dentro del Aura (con margen blanco)
DM_SIZE = 360
DM_QUIET_ZONE = 4        # Módulos de silencio (mínimo 4 por el estándar)

# --- Colores (formato RGB) ---
COLOR_BG = (255, 255, 255)      # Fondo blanco
COLOR_DM = (0, 0, 0)            # Data Matrix negro puro (alto contraste)
COLOR_AURA_BG = (10, 10, 20)    # Fondo oscuro del aura
COLOR_TEXT = (30, 30, 30)       # Texto principal
COLOR_TEXT_HASH = (80, 80, 80)  # Texto secundario (hash)

# Paleta de colores para el Aura (se elige según el hash del payload)
AURA_PALETTE = [
    (0, 200, 255),     # Cian eléctrico
    (255, 0, 180),     # Magenta neón
    (120, 0, 255),     # Púrpura profundo
    (0, 255, 150),     # Verde menta
    (255, 180, 0),     # Ámbar dorado
]

# =====================================================================
# FUNCIÓN: Generar el Aura Estocástica
# =====================================================================

def generar_aura(hash_hex: str, tamaño: int) -> Image.Image:
    """
    Genera el patrón de ruido determinista (Aura) a partir de un hash SHA-256.

    El mismo hash SIEMPRE produce el mismo patrón (determinismo).
    Un cambio de un solo bit en el hash produce un patrón COMPLETAMENTE
    distinto (Efecto Avalancha).
    """
    # 1. Convertir el hash hexadecimal en una semilla numérica estable
    semilla = int(hash_hex[:16], 16)

    # 2. Inicializar el generador pseudoaleatorio de NumPy con la semilla
    rng = np.random.default_rng(semilla)

    # 3. Generar dos matrices de ruido
    ruido_brillo = rng.random((tamaño, tamaño))
    ruido_color = rng.random((tamaño, tamaño))

    # 4. Elegir color base de la paleta según el hash
    indice_color = semilla % len(AURA_PALETTE)
    color_base = AURA_PALETTE[indice_color]

    # 5. Construir la matriz RGB
    fondo = np.array(COLOR_AURA_BG, dtype=float)
    color = np.array(color_base, dtype=float)

    factor = ruido_brillo[..., np.newaxis] ** 2
    matriz_rgb = fondo + (color - fondo) * factor

    # 6. Variación de color secundaria
    indice_color2 = (semilla // 7) % len(AURA_PALETTE)
    color_secundario = np.array(AURA_PALETTE[indice_color2], dtype=float)
    mascara_secundaria = (ruido_color > 0.75)[..., np.newaxis]
    matriz_rgb = np.where(
        mascara_secundaria,
        matriz_rgb * 0.5 + color_secundario * 0.5,
        matriz_rgb
    )

    # 7. Rango válido [0, 255]
    matriz_rgb = np.clip(matriz_rgb, 0, 255).astype(np.uint8)

    # 8. Imagen PIL
    aura_img = Image.fromarray(matriz_rgb, mode="RGB")

    # 9. Máscara circular con desenfoque
    mascara = Image.new("L", (tamaño, tamaño), 0)
    draw_mask = ImageDraw.Draw(mascara)
    radio = int(tamaño * 0.48)
    centro = tamaño // 2
    draw_mask.ellipse(
        (centro - radio, centro - radio, centro + radio, centro + radio),
        fill=255
    )
    mascara = mascara.filter(ImageFilter.GaussianBlur(radius=tamaño // 30))

    # 10. Componer sobre fondo blanco
    fondo_blanco = Image.new("RGB", (tamaño, tamaño), COLOR_BG)
    aura_final = Image.composite(aura_img, fondo_blanco, mascara)

    return aura_final


# =====================================================================
# FUNCIÓN: Generar el Data Matrix
# =====================================================================

def generar_data_matrix(texto: str, tamaño: int) -> Image.Image:
    """
    Genera un Data Matrix real (ISO/IEC 16022) a partir de un texto.
    """
    # 1. Generar con segno (micro=False asegura Data Matrix estándar)
    qr = segno.make(texto, micro=False)

    # 2. Guardar en memoria como PNG
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

    # 3. Abrir con Pillow y redimensionar
    dm_img = Image.open(buffer).convert("RGB")
    dm_img = dm_img.resize((tamaño, tamaño), Image.LANCZOS)

    return dm_img


# =====================================================================
# FUNCIÓN: Cargar fuente para el texto
# =====================================================================

def obtener_fuente(tamaño: int) -> ImageFont.ImageFont:
    """
    Intenta cargar una fuente monoespaciada del sistema.
    """
    candidatas = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    for ruta in candidatas:
        try:
            return ImageFont.truetype(ruta, tamaño)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()

# =====================================================================
# FUNCIÓN: Componer la imagen final
# =====================================================================

def componer_imagen(
    aura: Image.Image,
    data_matrix: Image.Image,
    hash_publico: str,
    id_escenario: str,
    sector: str,
) -> Image.Image:
    """
    Compone la imagen final: fondo blanco + aura + data matrix + texto.

    Ahora muestra el hash de la CAPA PÚBLICA (no de todo el payload)
    para reforzar el concepto de separación de capas.
    """
    # 1. Lienzo base blanco
    lienzo = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), COLOR_BG)
    draw = ImageDraw.Draw(lienzo)

    # 2. Pegar el Aura centrada
    aura_x = (IMG_WIDTH - AURA_SIZE) // 2
    aura_y = (IMG_HEIGHT - AURA_SIZE) // 2
    lienzo.paste(aura, (aura_x, aura_y))

    # 3. Pegar el Data Matrix centrado
    dm_x = (IMG_WIDTH - DM_SIZE) // 2
    dm_y = (IMG_HEIGHT - DM_SIZE) // 2
    lienzo.paste(data_matrix, (dm_x, dm_y))

    # 4. Título superior
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

    # 5. Sector (arriba a la derecha)
    fuente_sector = obtener_fuente(18)
    texto_sector = f"[{sector.upper()}]"
    draw.text((IMG_WIDTH - 160, 40), texto_sector, fill=COLOR_TEXT, font=fuente_sector)

    # 6. Hash de la capa pública (formato agrupado)
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

    # 7. ID del escenario
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

    # 8. Instrucción de escaneo
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
# FUNCIÓN: Serializar una capa a JSON canónico
# =====================================================================

def serializar_capa(capa) -> str:
    """
    Serializa una capa del payload a JSON canónico.
    Si la capa es None, devuelve cadena vacía.
    """
    if capa is None:
        return ""
    return json.dumps(capa, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


# =====================================================================
# FUNCIÓN: Procesar un escenario individual (v2.0.0 - 3 capas)
# =====================================================================

def procesar_escenario(escenario: dict) -> Path:
    """
    Procesa un único escenario del JSON (con 3 capas) y devuelve la ruta PNG.
    """
    # 1. Extraer datos
    id_escenario = escenario["id"]
    sector = escenario.get("sector", "general")
    capa_publica = escenario.get("capa_publica")
    capa_medica = escenario.get("capa_medica")
    capa_administrativa = escenario.get("capa_administrativa")

    # 2. Serializar cada capa a JSON canónico
    json_publica = serializar_capa(capa_publica)
    json_medica = serializar_capa(capa_medica)
    json_admin = serializar_capa(capa_administrativa)

    # 3. Calcular hash SHA-256 de cada capa
    hash_publica = hashlib.sha256(json_publica.encode("utf-8")).hexdigest()
    hash_medica = hashlib.sha256(json_medica.encode("utf-8")).hexdigest() if json_medica else ""
    hash_admin = hashlib.sha256(json_admin.encode("utf-8")).hexdigest() if json_admin else ""

    # 4. El hash "maestro" del escenario = hash de la concatenación de los 3 hashes
    hash_maestro = hashlib.sha256(
        (hash_publica + hash_medica + hash_admin).encode("utf-8")
    ).hexdigest()

    # 5. Generar el Aura usando el hash maestro (determinista)
    aura = generar_aura(hash_maestro, AURA_SIZE)

    # 6. Contenido del Data Matrix: las 3 capas separadas por marcadores
    #    En producción, las capas médica y admin irían cifradas aquí.
    contenido_dm = (
        f"PUB:{json_publica}"
        f"|MED:{json_medica}"
        f"|ADM:{json_admin}"
        f"|SHA:{hash_maestro[:16]}"
    )
    data_matrix = generar_data_matrix(contenido_dm, DM_SIZE)

    # 7. Componer imagen final
    imagen_final = componer_imagen(
        aura=aura,
        data_matrix=data_matrix,
        hash_publico=hash_publica,
        id_escenario=id_escenario,
        sector=sector,
    )

    # 8. Guardar
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ruta_salida = OUTPUT_DIR / f"aura_{id_escenario}.png"
    imagen_final.save(ruta_salida, "PNG", optimize=True)

    return ruta_salida


# =====================================================================
# FUNCIÓN PRINCIPAL
# =====================================================================

def main() -> None:
    """
    Orquestador principal.
    """
    print("=" * 60)
    print("  AuraHash ID — Generador Universal v2.0.0")
    print("=" * 60)
    print()

    # 1. Verificar archivo de datos
    if not DATA_FILE.exists():
        print(f"[ERROR] No se encontró el archivo: {DATA_FILE}")
        return

    # 2. Leer JSON
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        datos = json.load(f)

    escenarios = datos.get("escenarios", [])
    if not escenarios:
        print("[ERROR] El archivo JSON no contiene la clave 'escenarios'.")
        return

    print(f"[INFO] Escenarios encontrados: {len(escenarios)}")
    print(f"[INFO] Salida: {OUTPUT_DIR}")
    print()

    # 3. Procesar cada escenario
    resultados = []
    for i, escenario in enumerate(escenarios, start=1):
        print(f"[{i}/{len(escenarios)}] Procesando: {escenario['id']} ({escenario['sector']})")
        try:
            ruta = procesar_escenario(escenario)
            resultados.append((escenario["id"], ruta))
            print(f"        OK Generado: {ruta.name}")
        except Exception as e:
            print(f"        ERROR: {e}")

    # 4. Resumen final
    print()
    print("=" * 60)
    print(f"  Generacion completada: {len(resultados)}/{len(escenarios)} imagenes")
    print("=" * 60)
    for id_esc, ruta in resultados:
        print(f"  * {id_esc:<30} -> {ruta.name}")


# =====================================================================
# PUNTO DE ENTRADA
# =====================================================================

if __name__ == "__main__":
    main()