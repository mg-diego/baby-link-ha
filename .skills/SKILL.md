# Home Assistant Custom Component: Baby Link Integration

## 🎯 Objetivo del Proyecto
Desarrollar una integración personalizada (Custom Component) nativa para Home Assistant que conecte con la API de seguimiento del bebé (basada en Supabase/REST) para exponer el estado actual del bebé, últimas actividades y métricas del día en tiempo real dentro del ecosistema smart home.

## 🏛️ Arquitectura y Estructura del Repositorio
La integración debe seguir estrictamente los estándares modernos de desarrollo para Home Assistant (HACS compatible). Estructura obligatoria de archivos en el repositorio:

```text
custom_components/
  baby_link/
    __init__.py           # Configuración del entry y registro del Coordinator
    manifest.json         # Metadatos de la integración (domain, version, codeowners)
    config_flow.py        # Interfaz UI para que el usuario añada la API Key/URL en HA
    const.py              # Definición de dominios, intervalos de actualización y constantes
    coordinator.py        # DataUpdateCoordinator: peticiones a la API y caché de estado
    sensor.py             # Entidades de solo lectura (Última toma, último pañal, métricas hoy)
    binary_sensor.py      # Entidades booleanas (¿Está dormido?, ¿Necesita cambio?)
    button.py             # Acciones rápidas (Registrar pañal mojado, Iniciar siesta)
```



## 🔌 Especificación de la API Backend (Fuente de Datos)

La integración consumirá un endpoint REST en formato JSON que devuelve el resumen general del bebé (basado en el dashboard general del usuario).

Ejemplo del Payload JSON esperado de la API (GET /api/ha/overview):
```JSON
{
  "baby_id": "336351d0-40a3-4f4a-a04f-969a58212cb0",
  "name": "Lucas",
  "current_state": {
    "is_sleeping": true,
    "current_sleep_type": "Siesta",
    "sleeping_since": "2026-07-03T09:15:00Z"
  },
  "today_summary": {
    "total_sleep_mins": 630,
    "total_feeds": 4,
    "total_diapers": 3
  },
  "last_events": {
    "last_feed": {
      "time": "2026-07-03T08:30:00Z",
      "type": "bottle",
      "amount_ml": 180
    },
    "last_diaper": {
      "time": "2026-07-03T08:45:00Z",
      "condition": "wet"
    }
  }
}
```


## 🧩 Entidades que debe generar la integración
1. Binary Sensors (binary_sensor.py)
- binary_sensor.baby_sleeping: Estado on si current_state.is_sleeping == true. Usar device_class: occupancy o icono personalizado (mdi:sleep / mdi:eye).

2. Sensors (sensor.py)
- sensor.baby_last_feed_time: Timestamp del último feed (device_class: timestamp). Atributos extra: type, amount_ml.

- sensor.baby_last_diaper_time: Timestamp del último pañal (device_class: timestamp). Atributos extra: condition.

- sensor.baby_today_sleep_hours: Total de horas de sueño hoy (calculado dividiendo total_sleep_mins / 60). Unidad: h.

- sensor.baby_today_feeds: Contador total de tomas de hoy. Icono: mdi:baby-bottle.

- sensor.baby_today_diapers: Contador total de pañales de hoy. Icono: mdi:human-baby-changing-table.



## 🛠️ Normas de Código y Buenas Prácticas (Estrictas)
1. Asíncrono siempre: Toda petición a la red debe usar aiohttp (proporcionado por Home Assistant a través de async_get_clientsession(hass)). Nunca usar librerías síncronas como requests.

2. DataUpdateCoordinator: Todo el polling debe gestionarse desde un único DataUpdateCoordinator para hacer una sola petición de red cada 60 segundos y actualizar todas las entidades a la vez.

3. Manejo de Errores: Capturar timeouts o errores de conexión envolviéndolos en una excepción UpdateFailed de Home Assistant para que las entidades pasen a estado Unavailable de manera limpia si el servidor no responde.

4. Tipado y Traducciones: Código compatible con Python 3.11+, tipado estricto y soporte para cadenas de traducción (strings.json).

5. UI Config Flow: La integración no debe configurarse por YAML. Debe incluir un ConfigFlow para poder instalarse cómodamente desde la interfaz de usuario de Home Assistant solicitando la URL del servidor y el Token/Baby ID.