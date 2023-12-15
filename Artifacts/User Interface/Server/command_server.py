import threading
import time
import socket
import os
import struct
import hashlib
import commands_queue_server as cqs
# from final_Server import send_mode
import subprocess,os
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT1 = 8051
command_state = {
    '0': 'status_check',  # Status Check
    '1': 'start_TCP_connnection',  # Start TCP Connnection
    '2': 'sleep_mode_1',  # Sleep Mode 1
    '3': 'connection_standby',  # Connection Standby
    '4': 'connection_error',  # Connection Error
    '5': 'sleep_mode_2',  # # Sleep Mode 2
    '6': 'terminate_connection',  # Terminate Connection
    '7': 'receive_current_command',  # Send Current command
    '8': 'check_against_checksum',  # Check Against Checksum
    '9': 'send_feedback',  # Send Feedback
    '10': 'verify_error',  # Verify Error
    '11': 'check_with_previous_command_or_mode',  # Check With Previous Command
    '12':'update_command_buffer',  # Update Command Buffer
}

#"blank sample", "po4 standard", "po4 sample", "Restart", "reset cycle", "clear data","flush","refresh data"
commands=["101","102","103","104","105","106","107","108"]
#Automatic, Pause, Full Manual
modes=["1","2","3"]

connection={
    "0":"Off",
    "1":"On"
}

send_mode={
    "0":"passive",
    "1":"active"
}

command_buffer=[]
# command={
#     "0":"restart",
#     "1":"flush",
#     "2":"refresh_data",
#     "3":"send_command",
#     "4":"clear_data"
# }

s = None
conn = None

con_error = 3
connection_Error = ""
command_receive_error=""
command_received=""
command_with_checksum = ""
# value_error = 10
verify_error = 10

command_status={
    "0":"empty",
    "1":"idle",
    "2":"current_command"
}

current_state = '0'
next_state = '1'

status = '2'
# send_command_mode='1'

def calculate_checksum(data):
    sha1 = hashlib.sha1()
    sha1.update(data)
    return sha1.digest()

def connect():
    try:
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s2.bind((HOST, PORT1))
        s2.listen()

        try:
            conn, addr = s2.accept()
            if conn:
                print('Connected by', addr)
                # while True:
                #  data = conn.recv(1024).decode('utf-8')
                print("Connection establised")
                return s2, conn
            print("Server Started waiting for client to connect")
        except OSError as e:
            # Add error in log file
            print("Command connection error")
    except OSError as e:
        print("OS Error : ", str(e))

    return False, False

def my_server_command():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s1:
            s1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            s1.bind(("", PORT1))
            s1.listen(5)
            while 1:
                conn, addr = s1.accept()
                with conn:
                    cmd = conn.recv(1024).decode()
                    print(cmd)
                    data = "Ok".encode()
                    conn.send(data)
                    if cmd == "restart":
                        print("Restart Command Called")
                    elif cmd == "flush":
                        print("Flush command called")
    except OSError as e:
        print("command function error : ", str(e))

def send_feedback(value):
    global s,conn
    try:
        print('Receiving Feedback')
        if struct.unpack('>I', conn.recv(4))[0] == value:
            print("Feedback Received")
            conn.send(struct.pack('>I', value))
            print("Feedback Sent")
            return True
        else:
            print("Feedback Received")
            conn.send(struct.pack('>I', value))
            print("Feedback Sent")
            return False
    except Exception as e:
        print(e)
        print("Error Sending command")
        return 2

def run_script_for_sending_data():
    f = str(os.getcwd()) + '\\final_server.py'
    subprocess.run(['python', f])
    
