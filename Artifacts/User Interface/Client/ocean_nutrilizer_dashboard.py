from jinja2 import Undefined
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import os
from bokeh.models import ColumnDataSource, CustomJS, Range1d, Select,FactorRange
from bokeh.plotting import figure, show,output_file
from bokeh.layouts import column,grid,row
import matplotlib.pyplot as plt
from mpl_toolkits.axisartist.axislines import Subplot
from pymysql import NULL 
import subprocess
import pandas as pd
import numpy as np
from bokeh.models.widgets import Button
from random import random
import json
import time
from decode import file_read
import socket
import sys
from datetime import date
import tkinter as tk
from tkinter import *
from tkinter import ttk
# from tkterminal import Terminal
from tkinter.messagebox import NO, YES, showwarning
from tkinter import messagebox
import tkinter.scrolledtext as scrolledtext
from datetime import datetime
import commands_queue as commands_queue

devices={
    "PI1":["PI1","192.168.5.1","8080",["status",0]],
    }

t="@Time"
w="@Wavelength"
b_s_v_2048_1="@blank_sample_value_2048_1"
b_s_v_2048_2="@blank_sample_value_2048_2"
b_s_a="@blank_sample_absorbances"
b_s_c="@blank_sample_count"
po4_st_v_2048_2="@po4_standard_value_2048_1"
po4_st_v_2048_2="@po4_standard_value_2048_2"
po4_st_ab="@po4_standard_absorbances"
po4_st_c="@po4_standard_count"
po4_sa_v_2048_1="@po4_sample_value_2048_1"
po4_sa_v_2048_2="@po4_sample_value_2048_2"
po4ss = "@po4_sample_absorbances"
po4sc="@po4_sample_count" 
n_s_r="@num_of_sample_run" #done
n_p="@num_ports"
pp1="@port_p1"
pp2="@port_p2"
pp3="@port_p3"
pp4="@port_p4"
pp5="@port_p5"
pp6="@port_p6"
pp7="@port_p7"
pp8="@port_p8"
m_l="@monitoringlambda"
r_l="@reflambda"
k_c="@known_concentration" 
po4_c="@po4_concentrations"
f_p1_s="@flush_p1_speed"
f_p1_a="@flush_p1_amount"
f_p2_s="@flush_p2_speed"
f_p2_a="@flush_p2_amount"
b_p1_s="@blank_p1_speed"
b_p1_a="@blank_p1_amount"
m_p1_s="@molybdate_p1_speed"
m_p1_a="@molybdate_p1_amount"
m_p2_s="@molybdate_p2_speed"
m_p2_a="@molybdate_p2_amount"
a_p1_s="@ascorbic_p1_speed"
a_p1_a="@ascorbic_p1_amount"
a_p2_s="@ascorbic_p2_speed"
a_p2_a="@ascorbic_p2_amount"
f_c_p1_s="@flow_cell_p1_speed"
f_c_p1_a="@flow_cell_p1_amount"
p_st_p1_s="@po4_standard_p1_speed"
p_st_p1_a="@po4_standard_p1_amount"
p_sa_p1_s="@po4_sample_p1_speed"
p_sa_p1_a="@po4_sample_p1_amount"
t_p="@totalprimes"
p1_pp1s="@port1_pp1speed"
p1_pp1a="@port1_pp1amount"
p2_pp2s="@port2_pp1speed"
p2_pp2a="@port2_pp1amount"
p2_pp1s="@port2_pp2speed"
p2_pp1a="@port2_pp2amount"
p3_pp1s="@port3_pp1speed"
p3_pp1a="@port3_pp1amount"
p4_pp1s="@port4_pp1speed"
p4_pp1a="@port4_pp1amount"
p5_pp1s="@port5_pp1speed"
p5_pp1a="@port5_pp1amount"
p6_pp1s="@port6_pp1speed"
p6_pp1a="@port6_pp1amount"
p7_pp1s="@port7_pp1speed"
p7_pp1a="@port7_pp1amount"
p8_pp1s="@port8_pp1speed"
p8_pp1a="@port8_pp1amount"
aa_r_u="@Ascorbic_Acid_Reagent_used"
aa_r_r="@Ascorbic_Acid_Reagent_remaining"
m_r_u="@Molybdate_Reagent_used"
m_r_r="@Molybdate_Reagent_remaining"
p_r_u="@PO4_Reagent_used"
p_r_r="@PO4_Reagent_remaining"
w_r_u="@water_Reagent_used"
w_r_r="@water_Reagent_remaining"
t0="@t0"
t1="@t1"
t3="@t3"
a_t="@auxtime"
d_s_t="@darkscantime"
ref_s_t="@refscantime"
t_r="@time_required"
a_m_s="@aux_motor_status"

m1sp="@motor1_speed"
m1a="@motor1_amount" 
m1st="@motor1_status" #done

m2sp="@motor2_speed"
m2a="@motor2_amount" 
m2st="@motor2_status" #done

n_s_t="@next_sample_time" #done

motor1_data=None
device_data={

}
for i in devices: 
    device_data[i]={}

root = tk.Tk()

def refresh():
    print("refresh UI function called")
    #need to check which device is live
    # data = file_read(devices["PI1"])

    # device_data[device_info[0]][m1st].config(text=data["data"]["@motor1_status"])

    # motor1_data.config(textdata["data"]["@motor1_status"])
    # motor2_data.config(textdata["data"]["@motor2_status"])
    # spec.config(text=currentStruc[-1]["spec"])
    # aux_motor_status.config(text=currentStruc[-1]["aux_motor_status"])
    # curr_cycle.config(text=currentStruc[-1]["cycle"])
    # next_sample_time.config(text=currentStruc[-1]["next_sample_time"])
    # num_of_sample_run.config(text=currentStruc[-1]["num_of_sample_run"])
    # valve_position
    # root.after(10, refresh)
    root.update()

def fetch_log_data(data):

    d={}
    d["INFO"]=[]
    d["DEBUG"]=[]
    d["WARNING"]=[]

    for i in data[0]["INFO"]:
        d["INFO"].append([i[0],i[1]])
        # if "pump_1" in i[1]:
        #     try:
        #         d["Pump_1"].append([i[0],i[1].split("pump_1/")[0]+"pump_1"])
        #         if "pump_2" in i[1]:
        #             d["Pump_2"].append([i[0],i[1].split("pump_1/")[1]])
        #     except:if 
        #         d["Pump_1"].append([i[0],i[1]])

        # elif "pump_2" in i[1]:
        #     try:
        #         d["Pump_2"].append([i[0],i[1].split("pump_1/")[1]])
        #     except:
        #         d["Pump_2"].append([i[0],i[1]])
            
        # elif "Aux" in i[1]:
        #     d["Aux"].append([i[0],i[1]])

        # elif "port" in i[1]:
        #     d["Port"].append([i[0],i[1]])
    for i in data[0]["DEBUG"]:
        d["DEBUG"].append([i[0],i[1]])
    for i in data[0]["WARNING"]:
        d["WARNING"].append([i[0],i[1]])

    return d

# "remove commands (101) ","restart (102)","flush (103)","refresh data ()","clear data (105)"
command_list=["101","102","103","104",]

modes={"1":"automatic","2":"pause","3":"full manual"}

#"blank sample", "po4 standard", "po4 sample", "Restart", "reset cycle", "clear data","flush","refresh data","Clear Data"
command_list=["101","102","103","104","105","106","107","108","109"]


def verify_and_add_command(cmd):

    if cmd in command_list:
        # print("command is in command list. However, it will only be added if queue is free")    
        if commands_queue.add_command(cmd):
            # print("Command is added succeessfully in the buffer")
            messagebox.showinfo("Success", "Command is added succeessfully into the buffer")
            return True
        else:
            messagebox.showinfo("Error", "There is alredy command in queue, free queue to send new command")
            # print("There alredy command in queue, free queue to send new command")
            return False
    else:
        # print("Command is not in command list")
        messagebox.showinfo("Error", "Command is not in command list")
        return False

def send_command(text):
    if type(text) == str :pass
    else: text = text.get('1.0', 'end')
    if text.strip():
        verify_and_add_command(text.strip())

def free_command_queue():
    print("free_command_queue function called")
    if commands_queue.remove_command():
            messagebox.showinfo("Success", "Command is removed succeessfully from the buffer")
    else:
        messagebox.showinfo("Error", "No command in the buffer to remove")
    
def blank_sample():
    print("Blank Sampel function called")
    if commands_queue.get_last_mode() == "3":
        send_command("101")
        
    else:
        messagebox.showinfo("Error", "Please change mode from Automatic to manual and press reset cycle button and then run any sample")
    return True

def po4_standard():
    print("Po4 Standard Sample function called")
    if commands_queue.get_last_mode() == "3":
        send_command("102")
        
    else:
        messagebox.showinfo("Error", "Please change mode from Automatic to manual and press reset cycle button and then run any sample")
    
    return True

def po4_sample():
    print("Po4 Sample function called")
    if commands_queue.get_last_mode() == "3":
        send_command("103")
        
    else:
        messagebox.showinfo("Error", "Please change mode from Automatic to manual mode and use reset cycle button and then run any sample")
    return True

