# Checklist de calidad de la especificación

**Feature**: [015-beatgrid-loop](../spec.md)
**Revisión**: 2026-10-18. Esta checklist evalúa documentación, no implementación.

- [x] Objetivo y alcance definidos: Auto Loop musical, Resize, Exit y Reloop.
- [x] Beats, segundos, frames de fuente interna y frames de salida distinguidos.
- [x] Evidencia REA guardada reutilizada con rutas, hashes y límites.
- [x] Símbolos/QML separados de ejecución; modulo/anti-click etiquetados como diseño.
- [x] Historias prioritarias con aceptación y pruebas independientes.
- [x] Requisitos medibles de deriva, PCM, memoria, concurrencia y sync.
- [x] Grid variable, revisión, EOF, microloops y cambio de pista cubiertos.
- [x] Semánticas de resize, pausa, Exit/Reloop y scratch explícitas.
- [x] Deuda actual de RT reconocida; preparación/retirada fuera del callback.
- [x] Tests, UI y contratos tienen tareas con rutas y dependencias.
- [x] Roll/Slip, persistencia y equivalencia DSP propietaria no se prometen.
- [x] Las tareas y pruebas de implementación permanecen pendientes.

## Gates de entrega del motor (pendientes)

- [ ] Oráculos de geometría/transporte/PCM aprobados.
- [ ] Cero operaciones RT prohibidas y presupuesto de caché verificado.
- [ ] Sync con loops fraccionales y grid variable validado.
- [ ] Anti-click, capturas y escucha registrados.
- [ ] Suite completa y matriz FR→tests de implementación cerradas.
