# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.1.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [3.0.1] - 2026-10-16

### Añadido
- Nonce determinista para reproducibilidad.
- Documentación de limitaciones (`docs/LIMITACIONES.md`).
- Comparativa de lectores (reader.py vs Google Lens vs PWA).
- Scripts de diagnóstico para barrido de opacidades.

### Cambiado
- Opacidad del Aura a 5%.
- Reemplazo de `salud_emergencia_01` por `salud_emergencia_02`.
- Reemplazo de `legal_contrato_01` por `legal_contrato_02`.

### Corregido
- Patrón de Data Matrix en varios escenarios.

## [3.0.0] - 2026-10-15

### Añadido
- PWA Reader v2.0.1 (lectura Data Matrix + AES-256-GCM + Ed25519).
- 7 escenarios universales (salud, contacto, verificación, legal, militar).
- Documentación de visión universal (`docs/VISION.md`).

### Cambiado
- Payload completo (PUB + MED + ADM + SHA + SIG).

## [2.4.1] - 2026-10-14

### Añadido
- Firma digital Ed25519 end-to-end.
- 4 perfiles formalizados (salud, contacto, verificación, legal).

## [2.4.0] - 2026-10-13

### Añadido
- Versión inicial del generador con Data Matrix + Aura + SHA-256.