def restart():
    print("restart function called")
    if commands_queue.get_last_mode() == "3":
        send_command("104")
        
    else:
        messagebox.showinfo("Error", "Please change mode from Automatic mode to manual mode and press reset cycle button and then restart button")
    return True

def reset_cycle():
    print("Reset Cycle function called")
    if commands_queue.get_last_mode() == "3":
        send_command("105")
        
    else:
        messagebox.showinfo("Error", "Please change mode from Automatic mode to manual mode and then press reset cycle button")
    return True

def clear_data():
    print("Clear Data function called")
    if commands_queue.get_last_mode() == "3":
        send_command("106")
        
    else:
        messagebox.showinfo("Error", "Please change mode from Automatic mode to manual mode and then press reset cycle button")
    return True

def flush():
    print("flush function called")
    if commands_queue.get_last_mode() == "3":
        send_command("107")
        
    else:
        messagebox.showinfo("Error", "Please change mode from Automatic mode to manual mode and then press reset cycle button and then flush button")
    return True

def data_refresh():
    print("Refresh data function called")
    send_command("108")
    return True


def main_dashboard_tab(root,device_info,data,v,sampling_freq,cali_freq):

    tabControl = ttk.Notebook(root, width=1400, height=200)
    tab0 = ttk.Frame(tabControl)
    tab1 = ttk.Frame(tabControl)
    # tab2 = ttk.Frame(tabControl)
    tab3 = ttk.Frame(tabControl)
    tab4 = ttk.Frame(tabControl)
    tab5 = ttk.Frame(tabControl)
    tab6 = ttk.Frame(tabControl)
    

    tabControl.add(tab0, text ='Absorbance Spectrums')
    tabControl.add(tab1, text ='Select Mode')
    # tabControl.add(tab2, text ='Time Series')
    tabControl.add(tab3, text ='Volume Remaining')
    tabControl.add(tab4, text ='Set Port Positions')
    tabControl.add(tab5, text ='Set Pump Speed')
    tabControl.add(tab6, text ='Set Pump Amount')
    

    tabControl.place(x= 2, y=440)
    fm1 = tk.Frame(root,highlightbackground="black", highlightthickness=2)  #Radiobuttons
    top_bg = tk.Canvas(root, width=1400, height=45, bg='#1b2838', highlightthickness=0).place(x=0, y=0)
    tk.Label(root, text='Dashboard', font='Montserrat 25', bg='#1b2838', fg='white').place(x=15, y=3)

    conn_status = tk.Label(
        root,
        text="Connection Status",font='Times 14 bold')
    conn_status.place(x=10, y=50)

    motor111_data = tk.Label(
        root,
        text="Disconnected").place(x=210,y=50)

    instrument_status_box = tk.Canvas(root, width=420, height=220,highlightthickness=2,highlightbackground="black").place(x=10, y=100)
    instrument_status_box_top = tk.Canvas(root, width=420, height=22, highlightthickness=2,highlightbackground="black").place(x=10, y=80)
    tk.Label(root, text='Instrument Status', font='Montserrat 12 bold').place(x=15, y=82)


    action_box = tk.Canvas(root, width=420, height=70,highlightthickness=2,highlightbackground="black").place(x=10, y=350)
    action_box_top = tk.Canvas(root, width=420, height=22, highlightthickness=2,highlightbackground="black").place(x=10, y=330)
    tk.Label(root, text='Action', font='Montserrat 12 bold',).place(x=15, y=325)

    motor1 = tk.Label(root,text="Motor1",font='Times 14 bold')
    motor1.place(x=15, y=110)
    # global motor1_data
    device_data[device_info[0]][m1st]=tk.Label(root,text=data["data"][0]["@motor1_status"])
    device_data[device_info[0]][m1st].place(x=215,y=110)

    tk.Label(root,text="Valve Position",font='Times 14 bold').place(x=15,y=130)

    valve_position = tk.Label(root,text="3").place(x=215,y=130)

    tk.Label(root,text="Motor2",font='Times 14 bold').place(x=15,y=150)

    device_data[device_info[0]][m2st] =tk.Label(root,text=data["data"][0]["@motor2_status"])
    device_data[device_info[0]][m2st].place(x=215,y=150)

    tk.Label(root,text="Spec",font='Times 14 bold').place(x=15,y=170)

    spec = tk.Label(root,text="Acquiring")
    spec.place(x=215,y=170)

    tk.Label(root,text="Aux Pump",font='Times 14 bold').place(x=15,y=190)

    device_data[device_info[0]][a_m_s] = tk.Label(root,text="OFF")
    device_data[device_info[0]][a_m_s].place(x=215,y=190)

    tk.Label(root,text="Cycle",font='Times 14 bold').place(x=15,y=210)

    curr_cycle = tk.Label(root,text="SLEEP")
    curr_cycle.place(x=215,y=210)

    # tk.Label(root,text="Time Until Next Sample",font='Times 14 bold').place(x=15,y=230)

    # device_data[device_info[0]][n_s_t] = tk.Label(root,text=data["data"][0]["@next_sample_time"])
    # device_data[device_info[0]][n_s_t].place(x=215,y=230)

    tk.Label(
        root,
        text="Number of Sample Run",font='Times 14 bold').place(x=15,y=230)

    device_data[device_info[0]][n_s_r] = tk.Label(root,text=data["data"][0]["@num_of_sample_run"])
    device_data[device_info[0]][n_s_r].place(x=215,y=230)

    tk.Label(
        root,
        text="Number of Sample Run",font='Times 14 bold').place(x=15,y=230)
    
    t = commands_queue.get_next_command_and_mode()
    if t: 
        device_data[device_info[0]][n_s_r] = tk.Label(root,text=t)
        device_data[device_info[0]][n_s_r].place(x=215,y=230)
    else:
        device_data[device_info[0]][n_s_r] = tk.Label(root,text="No command in the Queue")
        device_data[device_info[0]][n_s_r].place(x=215,y=230)

    if sys.platform == 'darwin':
        def openFolder():
            try:
                subprocess.check_call(['open', '--', os.getcwd()+"/Device/"+device_info[0]])
            except subprocess.CalledProcessError as e:
                # Handle the error gracefully, or simply ignore it
                print(f"Error/Warning opening folder: {e}")
    elif sys.platform == 'linux2' or sys.platform == 'linux':
        def openFolder():
            try:
                subprocess.check_call(['xdg-open', '--', os.getcwd()+"/Device/"+device_info[0]])
            except subprocess.CalledProcessError as e:
                # Handle the error gracefully, or simply ignore it
                print(f"Error/Warning opening folder: {e}")
    elif sys.platform == 'win32' or sys.platform == 'win64':
        def openFolder():
            try:
                subprocess.check_call(['explorer', os.getcwd()+"\\Device\\"+device_info[0]])
            except subprocess.CalledProcessError as e:
                # Handle the error gracefully, or simply ignore it
                print(f"Error/Warning opening folder: {e}")

    
    button1 = tk.Button(root, text="Restart",command=restart)
    button1.place(x=20, y= 360)
    button2 = tk.Button(root, text="Flush",command=flush)
    button2.place(x=70, y= 360)
    button3 = tk.Button(root, text="Clear Data",command=clear_data)
    button3.place(x=115, y= 360)
    button4 = tk.Button(root, text="Show All Data",command=openFolder)
    button4.place(x=185, y= 360)
    button5 = tk.Button(root, text="Clear command queue", command=free_command_queue)
    button5.place(x=275, y= 360)
    button6 = tk.Button(root, text="Refresh Data",command=data_refresh)
    button6.place(x=20, y= 390)
    button7 = tk.Button(root, text="Reset Cycle",command=reset_cycle)
    button7.place(x=100, y= 390)
    button8 = tk.Button(root, text="Blank Sample",command=blank_sample)
    button8.place(x=175, y= 390)
    button9 = tk.Button(root, text="Po4 Standard",command=po4_standard)
    button9.place(x=265, y= 390)
    button10 = tk.Button(root, text="Po4 Sample",command=po4_sample)
    button10.place(x=350, y= 390)
    
    d = fetch_log_data(data["logs"])

    ### data : Logs ###

    tk.Label(root, text='Data Logs', font='Montserrat 12 bold',
            ).place(x=950, y=170)
    tree = ttk.Treeview(root, column=("c1", "c2"), show='headings', height=3)

    tree.column("# 1", anchor=tk.CENTER)
    tree.heading("# 1", text="Timestamp")
    tree.column("# 2", anchor=tk.CENTER)
    tree.heading("# 2", text="Logs")

    # Insert the data in Treeview widget
    for i,v in enumerate(d["INFO"]):
        # Insert the data in Treeview widget
        tree.insert('', 'end', text=i, values=(v[0], v[1]))
    tree.place(x=950,y=200)

    ### Operation Logs : Logs ###
    
    tk.Label(root, text='Operation Logs', font='Montserrat 12 bold',).place(x=950, y=46)
    tree = ttk.Treeview(root, column=("c1", "c2"), show='headings', height=3)

    tree.column("# 1", anchor=tk.CENTER)
    tree.heading("# 1", text="Timestamp")
    tree.column("# 2", anchor=tk.CENTER)
    tree.heading("# 2", text="Logs")

    for i,v in enumerate(d["INFO"]):
        # Insert the data in Treeview widget
        tree.insert('', 'end', text=i, values=(v[0], v[1]))
    tree.place(x=950,y=75)
    # tree.insert('', 'end', text=i, values=(date.today(),"PI restart"))
    # tree.insert('', 'end', text=i, values=(date.today(),"mode change"))
    # tree.place(x=950,y=76)

    ### Debug : Logs ###

    tk.Label(root, text='Debug logs', font='Montserrat 12 bold',
                        ).place(x=445, y=46)
    tree = ttk.Treeview(root, column=("c1", "c2"), show='headings', height=3)

    tree.column("# 1", anchor=tk.CENTER)
    tree.heading("# 1", text="Timestamp")
    tree.column("# 2", anchor=tk.CENTER,stretch=YES,width=300)
    tree.heading("# 2", text="Logs")

    for i,v in enumerate(d["INFO"]):
        # Insert the data in Treeview widget
        tree.insert('', 'end', text=i, values=(v[0], v[1]))
    tree.place(x=445,y=75)
    
    ### Status : Logs ###

    tk.Label(root, text='Status : Logs', font='Montserrat 12 bold',
            ).place(x=445, y=170)
    tree = ttk.Treeview(root, column=("c1", "c2"), show='headings', height=3)

    tree.column("# 1", anchor=tk.CENTER)
    tree.heading("# 1", text="Timestamp")
    tree.column("# 2", anchor=tk.CENTER,width=300)
    tree.heading("# 2", text="Logs")

    for i,v in enumerate(d["WARNING"]):
        # Insert the data in Treeview widget
        tree.insert('', 'end', text=i, values=(v[0], v[1]))
    tree.place(x=445,y=200)

    # commandprompt_text = tk.Text(root, height = 4, width = 115,background="black").place(x=445.5, y = 364)
    # command prompt box

    txt = scrolledtext.ScrolledText(root, height=3, width=60, undo=True,highlightthickness=2,highlightbackground="black")
    txt['font'] = ('consolas', '12')
    txt.place(x=445.5, y = 320)

    tk.Label(root, text='Command Prompt', font='Montserrat 12 bold'
                ).place(x=445, y=290)
    # tk.Button(root, text="Send Command", font='Montserrat 12 bold', command=send_command(txt)).place(x=960,y=340)
    tk.Button(root, text="Send Command", font='Montserrat 12 bold', command=lambda: send_command(txt)).place(x=960, y=340)


    fig1,(axs1,axs2,axs3) = plt.subplots(1,3,figsize=(8, 2))
    x = [float(i) for i in data["data"][0]["@Wavelength"][0:1005]]
    y = [float(i) for i in data["data"][0]["@blank_sample_value_2048_1"]]
    z = [float(i) for i in data["data"][0]["@po4_standard_value_2048_1"]]
    w = [float(i) for i in data["data"][0]["@po4_sample_value_2048_1"]]
        # plotting the graph
    # axs1.plot(blank_sample_spectrum[len(blank_sample_spectrum)-1]["wavelength"],blank_sample_spectrum[len(blank_sample_spectrum)-1]["absorbances"])
    axs1.plot(x,y)
    axs1.set_xlabel('Wavelength', fontsize=3, color='b',)
    axs1.set_ylabel('blank_sample', fontsize=3, color='b')
    axs1.grid()
    axs1.tick_params(axis='both', which='major', labelsize=3)
    
    # axs2.plot(po4_standard_spectrum[len(po4_standard_spectrum)-1]["wavelength"],po4_standard_spectrum[len(po4_standard_spectrum)-1]["absorbances"])
    axs2.plot(x,z)
    axs2.set_xlabel('Wavelength', fontsize=3, color='b')
    axs2.set_ylabel('po4_standard', fontsize=3, color='b')
    axs2.grid()
    axs2.tick_params(axis='both', which='major', labelsize=3)

    # axs3.plot(po4_sample_spectrum[len(po4_sample_spectrum)-1]["wavelength"],po4_sample_spectrum[len(po4_sample_spectrum)-1]["absorbances"])
    axs3.plot(x,w)
    axs3.set_xlabel('Wavelength', fontsize=3, color='b')
    axs3.set_ylabel('po4_sample', fontsize=3, color='b')
    axs3.grid()
    plt.tick_params(axis='both', which='major', labelsize=3)
    plt.subplots_adjust(left=0.2,
                        bottom=0.5, 
                        right=0.8, 
                        top=0.9, 
                        wspace=0.6, 
                        hspace=0.4)
    
        # creating the Tkinter canvas
        # containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig1,
                                master = tab0)  
    canvas.draw()

    canvas.get_tk_widget().pack(side = tk.TOP)

    plt.rcdefaults()
    fig, ax = plt.subplots(figsize=(4, 1.15))

    # Example data
    Ascorbic_Acid=abs(float(data["data"][0]["@Ascorbic_Acid_Reagent_remaining"]))/(abs(float(data["data"][0]["@Ascorbic_Acid_Reagent_used"]))+abs(float(data["data"][0]["@Ascorbic_Acid_Reagent_remaining"])))
    Molybdate=abs(float(data["data"][0]["@Molybdate_Reagent_remaining"]))/(abs(float(data["data"][0]["@Molybdate_Reagent_used"]))+abs(float(data["data"][0]["@Molybdate_Reagent_remaining"])))
    PO4=abs(float(data["data"][0]["@PO4_Reagent_remaining"]))/(abs(float(data["data"][0]["@PO4_Reagent_used"]))+abs(float(data["data"][0]["@PO4_Reagent_remaining"])))
    Water=abs(float(data["data"][0]["@water_Reagent_remaining"]))/(abs(float(data["data"][0]["@water_Reagent_used"]))+abs(float(data["data"][0]["@water_Reagent_remaining"])))

    sampleTypes = ('Ascorbic Acid', 'Molybdate', 'PO4', 'Water')
    y_pos = np.arange(len(sampleTypes))
    performance = np.array([int(Ascorbic_Acid*100), int(Molybdate*100), int(PO4*100), int(Water*100)])

    # Example data
    # sampleTypes = ('Carrier', 'Blank', 'Standard', 'Molybdate', 'Ascorbic Acid')
    # y_pos = np.arange(len(sampleTypes))
    # performance = 3 + 10 * np.random.rand(len(sampleTypes))
    # error = np.random.rand(len(sampleTypes))

    ax.barh(y_pos, performance,align='center')
    ax.set_yticks(y_pos, labels=sampleTypes,fontsize=3, color='r')
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Vol Remaining (Percentage)',fontsize=3, color='b')
    ax.tick_params(axis='both', which='major', labelsize=3, color='b')

    plt.subplots_adjust(
                            left=0.4,
                            bottom=0.4, 
                            right=0.9, 
                            top=0.99, 
                            wspace=0, 
                            hspace=0
                        )
    canvas = FigureCanvasTkAgg(fig,
                                master = tab3)  
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP)

    tk.Label(
        tab4,
        text="Port 1 Position",font='Times 14 bold').pack(side=tk.LEFT)

    tk.Entry(tab4, textvariable=cali_freq).pack(side=tk.LEFT)
    tab4.update()

    tk.Label(
        tab4,
        text="Port 2 Position",font='Times 14 bold').pack(side=tk.LEFT)

    tk.Entry(tab4, textvariable=cali_freq).pack(side=tk.LEFT)

    tk.Label(
        tab4,
        text="Port 3 Position",font='Times 14 bold').pack(side=tk.LEFT)

    tk.Entry(tab4, textvariable=cali_freq).pack(side=tk.LEFT)

    tk.Button(tab4, text="Set Position").pack(side=tk.BOTTOM)

    tk.Label(
        tab5,
        text="Pump 1 Speed",font='Times 14 bold').pack(side=tk.LEFT)

    tk.Entry(tab5, textvariable=cali_freq).pack(side=tk.LEFT)

    tk.Label(
        tab5,
        text="Pump 1 Speed",font='Times 14 bold').pack(side=tk.LEFT)

    tk.Entry(tab5, textvariable=cali_freq).pack(side=tk.LEFT)

    tk.Button(tab5, text="Set Speed").pack(side=tk.BOTTOM)

    tk.Label(
        tab6,
        text="Pump 1 Amount",font='Times 14 bold').pack(side=tk.LEFT)

    tk.Entry(tab6, textvariable=cali_freq).pack(side=tk.LEFT)

    tk.Label(
        tab6,
        text="Pump 1 Amount",font='Times 14 bold').pack(side=tk.LEFT)

    tk.Entry(tab6, textvariable=cali_freq).pack(side=tk.LEFT)

    tk.Button(tab6, text="Set Amount").pack(side=tk.BOTTOM)

    def on_radio_button_mode_changed():
        commands_queue.change_mode(str(var.get()))

    var = tk.IntVar()

    R1 = tk.Radiobutton(tab1, text="Automatic", variable=var, value="1",command=on_radio_button_mode_changed)
    R1.pack( anchor = tk.W )

    R2 = tk.Radiobutton(tab1, text="Pause", variable=var, value="2",command=on_radio_button_mode_changed)
    R2.pack( anchor = tk.W)

    R3 = tk.Radiobutton(tab1, text="Full Manual", variable=var, value="3",command=on_radio_button_mode_changed)
    R3.pack( anchor = tk.W)

    # R4 = tk.Radiobutton(tab1, text="Reset Cycle", variable=var, value="4",command=on_radio_button_mode_changed)
    # R4.pack( anchor = tk.W )

