from django.http import HttpResponse
from django.shortcuts import render
from . import decode
from django.http import JsonResponse
from . import commands_queue
import sys
import subprocess,os
import json
import win32con
import win32file 



mode = ["1","2","3","4","5"]
#"blank sample", "po4 standard", "po4 sample", "Restart", "reset cycle", "clear data","flush","refresh data"
command_list=["101","102","103","104","105","106","107","108"]

data={"message":"","success":False}

device_info=["PI1"]
   
def is_client_script_running():
    try:
        #Aqquire lock for client file
        return commands_queue.is_script_locked()
        
    except Exception as e:
        print(str(e))
        return True  # Failed to acquire lock, meaning the script is already running

def run_new_client_script():
    # Run the new script
    # subprocess.run(['python', client_script_path])
    f = str(os.getcwd()) + '\\api\command_client.py'
    subprocess.run(['python', f])

def start_running_client_script():
    # Check if the script is already running
    if not is_client_script_running():
        try:
            # Run the new script
            print("Running New Client Script")
            run_new_client_script()
            print("Virag Testing")
        except Exception as e :
            print(str(e))
        return True
    else:
        print("The script is already running.")
        return False
        
def graphs(request):
    data=decode.file_read(["PI1"])
    return JsonResponse(data)

def verify_and_add_command(cmd):

    if cmd in command_list:
        # print("command is in command list. However, it will only be added if queue is free")    
        if commands_queue.add_command(cmd):
            # print("Command is added succeessfully in the buffer")
            # print("Success", "Command is added succeessfully into the buffer")
            data["message"]="Command is added succeessfully into the buffer"
            return JsonResponse(data)
        else:
            # print("Error", "There is alredy command in queue, free queue to send new command")
            data["message"]="There is alredy command in queue, free queue to send new command"
            # print("There is alredy command in queue, free queue to send new command")
            return JsonResponse(data)
    else:
        # print("Command is not in command list")
        # print("Error", "Command is not in command list")
        data["message"]="Command is not in command list"
        return JsonResponse(data)

def send_command(text):
    if type(text) == str :pass
    else: text = text.get('1.0', 'end')
    if text.strip():
        return verify_and_add_command(text.strip())

def free_command_queue(request):
    if commands_queue.remove_command():
            data["message"]="Command is removed succeessfully from the buffer"
            return JsonResponse(data)
    else:
        data["message"]="No command in the buffer to remove"
        print('returning data')
        print(data)
        return JsonResponse(data)
    
def add_command(request):
    variable = request.GET.get('variable')
    if commands_queue.get_mode() == "" and commands_queue.get_last_mode() == "3":
        data = send_command(variable)
    else:
        data={}
        data["message"]="Please change mode from Automatic to manual mode and press reset cycle button and then send instruction to PI"
        return JsonResponse(data)
    return data

def sample_count_change(request):
    variable = request.GET.get('variable')
    data={}
    if commands_queue.add_all_sam_count(variable):
        # print("Command is added succeessfully in the buffer")
        # print("Success", "Command is added succeessfully into the buffer")
        data["message"]="All samaple count are added succeessfully into the buffer"
        return JsonResponse(data)
    else:
        # print("Error", "There is alredy command in queue, free queue to send new command")
        data["message"]="All samaple count are not added, Please add back later"
        # print("There is alredy command in queue, free queue to send new command")
        return JsonResponse(data)
    
def add_full_command(request):
    variable = request.GET.get('variable')
    data={}
    if commands_queue.get_mode() == "" and commands_queue.get_last_mode() == "5":
        if commands_queue.add_full_command(variable):
            # print("Command is added succeessfully in the buffer")
            # print("Success", "Command is added succeessfully into the buffer")
            data["message"]="Command is added succeessfully into the buffer"
            return JsonResponse(data)
        else:
            # print("Error", "There is alredy command in queue, free queue to send new command")
            data["message"]="There is alredy command in queue, free queue to send new command"
            # print("There is alredy command in queue, free queue to send new command")
            return JsonResponse(data)
    else:
        data["message"]="Please change mode from Automatic to manual mode and press reset cycle button and then send instruction to PI"
        return JsonResponse(data)
    return data

def next_sample(request):
    variable = request.GET.get('variable')
    data={}
    if commands_queue.get_mode() == "" and commands_queue.get_last_mode() == "3":
        if commands_queue.add_next_sample(variable):
            # print("Command is added succeessfully in the buffer")
            # print("Success", "Command is added succeessfully into the buffer")
            data["message"]="Request to move to Next Sample is added succeessfully into the buffer"
            return JsonResponse(data)
        else:
            # print("Error", "There is alredy command in queue, free queue to send new command")
            data["message"]="There is alredy next sample in queue"
            # print("There is alredy command in queue, free queue to send new command")
            return JsonResponse(data)
    else:
        data["message"]="Please change mode from Automatic to full manual mode and then send instruction to PI"
        return JsonResponse(data)
    return data

def start_conection(request):
    variable = request.GET.get('variable')
    data = {}
    print(variable)
    if variable == '1001':
        flag = start_running_client_script()
        
        if flag:
            data["message"]="Connection closed successfully"
        else:
            data["message"]="Connection already eshtablised"
        
        return JsonResponse(data)

def stop_connection(request):
    variable = request.GET.get('variable')
    if variable == '1002':
        commands_queue.change_connection_closed(0)
        data["message"]="Connecation termination request updated successfully"
        return JsonResponse(data)

def get_udates(request):
    return JsonResponse(commands_queue.get_whole_file()) 
    
def reset_connection(request):
    try:
        commands_queue.reset_connection_varibles()
        data["message"]="connection reseted successfully now you can start connection with PI"
        return JsonResponse(data)
    except Exception as e:
        print("Error: ",str(e))
        data["message"]="Error while changing reset varibles"
        return JsonResponse(data)

def change_mode(request):
    variable = request.GET.get('variable')
    if variable in mode:
        commands_queue.change_mode(variable)
        
        data["message"]="Mode is added succeessfully into the buffer"
        return JsonResponse(data)
    else:
        data["message"]="Mode is provided is not in the Mode list"
        return JsonResponse(data)


def showdata(request):
    if sys.platform == 'darwin':
        def openFolder():
            try:
                subprocess.check_call(['open', '--', os.getcwd()+"/Device/"+device_info[0]])
            except subprocess.CalledProcessError as e:
                # Handle the error gracefully, or simply ignore it
                print(f"Error/Warning opening folder: {e}")
    elif sys.platform == 'linux2':
        def openFolder():
            try:
                subprocess.check_call(['xdg-open', '--', os.getcwd()+"/Device/"+device_info[0]])
            except subprocess.CalledProcessError as e:
                # Handle the error gracefully, or simply ignore it
                print(f"Error/Warning opening folder: {e}")
    elif sys.platform == 'win32':
        def openFolder():
            try:
                subprocess.check_call(['explorer', os.getcwd()+"\\Device\\"+device_info[0]])
            except subprocess.CalledProcessError as e:
                # Handle the error gracefully, or simply ignore it
                print(f"Error/Warning opening folder: {e}")
    d = openFolder()
    print(d)
    data["message"]="Opened data folder successfully"
    return JsonResponse(data)



