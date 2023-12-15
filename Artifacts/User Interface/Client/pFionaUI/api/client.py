from copyreg import pickle
# from curses.ascii import NUL
import socket
import threading
import time
import json
from warnings import catch_warnings
from datetime import date
import struct
import os
import zlib
import sys
from pathlib import Path
import datetime

# import seaborn as sns

# Device = '10.251.188.57'  # The server's hostname or IP address
devices = {
    "PI1": ["PI1", "127.0.0.1", "8091", ["status", 0]],
    "PI2": ["PI1", "192.168.5.1", "8080", ["status", 0]],
    "PI3": ["PI1", "192.168.5.1", "8080", ["status", 0]]
}

host_request_data = 1

Device = '127.0.0.1'  # set ip accordingly
PORT = 8057  # The port used by the server
con_error = 3
value_error = 10
verify_error = 10
connection_Error = ""

s = None
conn = None
last_received_filename = ""

current_state = '0'
next_state = '1'

# thread_status='1'
receive_data_mode = '1'  #
status = '2'

data_receive_status = {"data_files": "0", "log_files": "0"}

# cycle_1_status = {"0":"data_received", "1":"data_collecting"}

receive_mode = {
    "0": "passive",
    "1": "active"
}

data_status = {
    "1": "idle",
    "2": "collect_data",
    "3": "data_received"
}

data_state = {
    '0': 'status_check',
    '1': 'start_TCP_connection',
    '2': 'sleep_mode_1',
    '3': 'connection_standby',
    '4': 'receiving_data',
    '5': 'connection_error',
    '6': 'send_feedback',
    '7': 'verification_error',
    '8': 'terminate_connection',
    '9': 'sleep_mode_2',
    '10': 'check_data_space',
    '11': 'verification_error'
}

BUFFER_SIZE = 8192


def get_crc32(path):
    with open(path, 'rb') as f:
        crc = 0
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            crc = zlib.crc32(data, crc)
    return crc

def record_verify_error():
    # write into new log files
    pass

def send_command():
    pass

def creat_new_folder(p, d):
    # Path
    path = os.path.join(p, d)
    try:
        return os.mkdir(path)
    except:
        return False

def send_feedback(value):
    global s
    try:
        print('Receiving Feedback')
        if struct.unpack('>I', s.recv(4))[0] == value:
            print("Feedback Received")
            s.send(struct.pack('>I', value))
            print("Feedback Sent")
            return True
        else:
            return False
    except Exception as e:
        print(e)
        print("Error Sending command")
        return False

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
            f = open(os.path.join(dir_path, 'connection/com.txt'))
        except:
            try:
                creat_new_folder(dir_path, 'connection/')
            except:
                try:
                    f = open(os.path.join(dir_path, 'connection/com.txt'), "a")
                except:
                    f = open(os.path.join(dir_path, 'connection/com.txt'), "x")

        # record socket.error
        f.write("\n")
        print("socket error: " + str(socket.error))
        f.write(str(socket.error))
        f.write("\n")
        f.write("\n")
        return False

def get_last_data_file_name(device):
    t = "Device/" + device + "/data/"
    data_date_dir_path = os.path.join(os.getcwd(), t)
    data_date_dir_list = os.listdir(data_date_dir_path)
    data_date_dir_list = sorted(data_date_dir_list)

    # remove .DS_Store from list date list
    try:
        data_date_dir_list.remove(".DS_Store")
    except:
        pass

    if data_date_dir_list:
        last_data_received_date = data_date_dir_list[-1]
        dir_path = os.path.join(os.getcwd(), "Device/", device, "")
        dir_path = os.path.join(dir_path, 'data/{}'.format(last_data_received_date))
        while len(os.listdir(dir_path)) == 0:
            data_date_dir_list = data_date_dir_list[:-1]
            last_data_received_date = sorted(data_date_dir_list)[-1]
            dir_path = os.path.join(os.getcwd(), "Device/", device, "")
            dir_path = os.path.join(dir_path, 'data/{}'.format(last_data_received_date))

        data_file_list = os.listdir(dir_path)

        try:
            data_file_list.remove(".DS_Store")
        except:
            pass

        data_file_list = sorted(data_file_list)
    else:
        data_file_list = ["2022-02-02_02-02-02.txt"]
    return data_file_list[-1] if len(data_file_list) > 0 else 'N/A'