def add_status_and_action(root,device_info,data,cali_freq,sampling_freq):
    x_d_s=25
    y_d_s=10
    fm1 = tk.Frame(root,highlightbackground="black", highlightthickness=2)
    # top_bg = tk.Canvas(root, width=1500, height=55, bg='#1b2838', highlightthickness=0).place(x=0, y=0)
    tk.Label(root, text='Status', font='Montserrat 25', bg='#1b2838', fg='white').place(x=x_d_s+10, y=y_d_s+8)

    #Top-Left Side UI for Connection status 
    conn_status = tk.Label(root,text="Connection Status",font='Times 14 bold')
    conn_status.place(x=x_d_s+10, y=y_d_s+60)

    motor111_data = tk.Label(root,text="Disconnected").place(x=x_d_s+210,y=y_d_s+65)

    instrument_status_box = tk.Canvas(root, width=405, height=450,highlightthickness=2,highlightbackground="black").place(x=x_d_s+10, y=y_d_s+105)
    instrument_status_box_top = tk.Canvas(root, width=405, height=42, highlightthickness=2,highlightbackground="black").place(x=x_d_s+10, y=y_d_s+85)
    tk.Label(root, text='Instrument Status', font='Montserrat 12 bold').place(x=x_d_s+18, y=y_d_s+90)

    instrument_status_box = tk.Canvas(root, width=405, height=450,highlightthickness=2,highlightbackground="black").place(x=x_d_s+450, y=y_d_s+105)
    instrument_status_box_top = tk.Canvas(root, width=405, height=42, highlightthickness=2,highlightbackground="black").place(x=x_d_s+450, y=y_d_s+85)
    tk.Label(root, text='Ports', font='Montserrat 12 bold').place(x=x_d_s+460, y=y_d_s+90)

    instrument_status_box = tk.Canvas(root, width=405, height=350,highlightthickness=2,highlightbackground="black").place(x=x_d_s+875, y=y_d_s+105)
    instrument_status_box_top = tk.Canvas(root, width=405, height=42, highlightthickness=2,highlightbackground="black").place(x=x_d_s+875, y=y_d_s+85)
    tk.Label(root, text='Ports', font='Montserrat 12 bold').place(x=x_d_s+885, y=y_d_s+90)

    x_button,y_button=870,400
    action_box = tk.Canvas(root, width=405, height=90,highlightthickness=2,highlightbackground="black").place(x=x_button+30, y=y_button+75)
    action_box_top = tk.Canvas(root, width=405, height=40, highlightthickness=2,highlightbackground="black").place(x=x_button+30, y=y_button+55)
    tk.Label(root, text='Action', font='Montserrat 12 bold',).place(x=x_button+43, y=y_button+65)

    if sys.platform == 'darwin':
        def openParentDataFolder():
            try:
                subprocess.check_call(['open', '--', os.getcwd()+"/Device/"+device_info[0]])
            except subprocess.CalledProcessError as e:
                # Handle the error gracefully, or simply ignore it
                print(f"Error/Warning opening folder: {e}")
    elif sys.platform == 'linux2' or sys.platform == 'linux':
        def openParentDataFolder():
            try:
                subprocess.check_call(['xdg-open', '--', os.getcwd()+"/Device/"+device_info[0]])
            except subprocess.CalledProcessError as e:
                # Handle the error gracefully, or simply ignore it
                print(f"Error/Warning opening folder: {e}")
    elif sys.platform == 'win32' or sys.platform == 'win64':
        def openParentDataFolder():
            try:
                subprocess.check_call(['explorer', os.getcwd()+"\\Device\\"+device_info[0]])
            except subprocess.CalledProcessError as e:
                # Handle the error gracefully, or simply ignore it
                print(f"Error/Warning opening folder: {e}")
            

    button1 = tk.Button(root, text="Restart",command=restart)
    button1.place(x=x_button+40, y= 105+y_button)
    button2 = tk.Button(root, text="Flush",command=flush)
    button2.place(x=x_button+125, y= 105+y_button)
    button4 = tk.Button(root, text="Clear Data",command=clear_data)
    button4.place(x=x_button+200, y= 105+y_button)
    button7 = tk.Button(root, text="Refresh Data",command=refresh)
    button7.place(x=x_button+300, y= 105+y_button)
    button5 = tk.Button(root, text="Show All Data",command=openParentDataFolder)
    button5.place(x=x_button+40, y= 135+y_button)
    button3 = tk.Button(root, text="Clear command queue", command=free_command_queue)
    button3.place(x=x_button+160, y= 135+y_button)

    # Motor1 state

    tk.Label(
        root,
        text="Motor1",font='Times 14 bold').place(x=x_d_s+15, y=y_d_s+135)

    motor1_data = tk.Label(
        root,
        text=data["data"][0]["@motor1_status"])
    motor1_data.place(x=x_d_s+215,y=y_d_s+140)

    # Valve Position

    tk.Label(
        root,
        text="Valve Position",font='Times 14 bold').place(x=x_d_s+15,y=y_d_s+165)

    valve_position = tk.Label(
        root,
        text="3").place(x=x_d_s+215,y=y_d_s+170)

    # Motor2 state

    tk.Label(
        root,
        text="Motor2",font='Times 14 bold').place(x=x_d_s+15,y=y_d_s+195)

    motor2_data =tk.Label(
        root,
        text=data["data"][0]["@motor2_status"])
    motor2_data.place(x=x_d_s+215,y=y_d_s+200)

    # Specs Value

    tk.Label(
        root,
        text="Spec",font='Times 14 bold').place(x=x_d_s+15,y=y_d_s+225)

    spec = tk.Label(
        root,
        text="Acquiring")
    spec.place(x=x_d_s+215,y=y_d_s+230)

    # Auxiliary Pump

    tk.Label(
        root,
        text="Aux Pump",font='Times 14 bold').place(x=x_d_s+15,y=y_d_s+255)

    aux_motor_status = tk.Label(
        root,
        text="OFF")
    aux_motor_status.place(x=x_d_s+215,y=y_d_s+260)

    # Cycle 

    tk.Label(
        root,
        text="Cycle",font='Times 14 bold').place(x=x_d_s+15,y=y_d_s+285)

    curr_cycle = tk.Label(
        root,
        text="SLEEP")
    curr_cycle.place(x=x_d_s+215,y=y_d_s+290)

    # Time untill next sample

    tk.Label(
        root,
        text="Time Until Next Sample",font='Times 14 bold').place(x=x_d_s+15,y=y_d_s+315)

    next_sample_time = tk.Label(
        root,
        text="02:10:11")
    next_sample_time.place(x=x_d_s+215,y=y_d_s+320)

    # Number of sample run

    tk.Label(
        root,
        text="Number of Sample Run",font='Times 14 bold').place(x=x_d_s+15,y=y_d_s+345)

    num_of_sample_run = tk.Label(
        root,
        text=data["data"][0]["@num_of_sample_run"])
    num_of_sample_run.place(x=x_d_s+215,y=y_d_s+350)

    tk.Label(
        root,
        text="Blank Sample Absorbances",font='Times 14 bold').place(x=x_d_s+15,y=y_d_s+375)

    blank_sample_absorbances = tk.Label(
        root,
        text=data["data"][0]["@blank_sample_absorbances"])
    blank_sample_absorbances.place(x=x_d_s+215,y=y_d_s+380)

    tk.Label(
        root,
        text="Blank Sample Count",font='Times 14 bold').place(x=x_d_s+15,y=y_d_s+405)

    blank_sample_count = tk.Label(
        root,
        text=data["data"][0]["@blank_sample_count"])
    blank_sample_count.place(x=x_d_s+215,y=y_d_s+410)

    tk.Label(
        root,
        text="Po4 Standard Absorbances",font='Times 14 bold').place(x=x_d_s+15,y=y_d_s+435)

    po4_standard_absorbances = tk.Label(
        root,
        text=data["data"][0]["@po4_standard_absorbances"])
    po4_standard_absorbances.place(x=x_d_s+215,y=y_d_s+440)

    tk.Label(
        root,
        text="Po4 Standard Count",font='Times 14 bold').place(x=x_d_s+15,y=y_d_s+465)

    po4_standard_count = tk.Label(
        root,
        text=data["data"][0]["@po4_standard_count"])
    po4_standard_count.place(x=x_d_s+215,y=y_d_s+470)

    tk.Label(
        root,
        text="Po4 Sample Absorbances",font='Times 14 bold').place(x=x_d_s+15,y=y_d_s+495)

    po4_sample_absorbances = tk.Label(
        root,
        text=data["data"][0]["@po4_sample_absorbances"])
    po4_sample_absorbances.place(x=x_d_s+215,y=y_d_s+500)

    tk.Label(
        root,
        text="Po4 Sample Count",font='Times 14 bold').place(x=x_d_s+15,y=y_d_s+525)

    po4_sample_count = tk.Label(
        root,
        text=data["data"][0]["@po4_sample_count"])
    po4_sample_count.place(x=x_d_s+215,y=y_d_s+530)

    # tk.Label(
    #     root,
    #     text="Num of ports",font='Times 14 bold').place(x=x_d_s+475, y_d_s+125)

    # num_ports = tk.Label(
    #     root,
    #     text=data["data"]["@num_ports"])
    # num_ports.place(x=x_d_s+575,y=y_d_s+130)
    x_d_s_2,y_d_s_2=450,10

    tk.Label(
        root,
        text="Num of ports",font='Times 14 bold').place(x=x_d_s_2+465, y=y_d_s_2+135)

    num_ports = tk.Label(
        root,
        text=data["data"][0]["@num_ports"])
    num_ports.place(x=x_d_s_2+665,y=y_d_s_2+140)
    
    tk.Label(
        root,
        text="port_p1",font='Times 14 bold').place(x=x_d_s_2+465, y=y_d_s_2+165)

    port_p1 = tk.Label(
        root,
        text=data["data"][0]["@port_p1"])
    port_p1.place(x=x_d_s_2+665,y=y_d_s_2+170)

    tk.Label(
        root,
        text="port_p2",font='Times 14 bold').place(x=x_d_s_2+465, y=y_d_s_2+195)

    port_p2 = tk.Label(
        root,
        text=data["data"][0]["@port_p2"])
    port_p2.place(x=x_d_s_2+665,y=y_d_s_2+200)

    tk.Label(
        root,
        text="port_p3",font='Times 14 bold').place(x=x_d_s_2+465, y=y_d_s_2+225)

    port_p3 = tk.Label(
        root,
        text=data["data"][0]["@port_p3"])
    port_p3.place(x=x_d_s_2+665,y=y_d_s_2+230)

    tk.Label(
        root,
        text="port_p4",font='Times 14 bold').place(x=x_d_s_2+465, y=y_d_s_2+255)

    port_p4 = tk.Label(
        root,
        text=data["data"][0]["@port_p4"])
    port_p4.place(x=x_d_s_2+665,y=y_d_s_2+260)

    tk.Label(
        root,
        text="port_p5",font='Times 14 bold').place(x=x_d_s_2+465, y=y_d_s_2+285)

    port_p5 = tk.Label(
        root,
        text=data["data"][0]["@port_p5"])
    port_p5.place(x=x_d_s_2+665,y=y_d_s_2+290)

    tk.Label(
        root,
        text="port_p6",font='Times 14 bold').place(x=x_d_s_2+465, y=y_d_s_2+315)

    port_p6 = tk.Label(
        root,
        text=data["data"][0]["@port_p6"])
    port_p6.place(x=x_d_s_2+665,y=y_d_s_2+320)

    tk.Label(
        root,
        text="port_p7",font='Times 14 bold').place(x=x_d_s_2+465, y=y_d_s_2+345)

    port_p7 = tk.Label(
        root,
        text=data["data"][0]["@port_p7"])
    port_p7.place(x=x_d_s_2+665,y=y_d_s_2+350)

    tk.Label(
        root,
        text="port_p8",font='Times 14 bold').place(x=x_d_s_2+465, y=y_d_s_2+375)

    port_p8 = tk.Label(
        root,
        text=data["data"][0]["@port_p8"])
    port_p8.place(x=x_d_s_2+665,y=y_d_s_2+380)

    x_d_s_3,y_d_s_3=250,10

    tk.Label(
        root,
        text="Port1 PP1speed",font='Times 14 bold').place(x=x_d_s_3+265, y=y_d_s_3+140)

    port1_pp1speed = tk.Label(
        root,
        text=data["data"][0]["@port1_pp1speed"])
    port1_pp1speed.place(x=x_d_s_3+465,y=y_d_s_3+145)

    tk.Label(
        root,
        text="Port1 PP1amount",font='Times 14 bold').place(x=x_d_s_3+265, y=y_d_s_3+160)

    port1_pp1amount = tk.Label(
        root,
        text=data["data"][0]["@port1_pp1amount"])
    port1_pp1amount.place(x=x_d_s_3+465,y=y_d_s_3+165)

    tk.Label(
        root,
        text="Port2 PP1speed",font='Times 14 bold').place(x=x_d_s_3+265, y=y_d_s_3+180)

    port2_pp1speed = tk.Label(
        root,
        text=data["data"][0]["@port2_pp1speed"])
    port2_pp1speed.place(x=x_d_s_3+465,y=y_d_s_3+185)

    tk.Label(
        root,
        text="Port2 PP1amount",font='Times 14 bold').place(x=x_d_s_3+265, y=y_d_s_3+200)

    port2_pp1amount = tk.Label(
        root,
        text=data["data"][0]["@port2_pp1amount"])
    port2_pp1amount.place(x=x_d_s_3+465,y=y_d_s_3+205)

    tk.Label(
        root,
        text="Port3 PP1speed",font='Times 14 bold').place(x=x_d_s_3+265, y=y_d_s_3+220)

    port3_pp1speed = tk.Label(
        root,
        text=data["data"][0]["@port3_pp1speed"])
    port3_pp1speed.place(x=x_d_s_3+465,y=y_d_s_3+225)

    tk.Label(
        root,
        text="Port3 PP1amount",font='Times 14 bold').place(x=x_d_s_3+265, y=y_d_s_3+240)

    port3_pp1amount = tk.Label(
        root,
        text=data["data"][0]["@port3_pp1amount"])
    port3_pp1amount.place(x=x_d_s_3+465,y=y_d_s_3+245)

    tk.Label(
        root,
        text="Port4 PP1speed",font='Times 14 bold').place(x=x_d_s_3+265, y=y_d_s_3+260)

    port4_pp1speed = tk.Label(
        root,
        text=data["data"][0]["@port4_pp1speed"])
    port4_pp1speed.place(x=x_d_s_3+465,y=y_d_s_3+265)

    tk.Label(
        root,
        text="Port4 PP1amount",font='Times 14 bold').place(x=x_d_s_3+265, y=y_d_s_3+280)

    port4_pp1amount = tk.Label(
        root,
        text=data["data"][0]["@port4_pp1amount"])
    port4_pp1amount.place(x=x_d_s_3+465,y=y_d_s_3+285)
    
    tk.Label(
        root,
        text="Port5 PP1speed",font='Times 14 bold').place(x=x_d_s_3+265, y=y_d_s_3+300)

    port5_pp1speed = tk.Label(
        root,
        text=data["data"][0]["@port5_pp1speed"])
    port5_pp1speed.place(x=x_d_s_3+465,y=y_d_s_3+305)

    tk.Label(
        root,
        text="Port5 PP1amount",font='Times 14 bold').place(x=x_d_s_3+265, y=y_d_s_3+320)

    port5_pp1amount = tk.Label(
        root,
        text=data["data"][0]["@port5_pp1amount"])
    port5_pp1amount.place(x=x_d_s_3+465,y=y_d_s_3+325)

    tk.Label(
        root,
        text="Port6 PP1speed",font='Times 14 bold').place(x=x_d_s_3+265, y=y_d_s_3+340)

    port6_pp1speed = tk.Label(
        root,
        text=data["data"][0]["@port6_pp1speed"])
    port6_pp1speed.place(x=x_d_s_3+465,y=y_d_s_3+345)

    tk.Label(
        root,
        text="Port6 PP1amount",font='Times 14 bold').place(x=x_d_s_3+265, y=y_d_s_3+360)

    port6_pp1amount = tk.Label(
        root,
        text=data["data"][0]["@port6_pp1amount"])
    port6_pp1amount.place(x=x_d_s_3+465,y=y_d_s_3+365)

    tk.Label(
        root,
        text="Port7 PP1speed",font='Times 14 bold').place(x=x_d_s_3+265, y=y_d_s_3+380)

    port7_pp1speed = tk.Label(
        root,
        text=data["data"][0]["@port7_pp1speed"])
    port7_pp1speed.place(x=x_d_s_3+465,y=y_d_s_3+385)

    tk.Label(
        root,
        text="Port7 PP1amount",font='Times 14 bold').place(x=x_d_s_3+265, y=y_d_s_3+400)

    port7_pp1amount = tk.Label(
        root,
        text=data["data"][0]["@port7_pp1amount"])
    port7_pp1amount.place(x=x_d_s_3+465,y=y_d_s_3+405)

    tk.Label(
        root,
        text="Port8 PP1speed",font='Times 14 bold').place(x=x_d_s_3+265, y=y_d_s_3+420)

    port8_pp1speed = tk.Label(
        root,
        text=data["data"][0]["@port8_pp1speed"])
    port8_pp1speed.place(x=x_d_s_3+465,y=y_d_s_3+425)

    tk.Label(
        root,
        text="Port8 PP1amount",font='Times 14 bold').place(x=x_d_s_3+265, y=y_d_s_3+440)
    port8_pp1amount = tk.Label(
        root,
        text=data["data"][0]["@port8_pp1amount"])
    port8_pp1amount.place(x=x_d_s_3+465,y=y_d_s_3+445)

