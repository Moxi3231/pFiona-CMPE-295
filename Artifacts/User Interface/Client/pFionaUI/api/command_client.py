import threading
import time
import socket
import os,subprocess
import struct
import commands_queue as commands_queue 
import hashlib

Device = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 8051

command_state = {
    '0': 'status_check',  # Status Check
    '1': 'start_TCP_connnection',  # Start TCP Connnection
    '2': 'sleep_mode_1',  # Sleep Mode 1
    '3': 'connection_standby',  # Connection Standby
    '4': 'connection_error',  # Connection Error
    '5': 'sleep_mode_2',  # # Sleep Mode 2
    '6': 'terminate_connection',  # Terminate Connection
    '7': 'send_current_command',  # Send Current command
    '8': 'verify_error',  # Verify Error
    '9': 'wait_for_feedback',  # Wait For Feedback
    '10': 'remove_current_command_or_mode',  # Remove Current Command
    '11':'command_buffer_check',  # Command Buffer check
}

devices = {
    "PI1": ["PI1", "127.0.0.1", "8091", ["status", 0]],
    "PI2": ["PI1", "192.168.5.1", "8080", ["status", 0]],
    "PI3": ["PI1", "192.168.5.1", "8080", ["status", 0]]
}

connection={
    "0":"Off",
    "1":"On"
}

send_mode={
    "0":"passive",
    "1":"active"
}


# command={
#     "0":"restart",
#     "1":"flush",
#     "2":"refresh_data",
#     "3":"send_command",
#     "4":"clear_data"
# }

con_error = 3
connection_Error = ""
command_send_error = ""
verify_error = 10

command_status={
    "0":"empty",
    "1":"idle",
    "2":"current_command"
}

current_state = '0'
next_state = '1'

status = '2'
send_command_mode='1'

s = None

cycle_2_status = {"command_received": False}

def calculate_checksum(data):
    sha1 = hashlib.sha1()
    sha1.update(data)
    return sha1.digest()

def creat_new_folder(p, d):
    # Path
    path = os.path.join(p, d)
    try:
        return os.mkdir(path)
    except:
        return False

def send_command(cmd):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect(("192.168.5.1", 8080))
            s.send(cmd.encode())
            data = s.recv(1024)
            data = data.decode('utf-8')
            print(data)
        except OSError as e:
            print("send command error : ", str(e))
        except socket.error:
            print(socket.error)

def connect(device_info):
    try:
        sok = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sok.connect((Device, PORT))
        # print('connect:', sok)
        return sok
    except socket.error:
        dir_path = os.path.join(os.getcwd(), "Device/", device_info[0], "")
        # print(dir_path)
        try:
            # print(os.path.join(dir_path, 'connection/com.txt'))
            f = open(os.path.join(dir_path, 'connection/com.txt'), 'a')
        except:
            creat_new_folder(dir_path, '/connection/')
            f = open(os.path.join(dir_path,'/connection/com.txt'), 'a')

        # record socket.error
        f.write("\n")
        print("socket error: " + str(socket.error))
        f.write(str(socket.error))
        f.write("\n")
        f.write("\n")
        return False

def receive_feedback(value):
    try:
        print("Seding Feedback")
        s.send(struct.pack('>I', value))
        print("Feedback Sent")
        print('Receiving Feedback')
        if struct.unpack('>I', s.recv(4))[0] == value:
            print("Feedback Received")
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def run_script_for_receiving_data():
    f = str(os.getcwd()) + '\\api\client.py'
    subprocess.run(['python', f])

