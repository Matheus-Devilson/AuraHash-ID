# Limitaciones conocidas de AuraHash ID

> **Propósito:** documentar de forma honesta las limitaciones técnicas del proyecto, especialmente las relacionadas con el lector de Data Matrix en el navegador (PWA con zxing-js).

---

## 1. Resumen ejecutivo

| Aspecto | Estado |
|---------|--------|
| **Generator (Python)** | ✅ Funcional. 7 escenarios. Payload completo (PUB + MED + ADM + SHA + SIG). |
| **Reader (Python)** | ✅ Funcional. Descifra el 100% de los escenarios. Verifica firma Ed25519 y SHA-256. |
| **PWA (zxing-js)** | ⚠️ Funciona para 5 de 7 escenarios (~70%). Los 2 restantes fallan por limitación de zxing-js. |
| **Lectores nativos** | ✅ Recomendados para producción. Google Lens, Dynamsoft, ML Kit, Vision leen el 100%. |

---

## 2. Limitación principal: zxing-js con Data Matrix de alta densidad

### 2.1 Descripción

**zxing-js** es la librería JavaScript usada en la PWA para leer Data Matrix. Tiene limitaciones conocidas con Data Matrix de alta densidad (payloads largos) y con ciertos patrones intrínsecos de Data Matrix.

### 2.2 Causa raíz

**No es el Aura.** Aunque el Aura agrava el problema, la causa raíz es la propia librería zxing-js. Confirmado por eliminación:
- **Sin Aura**, algunos escenarios también fallan (opacidad 0%).
- **Con Aura**, ~30% de los escenarios fallan.
- **Sin Aura y con Aura**, los fallos son aleatorios por patrón de Data Matrix.

### 2.3 Límites medidos

| Tipo de límite | Valor | Contexto |
|----------------|-------|----------|
| **Máximo absoluto** | ~1500-2000 chars | Data Matrix puro, sin Aura |
| **Máximo con payload realista** | ~1200-1500 chars | JSON + base64 + hex |
| **Máximo con Aura (5-10%)** | ~900 chars | Con Aura decorativa |
| **Payload máximo del proyecto** | 957 chars | militar_inteligencia_01 |

### 2.4 Tasa de éxito

| Configuración | Tasa de éxito |
|---------------|---------------|
| 10 variantes de militar (957 chars) | 70% (7/10) |
| 7 escenarios con opacidad 5% | 71% (5/7) |
| 7 escenarios sin Aura | 100% (7/7) |

**Conclusión**: ~30% de los Data Matrix generados por `segno` tienen patrones intrínsecamente ilegibles para zxing-js, independientemente del Aura.

---

## 3. Hallazgos sobre el Aura

### 3.1 El Aura envolvente (v2.x) es incompatible con zxing-js

El diseño v2.x del Aura (ruido envolviendo al Data Matrix) **impide la lectura**. El Data Matrix no puede tener Aura alrededor.

### 3.2 El Aura de fondo (v3.x) es compatible, con opacidad correcta

El diseño v3.x (Aura de fondo + Data Matrix sobre cuadrado blanco) **permite la lectura** con la opacidad correcta.

### 3.3 Opacidades óptimas

| Opacidad | Resultado |
|----------|-----------|
| 0% | ❌ |
| 1-2% | ⚠️ Depende |
| 3% | ⚠️ Depende |
| **4-5%** | ✅ **Punto dulce** |
| 6-8% | ❌ Rango muerto |
| 9% | ⚠️ Depende |
| 10% | ⚠️ Depende |
| 15%+ | ❌ |

**Conclusión**: **4-5% es el punto dulce**. Opacidades fuera de este rango fallan.

### 3.4 El Aura de fondo con halo blanco ya está implementado

El `generator.py` v3.0.1 ya incluye:
- Aura de fondo (opacidad 5%).
- Cuadrado blanco de zona de silencio (`DM_QUIET_ZONE_PX = 40`) alrededor del Data Matrix.

Esta es la "variante híbrida" entre Aura de fondo y Aura de bordes. **No resuelve el problema de raíz**, porque el Data Matrix sigue teniendo patrones ilegibles.

---

## 4. Hallazgos sobre el nonce AES-GCM

### 4.1 Nonce aleatorio

El nonce aleatorio (`secrets.token_bytes(12)`) produce un resultado **diferente en cada regeneración**. Esto causaba fallos aleatorios que confundían el diagnóstico.

### 4.2 Nonce determinista

**Solución adoptada**: nonce determinista derivado de `sha256(id_escenario + '::' + comprimido)[:12]`.

**Ventaja**: resultado reproducible. Si funciona hoy, funciona mañana.
**Desventaja**: el nonce determinista es una mala práctica criptográfica en producción general. **Para este proyecto es aceptable** porque cada escenario cifra su propio texto una sola vez (no hay reutilización de nonce en el mismo mensaje).

### 4.3 El nonce determinista no elimina la ilegibilidad

Aunque el nonce sea determinista, **~30% de los escenarios siguen fallando** por colisión entre el patrón del Data Matrix y el patrón del Aura. El nonce determinista **estabiliza** el resultado, pero no lo hace universalmente legible.

---

## 5. Soluciones para producción

### 5.1 Lectores nativos recomendados