def show_data_logs(root,device_info,data):

    tabControl = ttk.Notebook(root, width=1400, height=600)
    tab0 = ttk.Frame(tabControl)
    tab2 = ttk.Frame(tabControl)
    tab3 = ttk.Frame(tabControl)
    tab4 = ttk.Frame(tabControl)
    tab5 = ttk.Frame(tabControl)

    tabControl.add(tab0, text ='All Logs')
    tabControl.add(tab2, text ='Debug')
    tabControl.add(tab3, text ='Command Line')
    tabControl.add(tab4, text ='Status Logs')
    tabControl.add(tab5, text ='Data Logs')

    tabControl.place(x= 1, y=10)
    
    tk.Label(tab0, text="Logs", font='Montserrat 12 bold').place(x=40, y=5)

    if sys.platform == 'darwin':
        def openLogsFolder():
            try:
                subprocess.check_call(['open', '--', os.getcwd()+"/Device/"+device_info[0]+"/logs/"])
            except subprocess.CalledProcessError as e:
                # Handle the error gracefully, or simply ignore it
                print(f"Error/Warning opening folder: {e}")            
    elif sys.platform == 'linux2' or sys.platform == 'linux':
        def openLogsFolder():
            try:
                subprocess.check_call(['xdg-open', '--', os.getcwd()+"/Device/"+device_info[0]+"/logs/"])
            except subprocess.CalledProcessError as e:
                # Handle the error gracefully, or simply ignore it
                print(f"Error/Warning opening folder: {e}")            
    elif sys.platform == 'win32' or sys.platform == 'win64':
        def openLogsFolder():
            try:
                subprocess.check_call(['explorer', os.getcwd()+"\\Device\\"+device_info[0]+"\\logs\\"])
            except subprocess.CalledProcessError as e:
                # Handle the error gracefully, or simply ignore it
                print(f"Error/Warning opening folder: {e}")
            
    btn = tk.Button(tab0, text="More Data",command=openLogsFolder)
    btn.place(x=400, y=5)

    tree = ttk.Treeview(tab0, column=("c1", "c2"), show='headings', height=25)

    tree.column("# 1", anchor=tk.CENTER,stretch=YES,width=150)
    tree.heading("# 1", text="Timestamp")
    tree.column("# 2", anchor=tk.CENTER,stretch=YES,width=900)
    tree.heading("# 2", text="Logs")

    for i in data["logs"][0]["INFO"]:
        # Insert the data in Treeview widget
        tree.insert('', 'end', text="1", values=(i[0],i[1]))
        tree.place(x=40,y=50)
    for i in data["logs"][0]["DEBUG"]:
        # Insert the data in Treeview widget
        tree.insert('', 'end', text="1", values=(i[0],i[1]))
        tree.place(x=40,y=50)
    for i in data["logs"][0]["WARNING"]:
        # Insert the data in Treeview widget
        tree.insert('', 'end', text="1", values=(i[0],i[1]))
        tree.place(x=40,y=50)
    
    tk.Label(tab2, text="Debug", font='Montserrat 12 bold').place(x=40, y=5)
    tree = ttk.Treeview(tab2, column=("c1", "c2"), show='headings', height=5)

    tree.column("# 1", anchor=tk.CENTER,stretch=YES,width=150)
    tree.heading("# 1", text="Timestamp")
    tree.column("# 2", anchor=tk.CENTER,stretch=YES,width=300)
    tree.heading("# 2", text="Logs")
    for i in data["logs"][0]["DEBUG"]:
        # Insert the data in Treeview widget
        tree.insert('', 'end', text="1", values=(i[0],i[1]))
        tree.place(x=40,y=50)
    
    tk.Label(tab2, text='Command Prompt', font='Montserrat 12 bold'
                ).place(x=40, y=290)
                # command prompt box

    txt = scrolledtext.ScrolledText(tab2, height=3, width=60, undo=True,highlightthickness=2,highlightbackground="black")
    txt['font'] = ('consolas', '12')
    txt.place(x=40, y = 315)

    tk.Button(tab2, text="Send Command", font='Montserrat 12 bold', command=lambda: send_command(txt)).place(x=550,y=340)

    tk.Label(tab2, text="Connection Mode", font='Montserrat 12 bold').place(x=600, y=5)
    tree = ttk.Treeview(tab2, column=("c1", "c2"), show='headings', height=5)
    
    tree.column("# 1", anchor=tk.CENTER,stretch=YES,width=150)
    tree.heading("# 1", text="Timestamp")
    tree.column("# 2", anchor=tk.CENTER,stretch=YES,width=300)
    tree.heading("# 2", text="Logs")
    data2={}
    data2["Mode"]=[["2022-08-11_14:57:23","Automatic"],["2022-08-11 14:57:45","Automatic"],["2022-08-11 14:58:07","User Specified"],["2022-08-11 14:58:23","Enter Next State "]]
    for i in data2["Mode"]:
        # Insert the data in Treeview widget
        tree.insert('', 'end', text="1", values=(i[0],i[1]))
        tree.place(x=600,y=50)
    
    tk.Label(tab3, text="Command Line logs", font='Montserrat 12 bold',
            ).place(x=40, y=5)
    tree = ttk.Treeview(tab3, column=("c1", "c2","c3"), show='headings', height=5)

    tree.column("# 1", anchor=tk.CENTER,stretch=YES,width=150)
    tree.heading("# 1", text="Timestamp")
    tree.column("# 2", anchor=tk.CENTER,stretch=YES,width=300)
    tree.heading("# 2", text="Command Executed")
    tree.column("# 3", anchor=tk.CENTER,stretch=YES,width=300)
    tree.heading("# 3", text="Logs")
    
    data2["command_line_logs"]=[["2022-08-11_14:57:23","Command 1","Success/Error"],["2022-08-11 14:57:45","Command 2","Success/Error"],["2022-08-11 14:58:07","Command 3","Success/Error"],["2022-08-11 14:58:23","Command 4","Success/Error"]]
    
    for i in data2["command_line_logs"]:
        # Insert the data in Treeview widget
        tree.insert('', 'end', text="1", values=(i[0],i[1],i[2]))
        tree.place(x=40,y=50)

    tk.Label(tab4, text="Status Logs", font='Montserrat 12 bold',
            ).place(x=40, y=5)
    tree = ttk.Treeview(tab4, column=("c1", "c2"), show='headings', height=5)

    tree.column("# 1", anchor=tk.CENTER,stretch=YES,width=150)
    tree.heading("# 1", text="Time")
    tree.column("# 2", anchor=tk.CENTER,stretch=YES,width=600)
    tree.heading("# 2", text="Status")

    # data2["Status"]=[["Motor1","2022-08-11_14:57:23","On/Off"],["Motor2","2022-08-11 14:57:45","On/Off"],["Aux Pump","2022-08-11 14:58:07","On/Off"],["Spectrophotometer","2022-08-11 14:58:23","On/Off"]]
    # for i in data2["Status"]:
    #     # Insert the data in Treeview widget
    #     tree.insert('', 'end', text="1", values=(i[0],i[1],i[2]))
    #     tree.place(x=40,y=50)
    for i in data["logs"][0]["INFO"]:
        # Insert the data in Treeview widget
        tree.insert('', 'end', text="1", values=(i[0],i[1]))
        tree.place(x=40,y=50)
    
    tk.Label(tab5, text="Data logs", font='Montserrat 12 bold',
            ).place(x=40, y=5)
    tree = ttk.Treeview(tab5, column=("c1", "c2"), show='headings', height=5)

    tree.column("# 1", anchor=tk.CENTER,stretch=YES,width=150)
    tree.heading("# 1", text="Timestamp")
    tree.column("# 2", anchor=tk.CENTER,stretch=YES,width=300)
    tree.heading("# 2", text="Logs")

    for i in data["logs"][0]["WARNING"]:
        # Insert the data in Treeview widget
        tree.insert('', 'end', text="1", values=(i[0],i[1]))
        tree.place(x=40,y=50)

    # tree.insert('', 'end', text="1", values=(date.today(),"Data Logs 1"))
    # tree.insert('', 'end', text="1", values=(date.today(),"Data Logs 2"))
    # tree.insert('', 'end', text="1", values=(date.today(),"Data Logs 3"))
    # tree.place(x=40,y=50)
    
    # fm1 = tk.Frame(root,highlightbackground="black", highlightthickness=2)
    # # top_bg = tk.Canvas(root, width=1500, height=55, bg='#1b2838', highlightthickness=0).place(x=0, y=0)
    # tk.Label(root, text='Logs', font='Montserrat 25', bg='#1b2838', fg='white').place(x=x_d_s+10, y=y_d_s+8)

    # logs1 = tk.Canvas(root, width=320, height=550,highlightthickness=2,highlightbackground="black").place(x=x_d_s+10, y=y_d_s+105)
    # logs1_top = tk.Canvas(root, width=320, height=42, highlightthickness=2,highlightbackground="black").place(x=x_d_s+10, y=y_d_s+85)
    # tk.Label(root, text='Instrument Status', font='Montserrat 12 bold').place(x=x_d_s+18, y=y_d_s+90)

    # logs2 = tk.Canvas(root, width=320, height=550,highlightthickness=2,highlightbackground="black").place(x=x_d_s+330, y=y_d_s+105)
    # logs2_top = tk.Canvas(root, width=320, height=42, highlightthickness=2,highlightbackground="black").place(x=x_d_s+330, y=y_d_s+85)
    # tk.Label(root, text='Instrument Status', font='Montserrat 12 bold').place(x=x_d_s+340, y=y_d_s+90)

    # logs3 = tk.Canvas(root, width=320, height=550,highlightthickness=2,highlightbackground="black").place(x=x_d_s+652, y=y_d_s+105)
    # logs3_top = tk.Canvas(root, width=310, height=42, highlightthickness=2,highlightbackground="black").place(x=x_d_s+652, y=y_d_s+85)
    # tk.Label(root, text='Instrument Status', font='Montserrat 12 bold').place(x=x_d_s+662, y=y_d_s+90)

    # logs4 = tk.Canvas(root, width=310, height=550,highlightthickness=2,highlightbackground="black").place(x=x_d_s+974, y=y_d_s+105)
    # logs4_top = tk.Canvas(root, width=310, height=42, highlightthickness=2,highlightbackground="black").place(x=x_d_s+974, y=y_d_s+85)
    # tk.Label(root, text='Instrument Status', font='Montserrat 12 bold').place(x=x_d_s+984, y=y_d_s+90)
    
