# Ejemplo de uso de AuraHash ID

> **Guía práctica:** cómo usar AuraHash ID desde PowerShell, VS Code, o llamando a una URL. Con todos los detalles, paso a paso.

---

## Índice

1. [Requisitos previos](#1-requisitos-previos)
2. [Instalación](#2-instalación)
3. [Generar llaves](#3-generar-llaves)
4. [Generar imágenes](#4-generar-imágenes)
5. [Leer un payload desde PowerShell](#5-leer-un-payload-desde-powershell)
6. [Leer un payload desde VS Code](#6-leer-un-payload-desde-vs-code)
7. [Probar la PWA desde el navegador](#7-probar-la-pwa-desde-el-navegador)
8. [Probar desde el celular (misma red WiFi)](#8-probar-desde-el-celular-misma-red-wifi)
9. [Personalizar tus propios datos](#9-personalizar-tus-propios-datos)
10. [Solución de problemas](#10-solución-de-problemas)
11. [Crear una pulsera de contacto (caso de uso real)](#11-crear-una-pulsera-de-contacto-caso-de-uso-real)

---

## 1. Requisitos previos

| Herramienta | Versión mínima | Cómo verificar |
|-------------|----------------|----------------|
| **Python** | 3.10+ | `python --version` |
| **pip** | (incluido con Python) | `pip --version` |
| **Git** | 2.30+ | `git --version` |
| **VS Code** (opcional) | 1.80+ | `code --version` |
| **Chrome/Edge** (para PWA) | 80+ | `chrome://version` |

**Si falta Python**: descárgalo de https://www.python.org/downloads/.
**Si falta Git**: descárgalo de https://git-scm.com/downloads.

---

## 2. Instalación

### Paso 1: Clonar el repositorio

Abre **PowerShell** y ejecuta:

```powershell
cd C:\Users\TU_USUARIO\Proyectos
git clone https://github.com/Matheus-Devilson/AuraHash-ID.git
cd AuraHash-ID
Verifica que estás en el lugar correcto:

powershell
Get-Location
Get-ChildItem | Select-Object Name
Deberías ver: src/, data/, docs/, pwa/, keys/, README.md, LICENSE, etc.

Paso 2: Instalar dependencias
powershell
pip install -r requirements.txt
Deberías ver: segno, numpy, Pillow, cryptography.

3. Generar llaves
Solo la primera vez. Si ya tienes las llaves, salta al paso 4.

Paso 1: Clave AES-256
powershell
python -c "import secrets, pathlib; pathlib.Path('keys').mkdir(exist_ok=True); pathlib.Path('keys/aes.key').write_bytes(secrets.token_bytes(32))"
Verifica:

powershell
Get-ChildItem keys\ | Select-Object Name, Length
Deberías ver aes.key (32 bytes).

Paso 2: Par Ed25519
powershell
python src/keys_manager.py
Deberías ver:

text
[INFO] Llave privada generada: keys/ed25519_private.key
[INFO] Llave pública generada: keys/ed25519_public.key
Verifica:

powershell
Get-ChildItem keys\
Deberías ver:

.gitkeep

aes.key

ed25519_private.key

ed25519_public.key

4. Generar imágenes
powershell
python src/generator.py
Deberías ver:

text
============================================================
  AuraHash ID - Generador Universal v3.0.1
  (Payload completo + Aura 5% opacidad + nonce determinista)
============================================================

[1/7] Procesando: salud_emergencia_02 (salud) [perfil: salud]
        OK Generado: aura_salud_emergencia_02.png
[2/7] Procesando: personal_ciclista_01 (personal) [perfil: salud]
        OK Generado: aura_personal_ciclista_01.png
...
[7/7] Procesando: militar_inteligencia_01 (militar) [perfil: legal]
        OK Generado: aura_militar_inteligencia_01.png

============================================================
  Generacion completada: 7/7 imagenes
============================================================
Verifica:

powershell
Get-ChildItem output\*.png | Select-Object Name, Length
Deberías ver 7 archivos .png (~1.3-1.5 MB cada uno).

5. Leer un payload desde PowerShell
Paso 1: Obtener el payload
Opción A: Escanear con Google Lens.

Abre output/aura_salud_emergencia_02.png en tu celular.

Escanéalo con Google Lens.

Copia el texto que aparece (empieza con PUB:...).

Opción B: Usar la PWA (ver sección 7).

Paso 2: Ejecutar reader.py
powershell
python src/reader.py
Deberías ver:

text
Pega el payload escaneado (una sola linea) y pulsa Enter:
(Ejemplo: PUB:{...}|MED:AES256GCMZ:...|ADM:AES256GCMZ:...|SHA:...|SIG:...)

> 
Paso 3: Pegar el payload
Click derecho en la terminal → Pegar (o Ctrl+V).

Luego pulsa Enter.

Paso 4: Ver el resultado
Deberías ver:

text
============================================================
  AuraHash ID - Reader v1.4.0
  Perfil: salud
============================================================

--- CAPA PUBLICA (texto claro) ---
  alergias_criticas : Mariscos
  instruccion       : Llame al 911 o contacte a familiar
  nombre_pila       : Sofia
  perfil            : salud
  tipo              : EMERGENCIA_MEDICA
  id_visual         : 8B4D-2A5E

--- CAPA MEDICA (descifrada) ---
  nombre_completo   : Sofia Ejemplo
  edad              : 34
  peso_aprox_kg     : 78
  tipo_sangre       : O+
  alergias          : Mariscos, Sulfamidas
  ...

--- CAPA ADMINISTRATIVA (descifrada) ---
  curp_parcial      : ****5678
  aseguradora       : GNP Seguros
  ...

--- INTEGRIDAD (SHA-256) ---
  Estado          : OK

--- FIRMA DIGITAL (Ed25519) ---
  Estado          : FIRMA OK
Si ves eso, ¡funciona! ✅

6. Leer un payload desde VS Code
Paso 1: Abrir VS Code en el proyecto
powershell
cd C:\Users\erasn\Proyectos\AuraHash-ID
code .
Paso 2: Abrir la terminal integrada
Ctrl + ñ (teclado español).

O Ctrl + ` (teclado inglés).

O menú: Terminal → New Terminal.

Paso 3: Ejecutar reader.py
En la terminal integrada:

powershell
python src/reader.py
Paso 4: Pegar el payload
Click derecho en la terminal → Pegar.

Luego Enter.

Paso 5: Ver el resultado
Igual que en la sección 5.

7. Probar la PWA desde el navegador
Paso 1: Iniciar el servidor local
En una terminal nueva:

powershell
cd C:\Users\erasn\Proyectos\AuraHash-ID\pwa
python -m http.server 8000
Deberías ver:

text
Serving HTTP on :: port 8000 (http://[::]:8000/) ...
Deja esa terminal abierta. No la cierres.

Paso 2: Abrir Chrome
Abre Chrome y ve a:

text
http://localhost:8000
Deberías ver la PWA de AuraHash ID. ✅

Paso 3: Probar con "Subir imagen"
Click en "📁 Subir imagen".

Selecciona output/aura_salud_emergencia_02.png.

La PWA muestra:

Perfil: SALUD.

Capa pública (texto claro).

Capa médica (descifrada).

Capa administrativa (descifrada).

SHA-256: OK.

Firma Ed25519: OK.

Paso 4: Probar con cámara (opcional)
Click en "▶ Iniciar cámara y escanear".

Apunta la cámara al Data Matrix en pantalla.

La PWA detecta y descifra.

Nota: la cámara solo funciona en localhost o HTTPS.

8. Probar desde el celular (misma red WiFi)
Paso 1: Averiguar tu IP local
En PowerShell:

powershell
ipconfig | Select-String "IPv4"
Busca algo como 192.168.1.100. Esa es tu IP local.

Paso 2: Iniciar el servidor
powershell
cd C:\Users\erasn\Proyectos\AuraHash-ID\pwa
python -m http.server 8000
Paso 3: Abrir en el celular
Conecta el celular a la misma red WiFi que la computadora.

Abre Chrome en el celular.

Ve a:

text
http://192.168.1.100:8000
(reemplaza 192.168.1.100 con tu IP real).

Deberías ver la PWA.

Paso 4: Probar con cámara
Problema: Chrome en el celular bloquea la cámara en HTTP (no HTTPS). Para que funcione, necesitas:

Opción A: Chrome flag chrome://flags/#unsafely-treat-insecure-origin-as-secure (solo Android).

Opción B: ngrok (crea URL HTTPS temporal).

Opción C: Probar solo con "Subir imagen" (subir una foto del Data Matrix).

9. Personalizar tus propios datos
Editar data/example_data.json
Abre data/example_data.json en VS Code.

Verás 7 escenarios. Elige uno y modifica sus campos.

Ejemplo: crear una pulsera para un niño perdido:

json
{
  "id": "contacto_mi_nino",
  "sector": "personal",
  "descripcion": "Pulsera de contacto para mi hijo",
  "capa_publica": {
    "perfil": "contacto",
    "tipo": "CONTACTO_FAMILIAR",
    "instruccion": "Soy autista. Puedo no responder. Contacte a mi familia.",
    "nombre_pila": "Diego",
    "evento": "Comunicacion limitada - hable despacio",
    "id_visual": "MI-NINO-01"
  },
  "capa_medica": null,
  "capa_administrativa": {
    "tutor_nombre": "Maria Ejemplo",
    "tutor_parentesco": "Madre",
    "tutor_telefono": "+52-55-1234-5678",
    "tutor_telefono_alt": "+52-55-8765-4321",
    "notas": "Diego es no verbal. Prefiere ambiente tranquilo."
  }
}
Guarda el archivo.

Regenerar la imagen
powershell
python src/generator.py
Se generará output/aura_contacto_mi_nino.png con tus datos.

Imprimir y usar
Abre la imagen en el explorador de Windows.

Imprímela en una pulsera, sticker, o tarjeta.

Pégala en la muñeca del niño, mochila, o ropa.

Cualquiera puede escanearla con Google Lens y ver el contacto.

10. Solución de problemas
Error: "No se encontró la clave AES"
Causa: falta keys/aes.key.
Solución:

powershell
python -c "import secrets, pathlib; pathlib.Path('keys').mkdir(exist_ok=True); pathlib.Path('keys/aes.key').write_bytes(secrets.token_bytes(32))"
Error: "La llave privada Ed25519 debe tener 32 bytes"
Causa: falta keys/ed25519_private.key o está corrupta.
Solución:

powershell
python src/keys_manager.py --force
Pero cuidado: --force regenera las llaves. Los payloads anteriores dejarán de ser válidos.

La PWA no detecta el Data Matrix
Causa: limitación de zxing-js con ciertos patrones.
Solución:

Prueba con otra imagen (algunas funcionan, otras no).

Usa Google Lens (100% de éxito).

Usa reader.py (100% de éxito).

Ver docs/LIMITACIONES.md.

La cámara no funciona en el celular
Causa: Chrome bloquea la cámara en HTTP (no HTTPS).
Solución:

Usa "Subir imagen" (sube una foto del Data Matrix).

O usa Chrome flag en Android.

O usa ngrok para HTTPS.

"Permiso denegado" al ejecutar python
Causa: Python no está en el PATH.
Solución:

Reinstala Python y marca "Add Python to PATH".

O usa py en lugar de python.

11. Crear una pulsera de contacto (caso de uso real)
Si quieres crear una pulsera para un niño, una mascota o un adulto mayor, no necesitas editar JSON ni tocar código. Usa el script interactivo crear_contacto.py.

Paso 1: Ejecutar el script
powershell
cd C:\Users\erasn\Proyectos\AuraHash-ID
python src/crear_contacto.py
Paso 2: Responder las preguntas
El script te guiará paso a paso:

text
--- ¿Para quién es? ---
1. Niño
2. Mascota
3. Adulto mayor
4. Otro
Elige (1-4): 1

--- Datos del titular ---
Nombre de pila: Carlos
Instrucción de emergencia: Hola, me llamo Carlos y me perdí. Por favor llama a mi familia.
Descripción adicional: Tengo 10 años
ID visual: NIÑO-2026-001

--- Datos del tutor/contacto ---
Nombre del tutor: Lorena Martinez
Parentesco: Madre
Teléfono principal: +52-55-9876-5432
Teléfono alternativo: (opcional)
Notas adicionales: (opcional)
Puedes pulsar Enter para usar los valores por defecto (los que aparecen entre corchetes).

Paso 3: Obtener la imagen
El script generará automáticamente:

text
✓ Imagen generada: output/aura_contacto_nino_personalizado.png
Paso 4: Imprimir y usar
Abre la imagen en el explorador de Windows.

Imprímela en una pulsera, sticker, o tarjeta.

Pégala en la muñeca del niño, mochila, o ropa.

Cualquiera puede escanearla con Google Lens para ver el contacto.

Qué datos se guardan
Capa	Datos	¿Visible con Google Lens?
Pública	Nombre, instrucción, descripción, ID visual	✅ Sí
Administrativa	Tutor, parentesco, teléfonos, notas	❌ No (cifrado)
Ventaja: el teléfono del tutor no es visible con Google Lens. Solo con la PWA o reader.py (que tienen la llave AES-256).

Ejemplo de uso
Escenario: un padre crea una pulsera para su hijo Carlos.

Ejecuta python src/crear_contacto.py.

Responde las preguntas con los datos de Carlos.

Obtiene output/aura_contacto_nino_personalizado.png.

Imprime la imagen en una pulsera.

Se la pone a Carlos en la muñeca.

Carlos se pierde en un parque.

Alguien lo encuentra y escanea la pulsera con Google Lens.

Ve: "Hola, me llamo Carlos y me perdí. Por favor llama a mi familia."

No ve el teléfono del tutor (está cifrado).

Pero puede llamar a la policía, o usar la PWA (si la tiene) para descifrar el teléfono.

Alternativa: el padre puede configurar la capa pública para incluir el teléfono directamente (sin cifrar). Pero entonces cualquiera podría verlo.

Balance: privacidad vs accesibilidad. El diseño actual permite ambas opciones.

Resumen rápido de comandos
Acción	Comando
Clonar repo	git clone https://github.com/Matheus-Devilson/AuraHash-ID.git
Instalar dependencias	pip install -r requirements.txt
Generar llaves AES	python -c "import secrets, pathlib; pathlib.Path('keys').mkdir(exist_ok=True); pathlib.Path('keys/aes.key').write_bytes(secrets.token_bytes(32))"
Generar llaves Ed25519	python src/keys_manager.py
Generar imágenes	python src/generator.py
Leer payload	python src/reader.py
Iniciar PWA	cd pwa; python -m http.server 8000
Abrir PWA	Chrome → http://localhost:8000
Verificar estado	git log --oneline -3; git status
Crear pulsera personalizada	python src/crear_contacto.py
Última actualización: 2026-10-18