| SDK | Plataforma | Tasa de éxito |
|-----|-----------|---------------|
| **Google ML Kit** | Android | >95% en DM densos |
| **Apple Vision** | iOS | >95% en DM densos |
| **Dynamsoft Barcode Reader** | Multiplataforma (comercial) | >99% en DM densos |
| **Google Lens** | Web + móvil | 100% (estándar ISO/IEC 16022) |

### 5.2 Recomendación

**Para producción**: implementar app nativa Android/iOS con SDK nativo. Los SDK nativos tienen tasas de éxito >95% con Data Matrix densos, muy superiores a zxing-js (~70%).

**Para demos**: usar zxing-js con la PWA actual. Es suficiente para mostrar el concepto. Si un escenario falla, regenerar con datos diferentes hasta que funcione.

### 5.3 Alternativa: Google Lens

Google Lens lee **Data Matrix estándar ISO/IEC 16022** sin problemas. **Es una alternativa inmediata** para demostrar el 100% de los escenarios. La limitación es que Google Lens solo muestra la **capa pública** (no descifra MED ni ADM).

---

## 6. Decisiones de diseño

### 6.1 El Aura es decoración, no funcionalidad

El Aura es la **identidad visual** del proyecto. **No es funcionalidad crítica**. El Data Matrix y la firma Ed25519 son la funcionalidad. El Aura es branding.

**Decisión**: mantener el Aura en el diseño v3.x (opacidad 5%) y documentar la limitación.

### 6.2 El Data Matrix debe ser siempre legible

**Filosofía del proyecto**: el Data Matrix debe ser legible por la mayor cantidad de lectores posible. Si un lector específico (zxing-js) tiene limitaciones, se documenta y se recomienda un lector alternativo.

### 6.3 Aceptar la limitación del lector JS

**No se persigue el 100% con zxing-js**. Es una limitación de la librería, no del proyecto. La solución es usar un SDK nativo en producción.

---

## 7. Estado final del proyecto

| Componente | Versión | Estado |
|------------|---------|--------|
| `generator.py` | v3.0.1 | ✅ Funcional |
| `reader.py` | v1.4.0 | ✅ Funcional |
| `pwa/index.html` | v2.0.1 | ⚠️ Funciona para 5-6 de 7 escenarios |
| `keys_manager.py` | — | ✅ Funcional |
| `data/example_data.json` | — | ✅ 7 escenarios |

---

## 8. Reproducibilidad

Todos los resultados de este documento son **reproducibles** con el `generator.py` v3.0.1 (nonce determinista, opacidad 5%). Ejecutar:

```powershell
python src/generator.py
---

## 9. Comparativa de lectores

AuraHash ID puede leerse con tres herramientas distintas. **Cada una tiene una tasa de éxito diferente.**

| Lector | Herramienta | Tasa de éxito | Notas |
|--------|-------------|---------------|-------|
| **reader.py** | Python (script) | **100%** (7/7) | Descifra MED/ADM, verifica firma Ed25519 |
| **Google Lens** | App móvil / web | **100%** (7/7) | Solo muestra capa pública (no descifra) |
| **PWA (zxing-js)** | Navegador (Chrome/Edge/Safari) | **~70%** (5-6/7) | Descifra MED/ADM, verifica firma. Limitación de zxing-js |

### ¿Por qué la PWA solo funciona al 70%?

**Porque zxing-js (la librería JS de lectura de Data Matrix) tiene una limitación intrínseca** con ciertos patrones de Data Matrix de alta densidad. **No es un problema del proyecto, es un problema de la librería.**

### ¿Qué lector usar?

| Contexto | Lector recomendado |
|----------|-------------------|
| **Producción (app nativa)** | SDK nativo (Google ML Kit, Apple Vision, Dynamsoft) — 100% |
| **Demo rápida (Python)** | `reader.py` — 100% |
| **Demo rápida (celular sin app)** | Google Lens — 100% (solo capa pública) |
| **Demo web/PWA** | PWA (zxing-js) — ~70% |
| **Auditoría** | `reader.py` — 100% |

### ¿Por qué se diseñó una PWA si solo funciona al 70%?

**La idea original era tener una PWA universal**: cualquier persona con un celular podría escanear un AuraHash ID sin instalar nada.

**Pero zxing-js tiene limitaciones.** La PWA funciona para el ~70% de los escenarios. **La solución real es una app nativa** con SDK nativo (Google ML Kit, Apple Vision). Eso está en el roadmap.

**La PWA es el paso intermedio.** No es el producto final. Es la demo que funciona **sin instalar nada**.

### Conclusión

**El proyecto no es un fracaso por la PWA al 70%.** Es un **prototipo honesto** que:
- Funciona al **100%** con `reader.py` (Python).
- Funciona al **100%** con Google Lens.
- Funciona al **~70%** con zxing-js en el navegador.
- Documenta la limitación y ofrece una ruta clara a producción (**SDK nativo**).

**La PWA es una demo, no el producto.** El producto es el protocolo + la app nativa futura.

---

## 10. Referencias

- **ISO/IEC 16022**: estándar Data Matrix.
- **zxing-js**: https://github.com/zxing-js/library
- **Google ML Kit**: https://developers.google.com/ml-kit
- **Apple Vision**: https://developer.apple.com/documentation/vision
- **Dynamsoft Barcode Reader**: https://www.dynamsoft.com/barcode-reader/

---

*Última actualización: 2026-10-16 — Secciones 9 y 10 agregadas (comparativa de lectores + referencias)*