def start_cycle_2():
    
    global status
    # global value_error
    # global free_error
    global verify_error
    global con_error
    # global cycle_2_status
    global s,conn
    global current_state
    global next_state
    global command_received
    global command_with_checksum
    global command_receive_error

    while 1:
        try:
            # state 0       
            if command_state[current_state]=='status_check':  # 0
                print()
                print("Current State : " + current_state + " : Device network status check")
                time.sleep(3)
                if command_status[status]=="ideal":
                    next_state = '2'
                elif command_status[status]=="current_command":
                    # (CS,NS)=(1,3)
                    next_state = '1'
            
            # state 1
            elif command_state[current_state]=='start_TCP_connnection':  # 1
                print()
                print("Current State : " + current_state + " : Accepting TCP connection from Host")
                time.sleep(3)
                if not s :
                    time.sleep(6)
                    try:
                        s, conn = connect()
                        if s and conn:
                            next_state='3'
                        else:
                            connection_Error="Error While opening connection on port"
                            next_state='4'
                    except Exception as e: 
                        connection_Error = e
                        next_state='4'
                else:
                    print()
                    print("Warning : "  + current_state + " : Connection is already open")
                    time.sleep(3)
                    next_state='3'
                if con_error <= 0:
                    con_error=3
                    status='1'
                    next_state='0'

            # state 2
            elif command_state[current_state]=='sleep_mode_1':  # 2
                print()
                print("Current State : " + current_state + " : Into sleep state 1")
                time.sleep(3)
                print("Going for 600 seconds sleep")
                
                time.sleep(600)
                # (CS,NS)=(0,1)
                # cycle_2_status["command_sent"]=False
                if cqs.get_command():status='2'
                else:
                    print("Current State : " + current_state + " : " + "No Command in Buffer")
                    time.sleep(3)
                    status = '1'
                next_state='0'          

            # state 3
            elif command_state[current_state]=='connection_standby':  # 3
                print()
                print("Current State : " + current_state + " : " + "Into connection Stand By Mode")
                time.sleep(3)
                if command_status[status] == 'current_command':
                    next_state='7'
                elif command_status[status] == 'empty':
                    next_state='5'
                # elif command_status[status] == 'empty' and send_mode[send_command_mode] == 'passive':
                #     next_state='6'

            # state 4
            elif command_state[current_state]=='connection_error':  # 4
                con_error -= 1
                print()
                print("Current State : " + current_state + " : " + connection_Error)
                time.sleep(3)
                print("Recording error in file : ",connection_Error)
                next_state='1'
            
            # state 5
            elif command_state[current_state]=='sleep_mode_2': #5
                print()
                print("Current State : " + current_state + " : Into sleep mode 2")
                time.sleep(3)
                print("Going for 60 seconds sleep")
                time.sleep(6)
                # (CS,NS)=(0,1)
                # cycle_2_status["command_sent"]=False
                
                # Check if connection is going to close or not
                if send_feedback(1):
                    s.close()
                    s = None
                    next_state = '0'
                    status = '2'
                else:
                    print("Connection is still going to be eshtablished")
                    
                    #check if there is command in buffer
                    if send_feedback(1):
                        status='2'
                        next_state='3'
                    else:
                        print("No Command in Buffer")
                        time.sleep(3)
                        status = '1'
            
            # state 6
            elif command_state[current_state]=='terminate_connection': #6
                print()
                print("Current State : " + current_state + " : Connection Terminate")
                time.sleep(3)
                try:
                    s.close()
                    status='1'
                    next_state='0'
                    print("Terminated the connection")
                except:
                    print("Current State : " + current_state + " : " +"Error while terminating the connection")
                    next_state='0'

            # state 7
            elif command_state[current_state]=='receive_current_command': #7
                try : 
                    print()
                    print("Current State : " + current_state + " : " + "Receiving Current Command")

                    # Receive confirmation for receiving command
                    if send_feedback(1):
                        # print(s)
                        command_with_checksum = conn.recv(2048)
                        time.sleep(5)

                        byte_size = len(command_with_checksum)
                        print(f"Byte size of text: {byte_size} bytes")

                        command_with_checksum = command_with_checksum.decode()
                        next_state = '8'
                    else:
                        print("There are no commands in buffer to receive from client")
                        status='0'
                        next_state='3'
                except Exception as e:
                    print("Error : ",e)
                    time.sleep(3)
                    continue

            # state 8
            elif command_state[current_state]=='check_against_checksum':  #8
                print()
                print("Current State : " + current_state + " : " +"checking against checksum")
                try: 
                    print(command_with_checksum.split('b\''))
                    command_received,checksum_received=command_with_checksum.split('nalim')
                    checksum_calculated = calculate_checksum(command_received.encode())

                    if checksum_received == str(checksum_calculated):
                        print("Checksum verified, Command transmitted correctly")
                        next_state='9'
                    else:
                        command_send_error="Could not verify checkcum, Error in command transmission"
                        next_state='10'
                    time.sleep(5)

                except Exception as e:
                    command_send_error=e
                    next_state='10'

            # state 9
            elif command_state[current_state]=='send_feedback':  #9
                print()
                print("Current State : " + current_state + ": Send feedback for command received")
                time.sleep(3)
                while verify_error > 0:
                    try:
                        if send_feedback(1):
                            # cycle_1_status["data_received"] = True
                            next_state = '11'
                            break
                        else:
                            verify_error -= 1
                    except OSError as e:
                        print("Error : ", str(e))
                        verify_error -= 1
                    # record error
                if verify_error <= 0:
                    next_state = '11'
            
            # state 10
            elif command_state[current_state]=='verify_error':  #10
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

            # state 11
            elif command_state[current_state]== 'check_with_previous_command_or_mode': #11
                if command_received in modes: 
                    print("Current State : " + current_state + ": checking with previous mode " )
                    print("")
                    if cqs.get_current_mode() == command_received :
                        next_state='3'
                    else:
                        next_state='12'
                elif command_received in commands:
                    if command_received == "108":
                        run_script_for_sending_data()
                        print("Successfully transfered the data")
                    if cqs.get_command() == command_received :
                        next_state='3'
                    else:
                        next_state='12'
                elif command_received[0:5] == "picmd":
                    print("Current State : " + current_state + ": It's new command to run on linux terminal" )
                    command_received = command_received[5:]
                    next_state='12'
                elif command_received == '5':
                    print("Current State : " + current_state + ": Command for moving to next sample run" )
                    next_state='12'
                    print("")
                else:
                    print("Wrong mode or command")
                    next_state='3'
                if send_feedback(1):
                    status='2'
                else:
                    status='0'
            
            # state 12
            elif command_state[current_state] == 'update_command_buffer': #12
                
                if command_received in modes:
                    print("Current State : " + current_state + ": Updating mode " )
                    cqs.change_mode(command_received)
                elif command_received in commands:
                    if not command_received == "108":
                        print("Current State : " + current_state + ": Updating command " )
                        cqs.add_command(command_received)
                elif command_received == "5":
                    print("Current State : " + current_state + ": Updating next button clicked")
                    print(cqs.add_next_button_clicked(command_received))
                else:
                    print("Current State : " + current_state + ": Updating full command " )
                    cqs.add_full_command(command_received)
                    
                next_state='3'
            current_state = next_state
        
        except Exception as e:
            print("Current State : " + current_state + " : " + e)
            #Save the error 
            s.close()
            s = None
            next_state = '0'
            status = '2'

if __name__ == '__main__':
    # print(type(calculate_checksum("send_data".encode())))
    t2 = threading.Thread(target=start_cycle_2, name='commmand')

    # starting threads
    t2.start()

    # wait until all threads finish
    t2.join()

