"""
AuraHash ID - Creador de pulsera de contacto.
Guía al usuario paso a paso para crear un AuraHash ID personalizado.
Genera un JSON temporal, ejecuta generator.py con ese JSON, y produce la imagen.

Uso:
    python src/crear_contacto.py
"""

import json
import subprocess
import sys
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "example_data.json"
TEMP_JSON = BASE_DIR / "data" / "contacto_personalizado.json"
OUTPUT_DIR = BASE_DIR / "output"


def preguntar(pregunta, default=""):
    """Pregunta al usuario y devuelve la respuesta. Si está vacía, usa el default."""
    if default:
        respuesta = input(f"{pregunta} [{default}]: ").strip()
        return respuesta if respuesta else default
    return input(f"{pregunta}: ").strip()


def elegir_tipo():
    """Pregunta al usuario para quién es el AuraHash ID."""
    print("\n--- ¿Para quién es? ---")
    print("1. Niño")
    print("2. Mascota")
    print("3. Adulto mayor")
    print("4. Otro")
    opcion = preguntar("Elige (1-4)", "1")
    if opcion == "1":
        return "niño", "CONTACTO_FAMILIAR", "Hola, me llamo {nombre} y me perdí. Por favor llama a mi familia."
    elif opcion == "2":
        return "mascota", "CONTACTO_MASCOTA", "Soy una mascota. Si me encuentras, contacta a mi dueño."
    elif opcion == "3":
        return "adulto mayor", "CONTACTO_FAMILIAR", "Soy adulto mayor. Si me encuentras, contacta a mi familia."
    else:
        return "otro", "CONTACTO_FAMILIAR", "Hola, si me encuentras, por favor contacta a mi familia."


def main():
    print("=" * 60)
    print("  AuraHash ID - Creador de pulsera de contacto")
    print("=" * 60)
    print()
    print("Este script te guía para crear un AuraHash ID personalizado.")
    print("Responde las preguntas. Pulsa Enter para usar el valor por defecto.")
    print()

    # Elegir tipo
    tipo, tipo_contacto, instruccion_default = elegir_tipo()

    # Datos del titular
    print(f"\n--- Datos del titular ({tipo}) ---")
    nombre = preguntar("Nombre de pila", "Diego")
    instruccion = preguntar(
        "Instrucción de emergencia",
        instruccion_default.format(nombre=nombre)
    )
    evento = preguntar(
        "Descripción adicional (edad, condición, etc.)",
        "Tengo 7 años. Me gustan los dinosaurios."
    )
    id_visual = preguntar("ID visual (opcional)", f"{tipo.upper().replace(' ', '-')}-2026-001")

    # Datos del tutor
    print("\n--- Datos del tutor/contacto ---")
    tutor_nombre = preguntar("Nombre del tutor/contacto", "Maria Lopez")
    tutor_parentesco = preguntar("Parentesco", "Madre" if tipo == "niño" else ("Dueño" if tipo == "mascota" else "Familiar"))
    tutor_telefono = preguntar("Teléfono principal", "+52-55-9876-5432")
    tutor_telefono_alt = preguntar("Teléfono alternativo (opcional)", "")
    notas = preguntar("Notas adicionales (opcional)", "")

    # Generar el JSON temporal
    print("\n--- Generando AuraHash ID ---")

    escenario = {
        "id": f"contacto_{tipo.replace('ñ', 'n').replace(' ', '_')}_personalizado",
        "sector": "personal",
        "descripcion": f"Pulsera de contacto para {tipo}",
        "capa_publica": {
            "perfil": "contacto",
            "tipo": tipo_contacto,
            "instruccion": instruccion,
            "nombre_pila": nombre,
            "evento": evento,
            "id_visual": id_visual
        },
        "capa_medica": None,
        "capa_administrativa": {
            "tutor_nombre": tutor_nombre,
            "tutor_parentesco": tutor_parentesco,
            "tutor_telefono": tutor_telefono,
            "tutor_telefono_alt": tutor_telefono_alt or "No especificado",
            "notas": notas or "Sin notas adicionales."
        }
    }

    # Guardar el JSON temporal
    TEMP_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(TEMP_JSON, "w", encoding="utf-8") as f:
        json.dump({"escenarios": [escenario]}, f, ensure_ascii=False, indent=2)

    print(f"✓ JSON guardado: {TEMP_JSON}")

    # Hacer backup del JSON original
    backup_file = DATA_FILE.with_suffix(".json.bak")
    if DATA_FILE.exists():
        shutil.copy2(DATA_FILE, backup_file)
        print(f"✓ Backup del JSON original: {backup_file}")

    # Copiar el JSON temporal al JSON principal
    shutil.copy2(TEMP_JSON, DATA_FILE)
    print(f"✓ JSON temporal copiado a: {DATA_FILE}")

    # Ejecutar generator.py
    print("\n--- Ejecutando generator.py ---")
    try:
        resultado = subprocess.run(
            [sys.executable, str(BASE_DIR / "src" / "generator.py")],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        print(resultado.stdout)
        if resultado.stderr:
            print("[STDERR]", resultado.stderr)
    except Exception as e:
        print(f"[ERROR] No se pudo ejecutar generator.py: {e}")
        return

    # Restaurar el JSON original
    if backup_file.exists():
        shutil.copy2(backup_file, DATA_FILE)
        backup_file.unlink()
        print(f"\n✓ JSON original restaurado.")

    # Buscar la imagen generada usando el ID del JSON temporal
    with open(TEMP_JSON, "r", encoding="utf-8") as f:
        temp_data = json.load(f)
        temp_id = temp_data["escenarios"][0]["id"]
        
    imagen_generada = OUTPUT_DIR / f"aura_{temp_id}.png"
    
    if imagen_generada.exists():
        print(f"\n✓ Imagen generada: {imagen_generada}")
        print("\n--- Próximos pasos ---")
        print(f"1. Abre la imagen: {imagen_generada}")
        print("2. Imprímela en una pulsera, sticker, o tarjeta.")
        print("3. Pégala en la muñeca del niño, mochila, o ropa.")
        print("4. Cualquiera puede escanearla con Google Lens para ver el contacto.")
        print("\n¡Listo! El AuraHash ID está creado.")
    else:
        print(f"\n[AVISO] No se encontró la imagen: {imagen_generada}")


if __name__ == "__main__":
    main()