def visualize(root,device_info,data,cali_freq):
    options=[]
    for i in data["data"]:
        options.append(i["@Time"])
    dd_blank_sample=[]
    # To add tabs for diffrent graphs
    tabControl = ttk.Notebook(root, width=1400, height=400)
    tab0 = ttk.Frame(tabControl)
    tab2 = ttk.Frame(tabControl)
    tab3 = ttk.Frame(tabControl)
    tab4 = ttk.Frame(tabControl)
    tab5 = ttk.Frame(tabControl)
    tab6 = ttk.Frame(tabControl)
    tab1 = ttk.Frame(tabControl)

    tabControl.add(tab0, text ='Absorbance Spectrums')
    tabControl.add(tab3, text ='Volume Remaining')
    tabControl.add(tab2, text ='Time Series')
    # tabControl.add(tab4, text ='Set Port Positions')
    # tabControl.add(tab5, text ='Set Pump Speed')
    # tabControl.add(tab6, text ='Set Pump Amount')
    # tabControl.add(tab1, text ='Select Mode')
    
    # Place for tabcontrol for graphs 

    ####### Tab for Absorbance Spectrum #######

    tabControl.place(x= 2, y=50)

    fig1,(axs1,axs2,axs3) = plt.subplots(1,3,figsize=(48, 8))

    x = [float(i) for i in data["data"][0]["@Wavelength"][0:1005]]
    y = [float(i) for i in data["data"][0]["@blank_sample_value_2048_1"]]
    z = [float(i) for i in data["data"][0]["@po4_standard_value_2048_1"]]
    w = [float(i) for i in data["data"][0]["@po4_sample_value_2048_1"]]

    lines1 = axs1.plot(x,y,"b")
    axs1.set_xlabel('Wavelength (NM)', fontsize=3, color='b')
    axs1.set_ylabel('blank_sample', fontsize=3, color='b')
    axs1.tick_params(axis='both', which='major', labelsize=3)
    axs1.grid()

    lines2 = axs2.plot(x,z,"r")
    axs2.set_xlabel('Wavelength (NM)', fontsize=3, color='r')
    axs2.set_ylabel('po4_standard', fontsize=3, color='r')
    axs2.tick_params(axis='both', which='major', labelsize=3)
    axs2.grid()

    lines3 = axs3.plot(x,w,"g")
    axs3.set_xlabel('Wavelength (NM)', fontsize=3, color='g')
    axs3.set_ylabel('po4_sample', fontsize=3, color='g')
    axs3.tick_params(axis='both', which='major', labelsize=3)
    axs3.grid()

    plt.subplots_adjust(left=0.2,
                        bottom=0.3, 
                        right=0.8, 
                        top=0.8, 
                        wspace=0.6, 
                        hspace=0.4)

    timeData = StringVar(tab0)
    timeData.set(options[0]) # default value

    w = OptionMenu(tab0, timeData, *options)
    w.pack()
    # w.place(x=500, y=-2)
    
    if sys.platform == 'darwin':
        def openDataFolder():
            try:
                subprocess.check_call(['open', '--', os.getcwd()+"/Device/"+device_info[0]+"/data/"])
            except subprocess.CalledProcessError as e:
                # Handle the error gracefully, or simply ignore it
                print(f"Error/Warning opening folder: {e}")

    elif sys.platform == 'linux2' or sys.platform == 'linux':
        def openDataFolder():
            try:
                subprocess.check_call(['xdg-open', '--', os.getcwd()+"/Device/"+device_info[0]+"/data/"])
            except subprocess.CalledProcessError as e:
                # Handle the error gracefully, or simply ignore it
                print(f"Error/Warning opening folder: {e}")
            
    elif sys.platform == 'win32' or sys.platform == 'win64':
        def openDataFolder():
            try:
                subprocess.check_call(['explorer', os.getcwd()+"\\Device\\"+device_info[0]+"\\data\\"])
            except subprocess.CalledProcessError as e:
                # Handle the error gracefully, or simply ignore it
                print(f"Error/Warning opening folder: {e}")

    btn = tk.Button(tab0, text="More Data",command=openDataFolder)
    btn.place(x=800, y=-2)

    def drop_down(*args):
        for i in data["data"]:
            
            if i["@Time"] == timeData.get():
                print(i["@Time"])
                # print(timeData.get())
                x = [float(j) for j in i["@Wavelength"][0:1005]]
                y = [float(j) for j in i["@blank_sample_value_2048_1"]]
                z = [float(j) for j in i["@po4_standard_value_2048_1"]]
                w = [float(j) for j in i["@po4_sample_value_2048_1"]]
                
                lines1[0].set_ydata(None)
                d = axs1.plot(x,y)
                lines1[0] = d[0]

                lines2[0].set_ydata(None)
                d = axs2.plot(x,z)
                lines2[0] = d[0]

                lines3[0].set_ydata(None)
                d = axs3.plot(x,w)
                lines3[0] = d[0]

                fig1.canvas.draw()
                fig1.canvas.flush_events()
    timeData.trace('w', drop_down)

    # creating the Tkinter canvas that contains the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig1,master = tab0)  
    canvas.draw()

    canvas.get_tk_widget().pack(side = tk.TOP)

    plt.rcdefaults()
    fig, ax = plt.subplots(figsize=(12, 2))

    

    ####### Tab For Absorbance Values vs Time interval #######

    fig2,axs4 = plt.subplots(1,1,figsize=(60, 20))
    
    a = [datetime.strptime(i["@Time"].split("_")[0], '%Y-%m-%d') for i in data["data"]]
    b = [float(i["@blank_sample_absorbances"]) for i in  data["data"]]
    c = [float(i["@po4_standard_absorbances"]) for i in  data["data"]]
    d = [float(i["@po4_sample_absorbances"]) for i in  data["data"]]

    lines4 = axs4.plot(a,c,'b')
    axs4.set_xlabel('Time (Date)', fontsize=3, color='b')
    axs4.set_ylabel('po4_standard_absorbances', fontsize=3, color='b')
    axs4.tick_params(axis='both', which='major', labelsize=3)
    axs4.grid()

    # lines5 = axs5.plot(b,a,'r')
    # axs5.set_xlabel('Time (Date)', fontsize=3, color='r')
    # axs5.set_ylabel('blank_sample_absorbances', fontsize=3, color='r')
    # axs5.tick_params(axis='both', which='major', labelsize=3)
    # axs5.grid()

    # lines6 = axs6.plot(d,a,'g')
    # axs6.set_xlabel('Time (Date)', fontsize=3, color='g')
    # axs6.set_ylabel('po4_sample_absorbances', fontsize=3, color='g')
    # axs6.tick_params(axis='both', which='major', labelsize=3)
    # axs6.grid()

    plt.subplots_adjust(left=0.2,
                        bottom=0.3, 
                        right=0.8, 
                        top=0.8, 
                        wspace=0.6, 
                        hspace=0.4)

    timeData2 = StringVar(tab2)
    timeData2.set(options[0])

    tk.Label(
        tab2,
        text="Start Date",bg="yellow", fg="blue",font='Times 14 bold').place(x=530, y=0)
    # start_date = tk.Label(root,text="",font='Times 14 bold')
    # start_date.place(x=x_d_s+10, y=y_d_s+60)

    w = OptionMenu(tab2, timeData2, *options)
    w.pack()

    timeData3 = StringVar(tab2)
    timeData3.set(options[0])

    tk.Label(
        tab2,
        text="End Date",bg="yellow", fg="blue",font='Times 14 bold').place(x=530, y=25)
    # end_date = tk.Label(root,text="End Date",font='Times 14 bold')
    w = OptionMenu(tab2, timeData3, *options)
    w.pack()

    # canvas = FigureCanvasTkAgg(fig2,master = tab2)  
    # canvas.draw()

    # canvas.get_tk_widget().pack(side = tk.TOP)

    # plt.rcdefaults()
    # figu, axe = plt.subplots(figsize=(12, 2))

    def drop_down(*args):
        start = timeData2.get()
        end  = timeData3.get()
        start = datetime.strptime(start.split("_")[0], '%Y-%m-%d')
        end = datetime.strptime(end.split("_")[0], '%Y-%m-%d')

        a,b,c,d=[],[],[],[]
        for i in data["data"]:
            dt = datetime.strptime(i["@Time"].split("_")[0], '%Y-%m-%d')
            
            if start <= dt < end:
                print("filtered date time : ",i["@Time"])
                # print(timeData.get())
                # a = [datetime.strptime(i["@Time"].split("_")[0], '%Y-%m-%d') for i in data["data"]]
                a.append(datetime.strptime(i["@Time"].split("_")[0], '%Y-%m-%d'))
                b.append(float(i["@blank_sample_absorbances"]))
                c.append(float(i["@po4_standard_absorbances"]))
                #print(float(i["@po4_sample_absorbances"]))
                d.append(float(i["@po4_sample_absorbances"]))
        
        lines4[0].set_ydata(None)
        d = axs4.plot(a,c)
        lines4[0] = d[0]

        # lines5[0].set_ydata(None)
        # d = axs5.plot(b,a)
        # lines5[0] = d[0]

        # lines6[0].set_ydata(None)
        # d = axs6.plot(d,a)
        # lines6[0] = d[0]

        fig2.canvas.draw()
        fig2.canvas.flush_events()
    
    timeData2.trace('w', drop_down)
    timeData3.trace('w', drop_down)

    canvas = FigureCanvasTkAgg(fig2,master = tab2)  
    canvas.draw()

    canvas.get_tk_widget().pack(side = tk.TOP)

    plt.rcdefaults()
    fig3, ax3 = plt.subplots(figsize=(12, 2))
    
    # Example data
    Ascorbic_Acid=abs(float(data["data"][0]["@Ascorbic_Acid_Reagent_remaining"]))/(abs(float(data["data"][0]["@Ascorbic_Acid_Reagent_used"]))+abs(float(data["data"][0]["@Ascorbic_Acid_Reagent_remaining"])))
    Molybdate=abs(float(data["data"][0]["@Molybdate_Reagent_remaining"]))/(abs(float(data["data"][0]["@Molybdate_Reagent_used"]))+abs(float(data["data"][0]["@Molybdate_Reagent_remaining"])))
    PO4=abs(float(data["data"][0]["@PO4_Reagent_remaining"]))/(abs(float(data["data"][0]["@PO4_Reagent_used"]))+abs(float(data["data"][0]["@PO4_Reagent_remaining"])))
    Water=abs(float(data["data"][0]["@water_Reagent_remaining"]))/(abs(float(data["data"][0]["@water_Reagent_used"]))+abs(float(data["data"][0]["@water_Reagent_remaining"])))

    sampleTypes = ('Ascorbic Acid', 'Molybdate', 'PO4', 'Water')
    y_pos = np.arange(len(sampleTypes))
    performance = np.array([int(Ascorbic_Acid*100), int(Molybdate*100), int(PO4*100), int(Water*100)])
    # error = np.random.rand(len(sampleTypes))

    ax.barh(y_pos, performance,align='center')
    ax.set_yticks(y_pos, labels=sampleTypes)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Vol Remaining ( Percentage )',fontsize=3)
    ax.tick_params(axis='both', which='major', labelsize=3)
    plt.subplots_adjust(
                        left=0.2,
                        bottom=0.4, 
                        # right=0.9, 
                        # top=0.99, 
                        # wspace=0, 
                        # hspace=0
                        )
    canvas = FigureCanvasTkAgg(fig,master = tab3)  
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP)

    # tk.Label(
    #     tab4,
    #     text="Port 1 Position",font='Times 14 bold').pack(side=tk.LEFT)

    # tk.Entry(tab4, textvariable=cali_freq).pack(side=tk.LEFT)
    # tab4.update()


    # tk.Label(
    #     tab4,
    #     text="Port 2 Position",font='Times 14 bold').pack(side=tk.LEFT)

    # tk.Entry(tab4, textvariable=cali_freq).pack(side=tk.LEFT)

    # tk.Label(
    #     tab4,
    #     text="Port 3 Position",font='Times 14 bold').pack(side=tk.LEFT)

    # tk.Entry(tab4, textvariable=cali_freq).pack(side=tk.LEFT)

    # tk.Button(tab4, text="Set Position").pack(side=tk.BOTTOM)

    # tk.Label(
    #     tab5,
    #     text="Pump 1 Speed",font='Times 14 bold').pack(side=tk.LEFT)

    # tk.Entry(tab5, textvariable=cali_freq).pack(side=tk.LEFT)


    # tk.Label(
    #     tab5,
    #     text="Pump 1 Speed",font='Times 14 bold').pack(side=tk.LEFT)

    # tk.Entry(tab5, textvariable=cali_freq).pack(side=tk.LEFT)

    # tk.Button(tab5, text="Set Speed").pack(side=tk.BOTTOM)

    # tk.Label(
    #     tab6,
    #     text="Pump 1 Amount",font='Times 14 bold').pack(side=tk.LEFT)

    # tk.Entry(tab6, textvariable=cali_freq).pack(side=tk.LEFT)


    # tk.Label(
    #     tab6,
    #     text="Pump 1 Amount",font='Times 14 bold').pack(side=tk.LEFT)

    # tk.Entry(tab6, textvariable=cali_freq).pack(side=tk.LEFT)

    # tk.Button(tab6, text="Set Amount").pack(side=tk.BOTTOM)

    # var = tk.IntVar()

    # R1 = tk.Radiobutton(tab1, text="Automatic", variable=var, value=1,)
    # R1.pack( anchor = tk.W )

    # R2 = tk.Radiobutton(tab1, text="Blank Sample", variable=var, value=2,
    #                 )
    # R2.pack( anchor = tk.W )

    # R3 = tk.Radiobutton(tab1, text="PO4 Standard", variable=var, value=3,
    #                 )
    # R3.pack( anchor = tk.W)

    # R4 = tk.Radiobutton(tab1, text="PO4 Sample", variable=var, value=4,
    #                 )
    # R4.pack( anchor = tk.W)

    # R5 = tk.Radiobutton(tab1, text="Pause", variable=var, value=5,
    #                 )
    # R5.pack( anchor = tk.W)


    # R6 = tk.Radiobutton(tab1, text="Full Manual", variable=var, value=6,
    #                 )
    # R6.pack( anchor = tk.W)

