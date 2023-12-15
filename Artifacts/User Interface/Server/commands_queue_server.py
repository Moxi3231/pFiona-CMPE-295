import json
import os
from pathlib import Path

file_path = str(os.path.dirname(os.getcwd())) + '\JSON\server_command.json'
def update_json(newData):
    file = open(file_path, 'w')
    json.dump(newData, file)
    file.close()
    return True

def add_next_button_clicked(command):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        data["next_button_clicked"]=command
    else:
        print("The file does not exist. : ",file_path)
        return False
    return update_json(data)

def is_next_button_clicked(file=None):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        if data["next_button_clicked"]:
            return data["next_button_clicked"]
        else :return False
    else:
        if os.path.exists(file):
            with open(file, 'r') as f:
                data = json.load(f)
            if data["next_button_clicked"]:
                return data["next_button_clicked"]
            else :return False
    print("The file does not exist. : ",file_path)

def remove_next_button_clicked(file=None):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        if data["next_button_clicked"]:
            data["next_button_clicked"]=""
            return update_json(data)
        else:
            return False
    else:
        if os.path.exists(file):
            with open(file, 'r') as f:
                data = json.load(f)
            if data["next_button_clicked"]:
                data["next_button_clicked"]=""
                return update_json(data)
            else:
                return False
    print("The file does not exist. : ",file_path)
    return False

def add_full_command(command):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        data["full_command"]=command
    else:
        print("The file does not exist. : ",file_path)
        return False

    return update_json(data)

def add_command(command):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        data["commands"]=command
    else:
        print("The file does not exist. : ",file_path)
        return False

    return update_json(data)

def change_mode(command):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        data["current_mode"]=command
    else:
        print("The file does not exist. : ",file_path)
        return False
    return update_json(data)

def get_command(file=None):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        if data["commands"]:
            return data["commands"]
        else :return False
    else:
        if os.path.exists(file):
            with open(file, 'r') as f:
                data = json.load(f)
            if data["commands"]:
                return data["commands"]
            else :return False
    print("The file does not exist. : ",file_path)
    return False

# def get_last_command():
#     with open(file_path, 'r') as f:
#         data = json.load(f)
#     if data["commands"]:
#         return data["commands"]
#     else :return False

def get_current_mode(file=None):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        if data["current_mode"]:
            return data["current_mode"]
        else :return False
    else:
        if os.path.exists(file):
            with open(file, 'r') as f:
                data = json.load(f)
            if data["current_mode"]:
                return data["current_mode"]
            else :return False
    print("The file does not exist. : ",file_path)
    return False


def remove_command(file=None):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        if data["commands"]:
            data["commands"]=""
            return update_json(data)
        else:
            return False
    else:
        if os.path.exists(file):
            with open(file, 'r') as f:
                data = json.load(f)
            if data["commands"]:
                data["commands"]=""
                return update_json(data)
            else:
                return False
    print("The file does not exist. : ",file_path)
    return False

# def get_all_commands():
#     with open(file_path, 'r') as f:
#         data = json.load(f)
#     if data["commands"]:
#         return data["commands"]
#     else: return False
