# AuraHash ID — Prompt Maestro

> **Propósito de este archivo:** briefing estático del proyecto para que cualquier IA (o humano) pueda retomarlo sin contexto previo. No contiene estado vivo (eso vive en `docs/MINI-CONTEXTO_v3.txt`). Este documento cambia solo cuando cambia la arquitectura, filosofía o reglas operativas.

---

## 1. Visión del Proyecto

**AuraHash ID** es un protocolo universal de identificación física-digital. Vincula objetos, personas y documentos con su identidad digital de forma **segura, offline y privada**.

**Propuesta de valor:** verificación de identidad sin depender de servidores, sin apps propietarias, sin rastreo. Criptografía de grado bancario aplicada al mundo físico.

**Filosofía:**
- **100% Offline-First.** Cero dependencia de servidores en el momento de la lectura.
- **Privacidad por Diseño.** Los datos sensibles nunca viajan en claro.
- **Estándares abiertos.** Data Matrix (ISO/IEC 16022) como núcleo de compatibilidad universal.

---

## 2. Arquitectura de Datos (3 Capas)

El payload se estructura en tres capas, cada una con distinto nivel de exposición y protección:

| Capa | Contenido | Protección | Visible con Google Lens |
|------|-----------|-----------|-------------------------|
| `capa_publica` | Nombre de pila, instrucción de emergencia, alergias críticas | **Texto claro** (JSON minificado, claves cortas) | ✅ Sí |
| `capa_medica` | Tipo de sangre, condiciones, medicamentos, notas | **zlib + AES-256-GCM** | ❌ No |
| `capa_administrativa` | Pólizas, CURP parcial, datos legales | **zlib + AES-256-GCM** | ❌ No |

Toda la integridad se refuerza con **Ed25519** (firma digital del payload completo).

---

## 3. Formato del Payload (v2.4.0)

```
PUB:{json_minificado}|MED:AES256GCMZ:{base64}|ADM:AES256GCMZ:{base64}|SHA:{32hex}|SIG:{base64}
```

**Bloques:**

| Bloque | Descripción |
|--------|-------------|
| `PUB:` | JSON minificado con claves cortas. Texto claro. |
| `MED:` | Capa médica cifrada (`AES256GCMZ:` = zlib + AES-256-GCM). |
| `ADM:` | Capa administrativa cifrada (mismo esquema que `MED:`). |
| `SHA:` | SHA-256 maestro truncado a 32 hex (128 bits). |
| `SIG:` | Firma Ed25519 del mensaje `PUB|MED|ADM|SHA` en base64 (64 bytes). Opcional para retrocompatibilidad. |

**Mapa de claves cortas PUB (minificación):**

```
tipo -> t
instruccion -> i
nombre_pila -> n
alergias_criticas -> a
id_visual -> v
evento -> e
```

**Prefijos de cifrado soportados:**
- `AES256GCMZ:` → zlib + AES-256-GCM (actual, v2.3.0+)
- `AES256GCM:` → solo AES-256-GCM (legacy v2.1.0)

---

## 4. Stack Tecnológico

- **Python 3.14.8** (mínimo 3.10+)
- **segno** — Data Matrix (ISO/IEC 16022)
- **numpy + Pillow** — Aura estocástica e imagen final
- **cryptography 50.0.2** — AES-256-GCM + Ed25519
- **zlib** (stdlib) — Compresión previa al cifrado
- **VS Code + PowerShell + Git** — Entorno de desarrollo

---

## 5. Estructura de Archivos

```
AuraHash-ID/
├── src/
│   ├── generator.py         # Motor v2.4.0 (AES-256-GCM + zlib + Ed25519)
│   ├── reader.py            # Lector/verificador v1.3.0
│   └── keys_manager.py      # Generador de llaves Ed25519
├── data/
│   ├── .gitkeep
│   └── example_data.json    # 4 escenarios (texto plano legible)
├── output/                  # Imágenes generadas (ignorado por git)
├── keys/
│   ├── aes.key              # Clave AES-256 (IGNORADA por git)
│   ├── ed25519_private.key  # Llave privada Ed25519 (IGNORADA por git)
│   ├── ed25519_public.key   # Llave pública Ed25519 (TRACKEADA)
│   └── .gitkeep
├── docs/
│   ├── AI_CONTEXT.md        # Este archivo
│   └── MINI-CONTEXTO_v3.txt # Estado vivo del proyecto
├── backups/                 # Backups locales (ignorado por git)
├── .gitignore
├── LICENSE                  # MIT
├── README.md
└── requirements.txt
```

---

## 6. Convenciones de Código

- **Idioma:** español en comentarios, docstrings y mensajes al usuario.
- **Encoding:** UTF-8 sin BOM en todos los archivos.
- **Estilo:** snake_case para funciones y variables. Funciones puras cuando sea posible.
- **Sin dependencias exóticas.** Cada lib debe justificarse.
- **Serialización canónica:** JSON con `sort_keys=True, ensure_ascii=False, separators=(',', ':')` para que el hash sea reproducible.
- **Hashes sobre texto plano original**, no sobre ciphertext. Esto garantiza estabilidad aunque cambie el formato de salida.
- **La capa pública nunca se cifra.** Es información de emergencia.