def start_cycle_2(device):
    
    global status
    # global value_error
    # global free_error
    global verify_error
    global con_error
    global cycle_2_status
    global s
    global current_state
    global next_state
    global command_send_error

    while 1:
        try: 
            # state 0
            if command_state[current_state]=='status_check':  # 0
                print()
                print("Cuurent State : " + current_state + ": Host network status check")
                time.sleep(3)
                if command_status[status]=="idle":
                    next_state='2'
                elif command_status[status]=="current_command":
                    next_state='1'

            # state 1 
            elif command_state[current_state]=='start_TCP_connnection':  # 1
                print()
                print("Cuurent State : " + current_state + ": Start TCP connection")
                time.sleep(3)
                if not s :
                    try:
                        s = connect(device)
                        if s:
                            commands_queue.change_connection_closed(1)
                            commands_queue.change_lock_on_script(1)
                            next_state='3'
                        else:
                            connection_Error="Error while connecting to Server"
                            next_state='4'  
                    except Exception as e: 
                        connection_Error = e
                        next_state='4'
                else:
                    connection_Error="Port is alredy connected, going for next stage"
                    next_state='3'
                    continue

                if con_error <= 0:
                    con_error=3
                    status='1'
                    next_state='0'

            # state 2
            elif command_state[current_state]=='sleep_mode_1':  # 2
                print()
                print("Current State : " + current_state + ": Into sleep mode 1")
                time.sleep(3)
                print("Going for 600 seconds sleep")
                time.sleep(600)
                # (CS,NS)=(0,1)
                # cycle_2_status["command_sent"]=False
                if commands_queue.get_command():status='2'
                else:
                    print("Current State : " + current_state + ":" + "No Command in Buffer")
                    time.sleep(3)
                    status = '1'
                next_state='0'         

            # state 3
            elif command_state[current_state]=='connection_standby':  # 3
                print()
                print("Current State : " + current_state + ":" + "Into connection Stand By Mode")
                time.sleep(3)
                
                if command_status[status] == 'current_command':
                    next_state='7'
                elif command_status[status] == 'empty' and send_mode[send_command_mode] == 'active':
                    next_state='5'
                elif command_status[status] == 'empty' and send_mode[send_command_mode] == 'passive':
                    next_state='6'

            # state 4
            elif command_state[current_state]=='connection_error':  # 4
                con_error -= 1
                print()
                print("Current State : " + current_state + " : Error : " + str(connection_Error))
                time.sleep(3)
                print("Recording error in file : ",connection_Error)
                next_state='1'
            
            # state 5
            elif command_state[current_state]=='sleep_mode_2': #5
                print()
                print("Current State : " + current_state + ": Into sleep mode 2")
                time.sleep(3)
                print("Going for 60 seconds sleep")
                time.sleep(6)

                if not commands_queue.is_connection_closed():

                    receive_feedback(1)

                    s.close()
                    commands_queue.change_lock_on_script(0)
                    print("Connection SuccessFully closed")
                    break
                else:
                    receive_feedback(0)
                    print("Connection is still going to be established")
                # (CS,NS)=(0,1)
                # cycle_2_status["command_sent"]=False
                if commands_queue.get_command():
                    receive_feedback(1)
                    status='2'
                    next_state='3'
                else:
                    receive_feedback(0)
                    print("No Command in Buffer")
                    status = '1'
                    

            # state 6
            elif command_state[current_state]=='terminate_connection': #6
                print()
                print("Current State : " + current_state + ": Connection Terminate")
                time.sleep(3)
                try:
                    s.close()
                    status='1'
                    next_state='0'
                    print("Terminated the connection")
                except Exception as e:
                    print("Current State : " + current_state + " : " + e)
                    next_state='0'

            # state 7
            elif command_state[current_state]=='send_current_command':  #7
                print()
                print("Current State : " + current_state + " : " +"Sending Command")
                try :
                    # s.send(struct.pack('>I', len('0')))
        
                    next_command=commands_queue.get_next_command_and_mode()
                    if next_command:
                        receive_feedback(1)
                    else:
                        receive_feedback(0)

                    if next_command:
                        checksum = calculate_checksum(next_command.encode())
                        command_with_checksum = next_command+ "nalim" + str(checksum)
                    
                        byte_size = len(command_with_checksum.encode())
                        print(f"Byte size of text: {byte_size} bytes")

                        s.sendall(command_with_checksum.encode())
                        next_state='9'
                        time.sleep(10)
                    else : 
                        print("There is no command in buffer. So, going back to stand by mode")
                        status='0'
                        next_state='3'
                except Exception as e:
                    command_send_error = e
                    next_state = '8'

            # state 8
            elif command_state[current_state]=='verify_error': #8
                print("Current State : " + current_state + " : Verify Error : " + str(command_send_error))
                if verify_error>0:
                    verify_error-=1
                    time.sleep(3)
                    print("Recording error in file : ",str(command_send_error))
                    next_state='7'
                else:
                    time.sleep(3)
                    print("Terminating the connection due to continuous error")
                    next_state='6'
            
            # state 9
            elif command_state[current_state]=='wait_for_feedback':  #9
                print()
                print("Current State : " + current_state + " : " +"Waiting For Feedback")
                try:
                    if receive_feedback(1):
                        next_state = '10'
                    else:
                        print("Not able to receive feedback from server")
                        next_state = '8'
                except OSError as e:
                    next_state = '8'
                    command_send_error = e
                    print()
                time.sleep(10)

            # state 10
            elif command_state[current_state]=='remove_current_command_or_mode': #10
                
                t = commands_queue.get_next_command_and_mode()
                if t:
                    if t in commands_queue.modes: 
                        print("Current State : " + current_state + " : " +"Changing last mode")
                        if commands_queue.update_last_mode(t):
                            commands_queue.remove_mode()
                            print("Lats mode changed successfully and current mode set to null")
                        else:
                            print("Last Mode not chnaged for some reason")
                    elif t in commands_queue.commands:
                        if t == "108":
                            run_script_for_receiving_data()
                        print("Current State : " + current_state + " : " +"Removing command from buffer")

                        if commands_queue.remove_command():
                            print("Command removed successfully")
                        else:
                            print("Command not removed for some reason")
                    elif t == "5":
                        if commands_queue.remove_next_button_clicked():
                            print("next_button_clicked removed successfully")
                        else:
                            print("Command not removed for some reason")
                    elif t[0:5] == "picmd":
                        commands_queue.remove_full_command()
                else:
                    print("No commands to remove here")
                print()
                next_state="11"

            # state 11
            elif command_state[current_state]=='command_buffer_check': #11
                print("Current State : " + current_state + " : " +"Command buffer check")
                if commands_queue.get_command():
                    print("There is a command in buffer")
                    receive_feedback(1)
                    status='2'
                else:
                    print("There is no command in buffer")
                    receive_feedback(0)
                    status='0'
                next_state = '3'

            current_state = next_state
        except Exception as e:
            print("Current State : " + current_state + " : " + e)
            #Save the error 

if __name__ == '__main__':
    # print(type(calculate_checksum("send_data".encode())))
    t2 = threading.Thread(target=start_cycle_2(devices["PI1"]), name='command')

    # starting threads
    t2.start()

    # wait until all threads finish
    t2.join()