def get_last_log_file_name(device):
    t = "Device/" + device + "/logs/"
    data_date_dir_path = os.path.join(os.getcwd(), t)
    data_date_dir_list = os.listdir(data_date_dir_path)
    data_date_dir_list = sorted(data_date_dir_list)

    # remove .DS_Store from list date list
    try:
        data_date_dir_list.remove(".DS_Store")
    except:
        pass

    if data_date_dir_list:
        last_data_received_date = data_date_dir_list[-1]
        dir_path = os.path.join(os.getcwd(), "Device/", device, "")
        dir_path = os.path.join(dir_path, 'logs/{}'.format(last_data_received_date))
        while len(os.listdir(dir_path)) == 0:
            data_date_dir_list = data_date_dir_list[:-1]
            last_data_received_date = sorted(data_date_dir_list)[-1]
            dir_path = os.path.join(os.getcwd(), "Device/", device, "")
            dir_path = os.path.join(dir_path, 'data/{}'.format(last_data_received_date))

        data_file_list = os.listdir(dir_path)

        try:
            data_file_list.remove(".DS_Store")
        except:
            pass

        data_file_list = sorted(data_file_list)
    else:
        data_file_list = ["2022-02-02_02-02-02.txt"]
    return data_file_list[-1] if len(data_file_list) > 0 else 'N/A'

def request_latest_data(s, device_info):
    global last_received_filename
    # process to get last received file
    last_file_name = get_last_data_file_name(device_info[0])

    try:
        # last data file name send
        print("Sending Last File Name : ", last_file_name)
        print()
        s.send(struct.pack('>I', len(last_file_name)))
        s.send(last_file_name.encode())

        if struct.unpack('>I', s.recv(4))[0] != 200:
            print("All files are Up-to-date")
            return 2

        file_count = struct.unpack('>I', s.recv(4))[0]
        print("************************ Receiving data ************************")
        print()
        print("Total Data file to be receive : " + str(file_count) + " Files")
        print()
        cnt = 0
        for i in range(int(file_count)):
            if struct.unpack('>I', s.recv(4))[0] != 200:
                print("Server Error")
            # Note the error in file
            print("Receiving data file : " + str(i + 1))

            filename_size = struct.unpack('>I', s.recv(4))[0]
            # print(filename_size)
            cnt += 1

            f_name = s.recv(filename_size).decode()
            if cnt == file_count:
                last_received_filename = f_name
            # print(f_name)
            dir_path = os.path.join(os.getcwd(), "Device/", device_info[0], "")
            if f_name.find(".txt") != -1:
                path = os.path.join(dir_path, f'data/{f_name.split("_")[0]}/')
                # print(path)
                if not os.path.exists(path):
                    os.mkdir(path)
            elif f_name.find("_pfiona.log") != -1:
                path = os.path.join(dir_path, f'log/{f_name.split("_")[0]}/')
                # print(path)
                if not os.path.exists(path):
                    os.mkdir(path)
            else:
                path = os.path.join(dir_path, f'garbage/')
                print(path)
                if not os.path.exists(path):
                    os.mkdir(path)

            # receive checksum here
            receive_checksum = struct.unpack('>I', s.recv(4))[0]

            filesize = struct.unpack('>I', s.recv(4))[0]
            # print(f_name)
            file_to_write = open(path + f_name, 'wb')

            chunksize = 4096

            while filesize > 0:
                if filesize < chunksize:
                    chunksize = filesize
                data = s.recv(chunksize)
                file_to_write.write(data)
                filesize -= len(data)

            file_to_write.close()

            if receive_checksum == get_crc32(path + f_name):
                print(f_name + " received successfully")
                print()
                s.send(struct.pack('>I', 1))
                value_error = 10
            else:
                # delete the file
                os.remove(path + f_name)
                value_error -= 1
                s.send(struct.pack('>I', 0))
            time.sleep(5)
        return True
    # tell server to resend the file with cheksumn again

    except socket.error:
        # record socket.error
        s.send(struct.pack('>I', 0))
        dir_path = os.path.join(os.getcwd(), "Device/", device_info[0], "")

        try:
            path = creat_new_folder(dir_path, '/connection/')
            print(path)
            if not os.path.exists(path):
                os.mkdir(path)
            f = open(os.path.join(dir_path, 'connection/com.txt'), 'a')
        except:
            f = open(os.path.join(dir_path, '/connection/com.txt'), 'a')

        f.write("@Data_Receive_Error : " + str(value_error))
        f.write("\n")
        f.write(str(socket.error))
        f.write("\n")
        f.write("\n")

        print("value error: ", + str(value_error))
        print("Going for 20 seconds sleep")
        time.sleep(20)
        print(str(socket.error))
        return False

