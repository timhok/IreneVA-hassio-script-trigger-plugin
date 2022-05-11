# Триггер скриптов Home Assistant
# author: Timhok

import os
import json
import random
import requests

from vacore import VACore

modname = os.path.basename(__file__)[:-3] # calculating modname
hassio_scripts = []

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

        "commands": hassio_commands(core)
    }
    return manifest

def start_with_options(core:VACore, manifest:dict):
    pass

def hassio_commands(core:VACore):
    global hassio_scripts
    jaaRootFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    jaaOptionsPath = jaaRootFolder+os.path.sep+"options"

    options = {}
    try:
        with open(jaaOptionsPath+'/plugin_hassio_script_trigger.json', 'r', encoding="utf-8") as f:
            s = f.read(10000000)
            f.close()
        options = json.loads(s)
        #print("Saved options", options)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Файл с конфигурацией плагина недоступен")
        return {}

    if options["hassio_url"] == "" or options["hassio_key"] == "":
        core.play_voice_assistant_speech("Нужен ключ или ссылка для Хоум Ассистента")
        return {}

    try:
        commands = []
        url = options["hassio_url"] + "api/services"
        headers = {"Authorization": "Bearer " + options["hassio_key"]}
        res = requests.get(url, headers=headers) # запрашиваем все доступные сервисы
        hassio_services = res.json()
        for service in hassio_services: # ищем скрипты среди списка доступных сервисов
            if service["domain"] == "script":
                hassio_scripts = service["services"]
                for script in hassio_scripts:
                    commands.append(hassio_scripts[script]["name"])
                break

        ret = {}
        for command in commands:
            ret[command] = (hassio_run_script, command)
        return ret

    except:
        import traceback
        traceback.print_exc()
        core.play_voice_assistant_speech("Не получилось получить список команд HomeAssistant")
        return {}

def hassio_run_script(core:VACore, phrase:str, command:str):
    options = core.plugin_options(modname)

    if options["hassio_url"] == "" or options["hassio_key"] == "":
        print(options)
        core.play_voice_assistant_speech("Нужен ключ или ссылка для Хоум Ассистента")
        return

    try:
        for script in hassio_scripts:
            if str(hassio_scripts[script]["name"]) == command: # ищем скрипт с подходящим именем
                url = options["hassio_url"] + "api/services/script/" + str(script)
                headers = {"Authorization": "Bearer " + options["hassio_key"]}
                res = requests.post(url, headers=headers) # выполняем скрипт
                script_desc = str(hassio_scripts[script]["description"]) # бонус: ищем что ответить пользователю из описания скрипта
                if "ttsreply(" in script_desc and ")" in script_desc.split("ttsreply(")[1]: # обходимся без re :^)
                    core.play_voice_assistant_speech(script_desc.split("ttsreply(")[1].split(")")[0])
                else: # если в описании ответа нет, выбираем случайный ответ по умолчанию
                    core.play_voice_assistant_speech(options["default_reply"][random.randint(0, len(options["default_reply"]) - 1)])
                break

    except:
        import traceback
        traceback.print_exc()
        core.play_voice_assistant_speech("Не получилось выполнить скрипт")
        return
