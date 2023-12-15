import socket
# import numpy as np
import encodings
# import seabreeze_pf
import pickle
import json
import time
import threading
import os
from datetime import date
import struct
import zlib
import sys
import os

# from dotenv import load_dotenv

# load_dotenv()

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT1 = 8057  # Port to listen on (non-privileged ports are > 1023)
# PORT2 = 8095

# data_send = ""
d = date.today()


def random_data():
    return "hello world!!"  # return data_send seperated b>


current_state = '0'
next_state = '1'
data_status = {"0": "ideal", "1": "data_send"}
status = '1'
connection_Error = ""
data_sent_status = {"data_files": 0, "log_files": 0}
start_time = 0

host_request_data = 1

send_mode = 1

con_error = 3
value_error = 10
verify_error = 10
s = None
conn = None
free_error = 3
# current_state = {"data_sent": False, "data_sending_status": False}

data_state = {
    '0': 'status_check',
    '1': 'start_TCP_connection',
    '2': 'sleep_mode_1',
    '3': 'connection_standby',
    '4': 'sending_data',
    '5': 'connection_error',
    '6': 'receive_feedback',
    '7': 'verify_error',
    '8': 'terminate_connection',
    '9': 'check_data_space',
    '10': 'free_space_error'
}

BUFFER_SIZE = 8192

# def status_change(current_state, next_state):
#     global current_state, next_state
#     current_state = current_state
#     next_state = next_state
#     print()
#     print("state change : " + "Current: " + current_state + " Next: " + next_state)
#     print()


max_time = 10800


def get_crc32(path):
    with open(path, 'rb') as f:
        crc = 0
        while True:
            data_send = f.read(BUFFER_SIZE)
            if not data_send:
                break
            crc = zlib.crc32(data_send, crc)
    return crc


def get_file_list(f_name):
    f = 1
    if f_name.find(".txt") != -1:
        # directory path
        base_path = str(os.getcwd()) + '/Device/data'
        # "/Users/Milan/Documents/RA:TA/GitHub/pFIONA/final_dashboard/Devices/data"
        # t="Devices/data_send/"
        # base_path = os.path.join(os.getcwd(),t)
        data_date_dir_list = os.listdir(base_path)
    elif f_name.find("_pfiona.log") != -1:
        # directory path
        base_path = str(os.getcwd()) + '/Device/logs'
        # "/Users/Milan/Documents/RA:TA/GitHub/pFIONA/final_dashboard/Devices/logs"
        # base_path="/home/pfiona/pFIONA/.tmp"
        # t="Devices/data_send/"
        # base_path = os.path.join(os.getcwd(),t)
        data_date_dir_list = os.listdir(base_path)

    # remove "".DS_Store" and "reagents.csv" from list date list
    try:
        data_date_dir_list.remove(".DS_Store")
    except Exception as e:
        print(e)
        pass
    try:
        data_date_dir_list.remove("reagents.csv")
    except Exception as e:
        print(e)
        pass
    # print("pass")
    try:
        data_date_dir_sorted_list = sorted(data_date_dir_list)
        # print(data_date_dir_sorted_list)
        dates = data_date_dir_sorted_list[data_date_dir_sorted_list.index(f_name.split("_")[0]):]
        # print(dates)
        data_file_list = os.listdir(os.path.join(base_path, f'{dates[0]}'))
        # print(data_file_list)
        data_file_list = sorted(data_file_list)
        data_file_list = data_file_list[data_file_list.index(f_name):]
        # print(data_file_list)

        if len(dates) > 1:
            for i in range(1, len(dates)):
                data_file_list.extend(sorted(os.listdir(os.path.join(base_path, f'{dates[i]}'))))
    except Exception as e:
        print(e)
        data_file_list = []
        f = 0
    print(data_file_list)
    return data_file_list, f