def request_latest_logs(s, device_info):
    # process to get last received file
    last_file_name = get_last_log_file_name(device_info[0])

    try:
        # last data file name send
        print("Sending Last File Name : ", last_file_name)
        print()
        s.send(struct.pack('>I', len(last_file_name)))
        s.send(last_file_name.encode())

        if struct.unpack('>I', s.recv(4))[0] != 200:
            print("All files are Up-to-date")
            return 2

        file_count = struct.unpack('>I', s.recv(4))[0]
        print("************************ Receiving data ************************")
        print()
        print("Total Data file to be receive : " + str(file_count) + " Files")
        print()
        for i in range(int(file_count)):
            if struct.unpack('>I', s.recv(4))[0] != 200:
                print("Server Error")
            # Note the error in file
            print("Receiving log file : " + str(i + 1))

            filename_size = struct.unpack('>I', s.recv(4))[0]
            f_name = s.recv(filename_size).decode()
            dir_path = os.path.join(os.getcwd(), "Device/", device_info[0], "")
            # if f_name.find(".txt")!=-1:
            #     path = os.path.join(dir_path, f'data/{f_name.split("_")[0]}/')
            #     print(path)
            #     if not os.path.exists(path):
            #         os.mkdir(path)
            # el
            if f_name.find("_pfiona.log") != -1:
                path = os.path.join(dir_path, f'logs/{f_name.split("_")[0]}/')
                if not os.path.exists(path):
                    os.mkdir(path)
            else:
                path = os.path.join(dir_path, f'garbage/')
                if not os.path.exists(path):
                    os.mkdir(path)

            # receive checksum here
            receive_checksum = struct.unpack('>I', s.recv(4))[0]

            filesize = struct.unpack('>I', s.recv(4))[0]
            file_to_write = open(path + f_name, 'wb')

            chunksize = 4096

            while filesize > 0:
                if filesize < chunksize:
                    chunksize = filesize
                data = s.recv(chunksize)
                file_to_write.write(data)
                filesize -= len(data)

            file_to_write.close()

            if receive_checksum == get_crc32(path + f_name):
                print(f_name + " received successfully")
                print()
                s.send(struct.pack('>I', 1))
                value_error = 10
            else:
                # delete the file
                os.remove(path + f_name)
                value_error -= 1
                s.send(struct.pack('>I', 0))
            time.sleep(5)
        return True
    # tell server to resend the file with cheksumn again

    except socket.error:
        # record socket.error
        s.send(struct.pack('>I', 0))
        dir_path = os.path.join(os.getcwd(), "Device/", device_info[0], "")

        try:
            path = creat_new_folder(dir_path, '/connection/')
            print(path)
            if not os.path.exists(path):
                os.mkdir(path)
            f = open(os.path.join(dir_path, 'connection/com.txt'), 'a')
        except:
            f = open(os.path.join(dir_path, '/connection/com.txt'), 'a')

        f.write("@Data_Receive_Error : " + str(value_error))
        f.write("\n")
        f.write(str(socket.error))
        f.write("\n")
        f.write("\n")

        print("value error: ", str(value_error))
        print("Going for 20 seconds sleep")
        time.sleep(20)
        print(str(socket.error))
        return False

