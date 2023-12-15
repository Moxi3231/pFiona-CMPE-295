import json
import os
from pathlib import Path
file_path = str(os.getcwd()) + '\JSON\commands.json'

#"blank sample", "po4 standard", "po4 sample", "Restart", "reset cycle", "clear data","flush","refresh data"
commands=["101","102","103","104","105","106","107","108"]
#Automatic, Pause, Full Manual
modes=["1","2","3","4","5"]

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
        print(data)
        return update_json(data)
    
    except Exception as e:
        print(e)
        return False

def add_all_sam_count(v):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        data["all_sample_cout"] = v
        return update_json(data)
    except Exception as e:
        print(e)
        return False
    
def add_full_command(command):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            data["full_command"]=command
            return update_json(data)
        else:
            print("The file does not exist. : ",file_path)
            return False
    except Exception as e:
        print(e)
        return False

def add_next_sample(command):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            data["next_button_clicked"]=command
            return update_json(data)
        else:
            print("The file does not exist. : ",file_path)
            return False
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
        elif data["full_command"]:
            return data["full_command"]
        elif data["next_button_clicked"]:
            return data["next_button_clicked"]
        else :return False
    except Exception as e:
        print(e)
        return False

def remove_next_button_clicked():
    try: 
        with open(file_path, 'r') as f:
            data = json.load(f)
        if data["next_button_clicked"]:
            data["next_button_clicked"]=""
            return update_json(data)
        else:
            return False
    except Exception as e:
        print(e)
        return False

def remove_command():
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
    
def remove_next__command():
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

def remove_full_command():
    with open(file_path, 'r') as f:
        data = json.load(f)
    try:
        data["full_command"]=""
        return update_json(data)
    except:
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
        print("Updating the mode")
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
    elif data["full_command"]:
        return data["full_command"]
    elif data["next_button_clicked"]:
        return data["next_button_clicked"]
    else: return False

def change_mode(mode):
    with open(file_path, 'r') as f:
        data = json.load(f)
    try:
        if not data["last_mode"] == mode:
            data["last_mode"]=data["mode"]
            if mode in modes:
                print("Changing the mode")
                data["mode"]=mode
                return update_json(data)
            else:return False
        else: return False
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

def reset_connection_varibles():
    with open(file_path, 'r') as f:
        data = json.load(f)

    data["connection_closed"] = 0
    data["script_locked"] = 0

    return update_json(data)

def change_connection_closed(l):
    with open(file_path, 'r') as f:
        data = json.load(f)
    try:
        data["connection_closed"]=l
        return update_json(data)
    except:
        return False
    
def is_connection_closed():
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data["connection_closed"]

def change_lock_on_script(l):
    with open(file_path, 'r') as f:
        data = json.load(f)
    try:
        data["script_locked"]=l
        return update_json(data)
    except:
        return False

def is_script_locked():
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data["script_locked"]
    
def get_whole_file():
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data