def check_devices():
    # check if the devices is online or not and then add it to the UI
    temp={}
    for i in devices:
        if devices[i]:
            temp.append()

    return {"PI1":"192.168.5.1"}

def add_data_tabs(root,device_info,device,data,v,sampling_freq,cali_freq):
    #Dashboard creation start from here

    #Top Bar, one with the dashboard written on it
    fm1 = tk.Frame(root,highlightbackground="black", highlightthickness=2)  #Radiobuttons
    top_bg = tk.Canvas(root, width=1400, height=60, bg='#1b2838', highlightthickness=0).place(x=0, y=0)
    tk.Label(root, text='pFIONA', font='Montserrat 25', bg='#1b2838', fg='white').place(x=675, y=0)

    device_data_tab=ttk.Notebook(device, width=1400,height=780)
    device_data_tab.place(x= 0, y=5)

    device_main_dashboard= ttk.Frame(device_data_tab)
    device_meta_data= ttk.Frame(device_data_tab)
    device_logs= ttk.Frame(device_data_tab)
    device_graphs= ttk.Frame(device_data_tab)

    device_data_tab.add(device_main_dashboard,text= "Dashboard")
    device_data_tab.add(device_meta_data,text= "Data")
    device_data_tab.add(device_logs,text= "Logs")
    device_data_tab.add(device_graphs,text= "Graphs")

    #Main dashboard tab
    main_dashboard_tab(device_main_dashboard,device_info,data,v,sampling_freq,cali_freq)

    # Meta data logic
    add_status_and_action(device_meta_data,device_info,data,cali_freq,sampling_freq)
    
    # Data for logs
    show_data_logs(device_logs,device_info,data)

    #Visualization of data
    visualize(device_graphs,device_info,data,cali_freq)

