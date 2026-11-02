# Portada animada — plan de integración (rama de desarrollo)

**No publicar en Render ni fusionar esta rama hasta superar pruebas visuales.**

## Inventario comprobado
- `assets/portada.webp`: 1672×941, RGB **sin transparencia**. Contiene los personajes pintados sobre el paisaje.
- `assets/agumon_idle.png`: 512×1024, RGBA; celdas de 128×128.
- `assets/agumonWalk.png`: 768×1024, RGBA; celdas de 128×128.
- `assets/agumon_attack.png`: 768×1024, RGBA; celdas de 128×128.
- `assets/bat.png`: 768×768, RGBA; celdas de 96×96.
- `assets/kunemon.png`: 384×768, RGBA; celdas de 96×96.
- `assets/goblimon.png`: 384×768, RGBA; celdas de 96×96.

## Bloqueo de producción
No mover los personajes recortándolos de `portada.webp`: el original carece de fondo limpio debajo y produciría huecos o dobles. Los sprites de la arena no garantizan igual aspecto/pose que los personajes pintados.

## Entregables para considerar completa la portada
1. Fondo limpio sin criaturas, conservando logo, menús, geometría y estilo de la portada original.
2. Capas RGBA individuales de cada criatura que coincidan con las siluetas originales, con bordes revisados a escala 100% y 200%.
3. Animaciones de respiración/parpadeo/salto/aleteo sin halos, recortes visibles ni duplicados.
4. Efectos de agua y vegetación independientes y sin desplazamiento de regiones completas del fondo.
5. Pruebas visuales en móvil vertical/horizontal y escritorio, incluido movimiento reducido.
6. Pruebas de /api/health, /ws, creación de sala, ranking y escudo azul.
7. Revisión de la versión desplegada en Render antes de notificar resultado.

## Política
No modificar `main`, Render ni contratar servicios hasta la aceptación explícita de una versión terminada.