def fileOpener(file_name):
    # dir_path = os.path.join(os.getcwd(), "Devices/")
    # dir_path="/home/pfiona/pFIONA/saved_data/"
    if file_name.find(".txt") != -1:
        # directory path
        dir_path = str(os.getcwd()) + '/Device/data' 
        # "/Users/Milan/Documents/RA:TA/GitHub/pFIONA/final_dashboard/Devices/data"
        # t="Devices/data_send/"
        # base_path = os.path.join(os.getcwd(),t)

    elif file_name.find("_pfiona.log") != -1:
        # directory path
        dir_path = str(os.getcwd()) + '/Device/logs'
        # "/Users/Milan/Documents/RA:TA/GitHub/pFIONA/final_dashboard/Devices/logs"
        # base_path="/home/pfiona/pFIONA/.tmp"
        # t="Devices/data_send/"
        # base_path = os.path.join(os.getcwd(),t)

    file_path = os.path.join(dir_path, f'{file_name.split("_")[0]}/{file_name}')
    f = open(file_path, 'rb')
    data_send = f.read()
    return f, data_send, file_path, file_name


def closeFile(f):
    f.close()


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
                    data_send = "Ok".encode()
                    conn.send(data_send)
                    if cmd == "restart":
                        print("Restart Command Called")
                    elif cmd == "flush":
                        print("Flush command called")
    except OSError as e:
        print("command function error : ", str(e))


def receive_feedback(value):
    try:
        print("Seding Feedback")
        conn.send(struct.pack('>I', value))
        print("Feedback Sent")
        print('Receiving Feedback')
        if struct.unpack('>I', conn.recv(4))[0] == value:
            print("Feedback Received")
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def recvAll(conn, n):
    data_send = bytearray()
    while len(data_send) < n:
        pak = conn.recv(n - len(data_send))
        if not pak:
            return None
        data_send.extend(pak)
    return data_send


def send_latest_logs():
    # last file name
    global s
    global conn
    try:

        last_log_file_name = struct.unpack('>I', conn.recv(4))[0]
        f_name = conn.recv(last_log_file_name).decode()
        print("Last Log File name: ", f_name)
        print()

        log_file_list, f = get_file_list(f_name)
        if f == 0:
            print("There is discripancy while fetching the files, Please check Device folder on client and server")

        if len(log_file_list) <= 1:
            # Send latest data_send already sent, Close the connection
            conn.send(struct.pack('>I', 100))
            print("All log files are Up-to-date")
            return 2
        # print(log_file_list)
        conn.send(struct.pack('>I', 200))
        print("************************ Sending latest log files ************************")
        print()
        print("Total Data file to be sent : " + str(len(log_file_list) - 1) + " Files")
        print()
        conn.send(struct.pack('>I', int(len(log_file_list) - 1)))

        for i in range(1, len(log_file_list)):

            try:
                f, data_send, path, f_name = fileOpener(log_file_list[i])
            except Exception as e:
                print(e)
                # Send latest data_send already sent, Close the connection

                print("File opening or fetching data_send error")
                conn.send(struct.pack('>I', 100))
                continue

            conn.send(struct.pack('>I', 200))
            print("Sending data_send file : " + str(i))

            conn.send(struct.pack('>I', len(log_file_list[i])))
            conn.send(f_name.encode())

            conn.send(struct.pack('>I', int(get_crc32(path))))

            filesize = os.path.getsize(path)
            # filesize = bin(filesize)[2:].zfill(32) # encode filesize as 32 bit binary s.send(filesize)
            conn.send(struct.pack('>I', int(filesize)))
            conn.sendall(data_send)

            print(f_name + " sent successfully")
            print()

            if struct.unpack('>I', conn.recv(4))[0] == 0:
                # Note the error
                continue
            time.sleep(5)
        return True
    except Exception as e:
        print("error")
        print(e)
        print("error")
        print()
        # cycle_1_status["data_sending_status"]=False
        # record error
        return False


