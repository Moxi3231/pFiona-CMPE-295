import json
import os
from pathlib import Path
file_path = str(os.getcwd()) + '\JSON\commands.json'

#"blank sample", "po4 standard", "po4 sample", "Restart", "reset cycle", "clear data","flush","refresh data"
commands=["101","102","103","104","105","106","107","108"]
#Automatic, Pause, Full Manual
modes=["1","2","3"]

def update_json(newData):

    file = open(file_path, 'w')
    json.dump(newData, file)
    file.close()
    return True

def add_command(command):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        if command in modes:
            print("Changing the mode")
            data["mode"] = command
        elif command in commands:
            print("Adding comamand to the Queue,")
            data["commands"]=command
        else: return False

        return update_json(data)
    
    except Exception as e:
        print(e)
        return False

def get_next_command_and_mode():
    try: 
        with open(file_path, 'r') as f:
            data = json.load(f)
        if (not data["mode"] == data["last_mode"]) and data["mode"]:
            return data["mode"]
        elif data["commands"]:
            return data["commands"]
        else :return False
    except Exception as e:
        print(e)
        return False

def remove_command():
    print("into remove comand")
    try: 
        with open(file_path, 'r') as f:
            data = json.load(f)
        if data["commands"]:
            data["commands"]=""
            return update_json(data)
        else:
            return False
    except Exception as e:
        print(e)
        return False
    
def remove_mode():
    with open(file_path, 'r') as f:
        data = json.load(f)
    try:
        data["mode"]=""
        return update_json(data)
    except:
        return False
    
def update_last_mode(mode):
    with open(file_path, 'r') as f:
        data = json.load(f)
    try: 
        if mode in modes:
            data["last_mode"]=mode
            return update_json(data)
        else:return False
    except: return False

def get_command():
    with open(file_path, 'r') as f:
        data = json.load(f)
    if data["commands"] :
        return data["commands"]
    elif data["mode"]:
        return data["mode"]
    else: return False

def change_mode(mode):
    with open(file_path, 'r') as f:
        data = json.load(f)
    try:
        if mode in modes:
            print("Changing the mode")
            data["mode"]=mode
            return update_json(data)
        else:return False
    except:
        return False
    
def get_mode():
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data["mode"]

def get_last_mode():
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data["last_mode"]