---

## 7. Reglas Operativas

Al trabajar en este proyecto, respetar:

1. **PowerShell 5.1:** máximo 5-6 líneas por bloque pegado. Nunca bloques >30 líneas.
2. **Editar `.md` y `.py` largos:** en VS Code o Notepad. **NUNCA** pegar código Python directamente en PowerShell.
3. **Antes de cambios:** `Copy-Item [archivo] backups/[archivo]_ANTES_[fecha]`.
4. **Verificar** con `Select-String` o `python -c` después de cada cambio.
5. **Commits atómicos:** un commit + push por cada pendiente terminado. No acumular.
6. **Sin saludos ni relleno.** Directo al grano.
7. **Código completo, sin `...`.** El usuario no es programador profesional; guiarlo paso a paso con comandos exactos.
8. **Explicar términos técnicos brevemente** cuando aparezcan por primera vez.
9. **Nunca heredar métricas de contexto entre chats.** Cada chat empieza en N1 (0-25%).
10. **Cero invención de detalles** (rutas, comandos, hashes). Si no se sabe, se verifica.

---

## 8. Flujo de Trabajo Estándar

```
1. Confirmar HEAD + working tree limpio (git log, git status)
2. Backup del/los archivo(s) a modificar
3. Editar en VS Code (no PowerShell)
4. Verificar sintaxis (python -m py_compile)
5. Probar funcionalidad end-to-end
6. Limpiar archivos temporales de prueba
7. git add + git commit + git push
8. Actualizar docs/MINI-CONTEXTO_v3.txt si corresponde
```

---

## 9. Roadmap

**Completado:**
- [x] Definición de arquitectura y visión universal
- [x] Estructura inicial del repositorio
- [x] Generador universal (JSON → AuraHash)
- [x] Cifrado AES-256-GCM + zlib en capas sensibles
- [x] Firma digital Ed25519 end-to-end
- [x] Lector/verificador offline (`reader.py`)
- [x] Optimización del payload (-21.8%)
- [x] README + LICENSE + limpieza de repo

**Pendiente:**
- [ ] `docs/AI_CONTEXT.md` (este archivo — en construcción)
- [ ] SDK para apps móviles (iOS/Android)
- [ ] Aura Dinámica para boletos digitales (rotación cada 30s)
- [ ] Alianzas con fabricantes de pulseras y calcomanías industriales
- [ ] Recorte opcional de `example_data.json` (~6%, no urgente)

---

## 10. Modelo de negocio y flujo de eventos

AuraHash ID no es un producto cerrado. Es un **protocolo abierto (MIT)** que cualquier emisor (hospital, empresa, promotor) puede adoptar. El valor no está en el software, está en la **arquitectura criptográfica** que resuelve problemas concretos.

### 10.1 — Sector eventos (caso de referencia)

El flujo completo está en `docs/FLUJO_EVENTOS.md`. Resumen:

- **Principio:** el boleto es un activo **controlado por el emisor**, no propiedad absoluta del comprador (modelo boleto aéreo).
- **Vinculación:** el AuraHash lleva `SHA-256(INE + nombre)` del comprador. La INE nunca viaja en claro.
- **Verificación:** offline-first con lista firmada de IDs válidos descargada a las pistolas antes del evento.
- **Reembolso:** política configurable por el emisor (`ventana_gratis_horas`, `costo_adicional_mxn`, etc.).
- **Anti-reventa:** sin la INE del titular, el boleto no entra. Transferencia solo por canal oficial.
- **Auditoría:** métricas completas post-evento (vendidos, reembolsados, asistencia, fraudes detectados).

### 10.2 — Speech para presentaciones

El documento `docs/VISION_COMERCIAL.md` contiene el **discurso de presentación** y las **preguntas frecuentes** de un auditorio con empresarios/promotores. NO es un pitch de venta corporativo, es un speech honesto sobre capacidades y limitaciones.

### 10.3 — Aclaración importante

AuraHash ID hoy es **MVP funcional + visión documentada**. NO es:
- Un producto listo para vender.
- Un reemplazo de Ticketmaster / ODESA.
- Una solución completa sin integración.

Lo que ofrece:
- Protocolo abierto y auditable.
- Arquitectura criptográfica probada.
- Camino claro para adopción por fases (piloto → expansión → producción → escala).

---

## 11. Referencias

- `docs/MINI-CONTEXTO_v3.txt` — Estado vivo del proyecto (pendientes, HEAD, métricas).
- `docs/PERFILES.md` — Los 4 perfiles (salud/contacto/verificacion/legal).
- `docs/FLUJO_EVENTOS.md` — Flujo end-to-end del sector eventos.
- `docs/VISION_COMERCIAL.md` — Speech y Q&A para presentaciones.
- `README.md` — Documentación pública.
- `LICENSE` — MIT.
- GitHub: https://github.com/Matheus-Devilson/AuraHash-ID (privado).

---

*Última actualización: 2026-10-15 — Pendiente #13*