def send_latest_data():
    # last file name
    global s
    global conn
    try:
        last_file_name = struct.unpack('>I', conn.recv(4))[0]
        f_name = conn.recv(last_file_name).decode()
        print("Last File name: ", f_name)
        print()

        data_file_list, f = get_file_list(f_name)
        if f == 0:
            print("There is discripancy while fetching the files, Please check Device folder on client and server")

        if len(data_file_list) <= 1:
            # Send latest data_send already sent, Close the connection
            conn.send(struct.pack('>I', 100))
            print("All files are Up-to-date")
            return 2
        print(data_file_list)
        conn.send(struct.pack('>I', 200))
        print("************************ Sending latest data files ************************")
        print()
        print("Total Data file to be sent : " + str(len(data_file_list) - 1) + " Files")
        print()
        conn.send(struct.pack('>I', int(len(data_file_list) - 1)))

        for i in range(1, len(data_file_list)):

            try:
                f, data_send, path, f_name = fileOpener(data_file_list[i])
            except Exception as e:
                print(e)
                # Send latest data_send already sent, Close the connection

                print("File opening or fetching data_send error")
                conn.send(struct.pack('>I', 100))
                continue

            conn.send(struct.pack('>I', 200))
            print("Sending data_send file : " + str(i))

            conn.send(struct.pack('>I', len(data_file_list[i])))
            conn.send(f_name.encode())

            conn.send(struct.pack('>I', int(get_crc32(path))))

            filesize = os.path.getsize(path)
            # filesize = bin(filesize)[2:].zfill(32) # encode filesize as 32 bit binary s.send(filesize)
            conn.send(struct.pack('>I', int(filesize)))
            conn.sendall(data_send)

            print(f_name + " sent successfully")
            print()

            if struct.unpack('>I', conn.recv(4))[0] == 0:
                # Note the error
                continue
            time.sleep(5)
        return True

    except Exception as e:
        print("error")
        print(e)
        print("error")
        print()
        # cycle_1_status["data_sending_status"]=False
        # record error
        return False


def connect():
    try:
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Server Started waiting for client to connect")

        s2.bind((HOST, PORT1))
        s2.listen()

        try:
            conn, addr = s2.accept()
            if conn:
                print('Connected by', addr)
                # while True:
                #  data_send = conn.recv(1024).decode('utf-8')
                print("Connection establised")
                return s2, conn
        except OSError as e:
            # Add error in log file
            print("data_send connection error")
    except OSError as e:
        print("data_send function error : ", str(e))

    return False, False


def chekck_for_space_availability():
    # check for the space in PI
    return True


def remove_files():
    # remove files to free up space
    return True


def check_if_new_data_available(c):
    while c > 0:
        time.sleep(10)
        c -= 1
    return True


def check_connection():
    return True


