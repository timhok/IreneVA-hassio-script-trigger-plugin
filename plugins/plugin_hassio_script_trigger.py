# Триггер скриптов Home Assistant
# author: Timhok

import os
import random

from vacore import VACore

modname = os.path.basename(__file__)[:-3] # calculating modname

# функция на старте
def start(core:VACore):
    manifest = {
        "name": "Триггер скриптов Home Assistant",
        "version": "1.0",
        "require_online": True,

        "default_options": {
            "hassio_url": "http://hassio.lan:8123/",
            "hassio_key": "", # получить в /profile, "Долгосрочные токены доступа"
            "default_reply": [ "Хорошо", "Выполняю", "Будет сделано" ], # ответить если в описании скрипта не указан ответ в формате "ttsreply(текст)"
        },

        "commands": {
            "хочу|сделай|я буду": hassio_run_script,
        }
    }
    return manifest

def start_with_options(core:VACore, manifest:dict):
    pass

def hassio_run_script(core:VACore, phrase:str):

    options = core.plugin_options(modname)

    if options["hassio_url"] == "" or options["hassio_key"] == "":
        print(options)
        core.play_voice_assistant_speech("Нужен ключ или ссылка для Хоум Ассистента")
        return

    try:
        import requests
        url = options["hassio_url"] + "api/services"
        headers = {"Authorization": "Bearer " + options["hassio_key"]}
        res = requests.get(url, headers=headers) # запрашиваем все доступные сервисы
        hassio_services = res.json()
        hassio_scripts = []
        for service in hassio_services: # ищем скрипты среди списка доступных сервисов
            if service["domain"] == "script":
                hassio_scripts = service["services"]
                break

        no_script = True
        for script in hassio_scripts:
            if str(hassio_scripts[script]["name"]) == phrase: # ищем скрипт с подходящим именем
                url = options["hassio_url"] + "api/services/script/" + str(script)
                headers = {"Authorization": "Bearer " + options["hassio_key"]}
                res = requests.post(url, headers=headers) # выполняем скрипт
                script_desc = str(hassio_scripts[script]["description"]) # бонус: ищем что ответить пользователю из описания скрипта
                if "ttsreply(" in script_desc and ")" in script_desc.split("ttsreply(")[1]: # обходимся без re :^)
                    core.play_voice_assistant_speech(script_desc.split("ttsreply(")[1].split(")")[0])
                else: # если в описании ответа нет, выбираем случайный ответ по умолчанию
                    core.play_voice_assistant_speech(options["default_reply"][random.randint(0, len(options["default_reply"]) - 1)])
                no_script = False
                break
        if no_script:
            core.play_voice_assistant_speech("Не могу помочь с этим")

    except:
        import traceback
        traceback.print_exc()
        core.play_voice_assistant_speech("Не получилось выполнить скрипт")
        return
