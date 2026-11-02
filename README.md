# DigiRogue Online — proyecto preparado para Render

## Incluye
- Portada pixel art responsive y acceso al juego clásico.
- Arena WebSocket: salas privadas de hasta cuatro jugadores online.
- Ranking de kills registrado por el servidor en SQLite.
- Cristales de recompensa con escudo azul individual durante 12 segundos:
  el mundo no se pausa y los compañeros siguen luchando.

## Publicación
1. Abre https://github.com/lordcris87-netizen/digirogue
   y sube LOS ARCHIVOS DEL INTERIOR DE ESTE ZIP a la raíz del repositorio.
   `render.yaml`, `Dockerfile`, `server.py`, `index.html` y `assets/` deben
   quedar juntos en la raíz, no dentro de otra carpeta.
2. Abre:
   https://dashboard.render.com/blueprint/new?repo=https%3A%2F%2Fgithub.com%2Flordcris87-netizen%2Fdigirogue
3. Conecta GitHub con Render si lo solicita.
4. Verifica el precio antes de pulsar Apply: web service Docker plan `starter`
   y disco persistente de 1 GB montado en `/data` (servicio de pago).
5. Una vez Render diga `Live`, comprueba la URL pública y `/api/health`.
   Prueba dos navegadores en la misma sala y el ranking.

## Tests locales
- `python -m pip install -r requirements.txt`
- `python test_shield.py`
- `python -m py_compile server.py`

## Límites
Este archivo no publica la web ni aprueba pagos.
La clasificación se asocia a apodos, no a usuarios autenticados.
Diseñado para un único proceso y una instancia: no escalar horizontalmente
sin rehacer las salas y el almacenamiento.
El disco mantiene SQLite durante reinicios, pero hay que hacer copias
externas para proteger los datos frente a borrados o fallos graves.
La disponibilidad del alojamiento depende de mantener el plan activo.

## Edición ligera
Los sprites incrustados en `game.html` se han extraído en `assets/integrados/` sin borrar ninguno. NO separar esa carpeta del proyecto. Las imágenes se han conservado sin pérdida cuando ello permitía reducir su tamaño; otras están en WebP de alta calidad.