def start_cycle_1():
    global current_state
    global next_state

    global value_error
    global free_error
    global verify_error
    global con_error
    global connection_Error

    global s
    global conn


    global start_time
    global status
    global data_sent_status
    global data_status

    while 1:

        if data_state[current_state] == 'status_check':  # 0
            print("Current State : " + current_state + " : Device network status check")
            time.sleep(3)
            if data_status[status] == "ideal":
                next_state = '2'
            elif data_status[status] == "data_send":
                # (CS,NS)=(1,3)
                next_state = '1'

        elif data_state[current_state] == 'start_TCP_connection':  # 1
            print("Current State : " + current_state + " : Accepting TCP connection from Host")
            if not s:
                while con_error > 0:
                    time.sleep(6)
                    try:
                        s, conn = connect()
                        if s and conn:
                            # (CS,NS)=(3,4)
                            # cycle_1_status["data_sending_status"] = True
                            start_time = time.time()
                            next_state = "3"
                            break
                        else:
                            connection_Error = "Error While opening connection on port"
                            next_state = '5'
                            # con_error -= 1
                    except Exception as e:
                        connection_Error = e
                        next_state = '5'
            else:

                # cycle_1_status["data_sending_status"] = False
                print()
                print("Warning : " + current_state + " : Connection is already open")
                time.sleep(3)
                start_time = time.time()
                next_state = '3'

            if con_error <= 0:
                con_error = 3
                status = '0'
                next_state = '0'

        elif data_state[current_state] == 'sleep_mode_1':  # 2
            print()
            print("Current State : " + current_state + " : Into sleep state 1")
            time.sleep(3)
            print("Going for 600 seconds sleep")

            time.sleep(600)
            status = 1
            next_state = 0

        elif data_state[current_state] == 'connection_standby':  # 3

            print()
            print("Current State : " + current_state + " : " + "Into connection Stand By Mode")
            time.sleep(3)
            # wait for host request
            # print("Free Error: ", free_error)
            # free_error = 3

            if host_request_data:
                next_state = "4"
            else:
                if (time.time() - start_time) < max_time:
                    time.sleep(10)
                    next = '3'
                else:
                    next_status = "8"

        elif data_state[current_state] == 'sending_data':  # 4
            print()
            print("Current State : " + current_state + " : " + "Sending Latest Data")
            data_sent_status["data_files"] = 0
            data_sent_status["log_files"] = 0

            d = send_latest_data()
            if d:
                if isinstance(d, (bool)):  # True
                    data_sent_status["data_files"] = 1
                    print()
                    print("Data files sent successfully from server")
                elif d == 2:
                    data_sent_status["data_files"] = 2
                    print()
                    print("All data files are up to date. So, no tranfer needed for data files")
                else:
                    print()
                    print("Encounter issue while sending data files")

            # else:#False
            #     # (CS,NS)=(7,6)
            #     status_change('7', '4')

            d2 = send_latest_logs()
            if d2:
                if isinstance(d2, (bool)):  # True
                    data_sent_status["log_files"] = 1
                    print()
                    print("Log files sent successfully from server")

                elif d2 == 2:
                    data_sent_status["log_files"] = 2
                    print()
                    print("All log files are up to date. So, no tranfer needed for logs")
                else:
                    print()
                    print("Encounter issue while sending Log files")
            break
            if data_sent_status["data_files"] and data_sent_status["log_files"]:
                next_state = "6"
            else:
                next_state = "7"

        elif data_state[current_state] == 'connection_error':  # 5

            con_error -= 1
            print()
            print("Current State : " + current_state + " : " + "connection_Error")
            time.sleep(3)
            print("Recording following error in file : ", connection_Error)
            next_state = '1'

            # print("Into connection error state")
            # con_error -= 1
            # print("Connection Error: ", con_error)
            # print("Into 60 seconds sleep")
            # time.sleep(60)
            # next_state='1'

        elif data_state[current_state] == 'receive_feedback':  # 6
            print()
            print("Current State : " + current_state + ": Receive feedback for data sent")
            time.sleep(3)
            while free_error > 0:
                try:
                    if receive_feedback(1):
                        # (CS,NS)=(9,3)
                        next_state = '2'
                        break
                    else:
                        # (CS,NS)=(7,4)
                        free_error -= 1
                except OSError as e:
                    print("Error : ", str(e))
                    free_error -= 1
                    # record error
            if free_error <= 0:
                next_state = '7'

        elif data_state[current_state] == 'verify_error':  # 7
            if verify_error > 0:
                verify_error -= 1
                print("Into verify error state : verify_error : ", verify_error)
                time.sleep(20)
                next_state = '4'
            else:
                next_state = '8'

        elif data_state[current_state] == 'terminate_connection':  # 8
            print("Into terminate connection state")

            if s:
                s.close()

            free_error = 3
            verify_error = 10

            next_state = '2'

        elif data_state[current_state] == 'check_data_space':  # 9
            print("Into Check space availability State")

            if chekck_for_space_availability():
                next_state = '3'
            else:
                while free_error > 0:
                    if remove_files():
                        next_state = '10'
                    else:
                        free_error -= 1
                        next_state = '3'

        elif data_state[current_state] == 'free_space_error':  # 10
            counter = 10
            if check_if_new_data_available(counter):
                free_error = 3
                verify_error = 10
                next_state = '3'

        current_state = next_state


if __name__ == '__main__':
    t1 = threading.Thread(target=start_cycle_1, name='data_send')

    # starting threads
    t1.start()

    # wait until all threads finish
    t1.join()
