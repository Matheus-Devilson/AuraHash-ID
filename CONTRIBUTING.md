# Contribuir a AuraHash ID

Gracias por tu interés en contribuir. Este documento explica cómo hacerlo.

## ¿Encontraste un bug?

Abre un [Issue](https://github.com/Matheus-Devilson/AuraHash-ID/issues) con:

- **Descripción del problema**: qué esperabas que pasara y qué pasó.
- **Pasos para reproducirlo**: lista numerada.
- **Entorno**: sistema operativo, versión de Python, navegador (si aplica).
- **Capturas o logs**: si es posible.

## ¿Tienes una idea o sugerencia?

Abre un [Issue](https://github.com/Matheus-Devilson/AuraHash-ID/issues) con:

- **Descripción de la idea**.
- **Casos de uso**.
- **Posible implementación** (opcional).

## ¿Quieres contribuir con código?

1. **Fork** el repositorio.
2. **Crea un branch**: `git checkout -b mejora-xyz`
3. **Haz los cambios**.
4. **Prueba**: `python src/generator.py` debe generar 7 imágenes.
5. **Commit**: `git commit -m "feat: mejora xyz"`
6. **Push**: `git push origin mejora-xyz`
7. **Abre un Pull Request** contra `main`.

## Estilo de código

- **Python**: PEP 8.
- **Comentarios**: en español.
- **Commits**: en español, con prefijo (`feat:`, `fix:`, `docs:`, `refactor:`).

## Limitaciones conocidas

Antes de contribuir, lee [`docs/LIMITACIONES.md`](docs/LIMITACIONES.md). La PWA tiene una tasa de éxito del ~70% por limitaciones de zxing-js. **No es un bug, es una limitación documentada.**

## Licencia

Al contribuir, aceptas que tu código se distribuya bajo la licencia MIT.