def start_cycle_1(device):
    global current_state
    global next_state
    global value_error
    global verify_error
    global con_error
    global status
    global last_received_filename
    global connection_Error
    global s
    global host_request_data

    while 1:
        if data_state[current_state] == 'status_check':  # 0
            print()
            print("Current State : " + current_state + " : Host network status check")
            time.sleep(3)
            if data_status[status] == "ideal":
                next_state = '2'
            elif data_status[status] == "collect_data":
                next_state = '1'

        elif data_state[current_state] == 'start_TCP_connection':  # 1
            print()
            print("Current State : " + current_state + " : Start TCP connection")
            time.sleep(3)

            if not s:
                print()
                print("Connection Error: ", con_error)
                time.sleep(5)
                try:
                    s = connect(device)
                    if s:
                        next_state = '3'
                    else:
                        connection_Error = "Error while connecting to Server"
                        next_state = '5'
                except Exception as e:
                    connection_Error = e
                    next_state = '5'
            else:
                connection_Error = "Port is alredy connected, going for next stage"
                next_state = '3'
            if con_error <= 0:
                # cycle_1_status["data_collecting_status"] = True
                con_error = 3
                next_state = '2'

        elif data_state[current_state] == 'sleep_mode_1':  # 2
            print()
            print("Current State : " + current_state + ": Into sleep mode 1")
            time.sleep(3)
            print("Going for 600 seconds sleep")
            time.sleep(600)
            next_state = '0'
            status = '2'

        elif data_state[current_state] == 'connection_standby':  # 3
            print()
            print("Current State : " + current_state + " : " + "Into connection Stand By Mode")
            time.sleep(3)
            if host_request_data and data_status[status] == "data_received":
                next_state = "9"
            elif not host_request_data and data_status[status] == "data_received":
                next_state = "8"
            else:
                next_state = "4"
            print(next)

        elif data_state[current_state] == 'receiving_data':  # 4
            print()
            print("Current State : " + current_state + " : " + "Receiving Latest Data and Log Files")
            data_receive_status["data_files"] = 0
            data_receive_status["log_files"] = 0

            d = request_latest_data(s, device)
            if d:
                if isinstance(d, (bool)):
                    data_receive_status["data_files"] = 1
                    print()
                    print("Data files received successfully from server")
                    next_state = "6"
                elif d == 2:
                    data_receive_status["data_files"] = 2
                    print()
                    print("All data files are up to date. So, no tranfer needed for data")
                    next_state = "2"
                else:
                    print()
                    print("Encounter issue while receiving data files")

            d2 = request_latest_logs(s, device)
            if isinstance(d2, (bool)):  # True
                data_receive_status["log_files"] = 1
                print()
                print("Log files rececived successfully from server")

            elif d2 == 2:
                data_receive_status["log_files"] = 2
                print()
                print("All log files are up to date. So, no tranfer needed for logs")
            else:
                print()
                print("Encounter issue while receiving Log files")
            break
            if data_receive_status["data_files"] and data_receive_status["log_files"]:
                next_state = "6"
            else:
                next_state = "7"

        elif data_state[current_state] == 'connection_error':  # 5
            con_error -= 1
            print()
            print("Current State : " + current_state + " : Error : " + str(connection_Error))
            time.sleep(5)
            print("Recording error in file : ", connection_Error)
            next_state = '1'

        elif data_state[current_state] == "send_feedback":  # 6
            print()
            print("Current State : " + current_state + ": Send feedback for data received")
            time.sleep(3)

            while verify_error > 0:
                try:
                    if send_feedback(1):
                        # cycle_1_status["data_received"] = True
                        next_state = '2'
                        break
                    else:
                        verify_error -= 1
                except OSError as e:
                    print("Error : ", str(e))
                    verify_error -= 1
                # record error
            if verify_error <= 0:
                next_state = '11'

        elif data_state[current_state] == 'verification_error':  # 7
            print()
            print("Current State : " + current_state + ": Verification Error")
            time.sleep(3)
            verify_error -= 1
            if verify_error > 0:
                print()
                print("Verify error: ", verify_error)
                print("Going for 10 seconds sleep")
                time.sleep(10)
                next_state = '4'
            else:
                next_state = '8'

        elif data_state[current_state] == 'terminate_connection':  # 8
            # terminate the connection
            print("Into terminate connection state")
            if s:
                s.close()
            verify_error = 10
            next_state = '0'
            status = '1'

        elif data_state[current_state] == 'sleep_mode_2':  # 9
            print()
            print("Current State : " + current_state + ": Into sleep mode 2")
            time.sleep(3)
            print("Going for 60 seconds sleep")
            time.sleep(60)
            next_state = "3"

        elif data_state[current_state] == "verify_received_data":  # 10
            print()
            print("Current State : " + current_state + ": Verifying received files")
            time.sleep(3)
            if last_received_filename == get_last_data_file_name(device[0]):
                next_state = '6'
            else:
                next_state = '7'
            # status_change('7', '4')

        elif data_state[current_state] == "update_status":  # 11
            print()
            print("Current State : " + current_state + ": Updating status : Data received and verified successfully")
            time.sleep(3)
            status = "3"
            next_state = "3"
            host_request_data = 0
            print()
        
        current_state = next_state

if __name__ == '__main__':
    t1 = threading.Thread(target=start_cycle_1(devices["PI1"]), name='data')
    # t2 = threading.Thread(target=send_command, name='command')

    # starting threads
    t1.start()
    # t2.start()

    # wait until all threads finish
    t1.join()
# t2.join()