def UI(root):
    
    # root.update()
    style = ttk.Style()
    style.configure("Treeview", foreground='#00337f',background="#ffc61e")
    data = NULL
    root.geometry('1400x780')
    root.title("Dashboard(192.168.0.1)")
    fm3 = tk.Frame(root,highlightbackground="black", highlightthickness=2, width=800, height=220)  #Plots

    # cd = check_devices()
    # if cd:
    devicetab=ttk.Notebook(root, width=1400,height=780)
    devicetab.place(x= 2, y=55)

    #Device Tab Logic

    for i in devices:
        if devices[i]:
            device= ttk.Frame(devicetab)

            print("---get initial data-----")
            data = file_read(devices[i])
            print(type(data["data"]))
            # print(data["logs"][0])
            v = tk.IntVar()
            sampling_freq = tk.StringVar()
            cali_freq = tk.StringVar()

            add_data_tabs(root,devices[i],device,data,v,sampling_freq,cali_freq)

            devicetab.add(device,text= devices[i][0] + " (" +devices[i][1]+ ")")

    # device2= ttk.Frame(devicetab)
    # device3= ttk.Frame(devicetab)

    
    # devicetab.add(device2,text="PI2(IP Adress or name)")
    # devicetab.add(device3,text="PI3(IP Adress or name)")

    # print(data)

    root.after(6000000, refresh, root)       

UI(root)
root.mainloop()
