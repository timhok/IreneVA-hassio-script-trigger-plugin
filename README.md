# Триггер скриптов Home Assistant
Плагин для [Ирины, голосового ассистента](https://github.com/janvarev/Irene-Voice-Assistant)

Данный плагин открывает огромные возможности для Ирины, позволяя запускать голосом скрипты в Home Assistant.

Запросы делаются по [REST API](https://developers.home-assistant.io/docs/api/rest/), благадоря чему отпадает надобность в перезапуске и Ирины, и HA.

## Как использовать плагин
1. Скачайте репозиторий и положите папку plugins в директорию с репозиторием Ирины (или просто положите файл в plugins)
2. Запустите Ирину вместе с плагином один раз и убедитесь, что в папке `options` появился файл `plugin_hassio_script_trigger.json`
3. Получите "Долгосрочный токен доступа" / [long lived access token](https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token) в своём профиле в Home Assistant
4. Откройте файл `plugin_hassio_script_trigger.json` в текстовом редакторе
5. Замените ссылку напротив `hassio_url` на ссылку вашего Home Assistant, обратите внимание - в конце должен быть символ `/`
6. Впишите ваш токен из пункта 2 напротив `hassio_key`

## Принцип работы
- После получения одной из команд плагина в API вашего HA запрашивается список всех доступных сервисов, из этого списка выбираются только скрипты.
- В списке скриптов плагин ищет совпадения фразы и алиаса скрипта (HA позволяет давать названия скриптам на кириллице).
- Если скрипт нашёлся - делается запрос на его выполнение по "ID объекта"
- Бонусом Ирина озвучит текст из описания в специальном формате - `ttsreply(текст)` (для добавления описания к скрипту придется открыть текстовый редактор)

## Примеры команд и скриптов
1. Вы говорите "ирина хочу спать"

>Скрипт выключает весь свет, в спальне включает ночник и устанавливает комфортную температуру, жалюзи закрываются, ассистент желает вам приятных снов

```YAML
alias: хочу спать
description: ttsreply(Приятных снов)
sequence:
  - service: light.turn_off
    data: {}
    target:
      area_id:
        - kuhnya
        - korridor
        - spalnia
  - service: light.turn_on
    data:
      brightness_pct: 20
      kelvin: 2500
    target:
      entity_id: light.tradfri_lamp_level_light_color_on_off
  - service: climate.set_temperature
    data:
      temperature: 20
    target:
      area_id: spalnia
  - service: switch.turn_on
    data: {}
    target:
      entity_id: switch.blinds_bedroom
mode: single
icon: mdi:bed
```

2. Вы говорите "ирина я буду собираться на работу"

>Скрипт присылает вам на телефон прогноз погоды и примерное время пути, термостат отключается, включается чайник на кухне, ассистент желает  продуктивного дня

2. Вы говорите "ирина сделай свет ярче"

>Жалюзи открываются, включается свет
