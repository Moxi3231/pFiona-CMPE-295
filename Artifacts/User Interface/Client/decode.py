from datetime import date
import datetime
import re
# importing the required module  
# import matplotlib.pyplot as plt  
# from pathlib import Path
import os

d = date.today()
device_data=["PI1"]

def get_files_from_folder(folder):
    data_files=[]

    data_file_list = os.listdir(folder)
    if '.DS_Store' in data_file_list:
        data_file_list.remove(".DS_Store")
    data_file_list.sort(key=lambda date: datetime.datetime.strptime(date, "%Y-%m-%d"))
    data_file_list=data_file_list[::-1]

    for i in data_file_list:
        try:
            path = folder + i
            data_files.extend(os.listdir(path))
        except :
            break

    data_files = [ (s.split("_")[0] + "/" + s) for s in sorted(data_files)[::-1] ]
    # print(len(data_files))
    return data_files

def read_data_files(file_path):
    data={}
    try:
        f = open(file_path,'r')
        Lines = f.readlines()
        c = 0

        for line in Lines:
            t=line.split()[0]
            if t=="@Time":
                s=line.split()
                data[s[0]]=s[1]
                date=s[1].split("_")[0]
                time=s[1].split("_")[1]
                c+=1
                # print("Time : " + date + " " + time) 
            
            elif t=="@Wavelength":
                s=line.split()[2:2050]
                s.sort(key = float)
                data[t]=s
                c+=1
                # print("Wavelength " ,len(s))
            
            elif t=="@blank_sample_value_2048_1":
                s=line.split()[2:2050]
                # s.sort(key = float)
                data[t]=s
                c+=1
                # print("blank_sample_value_2048_1 " ,len(s))
            
            elif t=="@blank_sample_value_2048_2":
                s=line.split()[2:2050]
                # s.sort(key = float)            
                data[t]=s
                c+=1
                # print("blank_sample_value_2048_1 " ,len(s))
            
            elif t=="@blank_sample_absorbances":
                c+=1
                s=line.split()
                data[s[0]]=s[1]
            
            elif t=="@blank_sample_count":
                c+=1
                s=line.split()
                data[s[0]]=s[1]
            
            elif t=="@po4_standard_value_2048_1":
                
                s=line.split()[2:2050]
                # s.sort(key = float)
                data[t]=s
                c+=1
            
            elif t=="@po4_standard_value_2048_2":
                s=line.split()[2:2050]
                # s.sort(key = float)
                data[t]=s
                c+=1

            elif t=="@po4_standard_value_2048_3":
                s=line.split()[2:2050]
                # s.sort(key = float)
                data[t]=s
                c+=1
            
            elif t=="@po4_standard_absorbances":
                c+=1
                s=line.split()
                data[s[0]]=s[1]
            
            elif t=="@po4_standard_count":
                c+=1
                s=line.split()
                data[s[0]]=s[1]
            
            elif t=="@po4_sample_value_2048_1":
                
                s=line.split()[2:2050]
                # s.sort(key = float)
                data[t]=s
                c+=1
            
            elif t=="@po4_sample_value_2048_2":
                
                s=line.split()[2:2050]
                # s.sort(key = float)
                data[t]=s
                c+=1
            
            elif t=="@po4_sample_value_2048_3":
                
                s=line.split()[2:2050]
                # s.sort(key = float)
                data[t]=s
                c+=1 

            elif t=="@po4_sample_absorbances":
                c+=1
                s=line.split()
                data[s[0]]=s[1]
            
            elif t=="@po4_sample_count":
                c+=1
                s=line.split()
                data[s[0]]=s[1]
            
            elif t=="@num_of_sample_run":
                c+=1
                s=line.split()
                data[s[0]]=s[1]
            
            elif t=="@po4_concentrations":
                c+=1
                s=line.split()
                data[s[0]]=s[1]
            
            elif t=="@num_ports" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]
            
            elif t=="@sample_times" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port_p1" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port_p2" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port_p3" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port_p4" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port_p5" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port_p6" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port_p7" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port_p8" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@monitoringlambda" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@reflambda" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@known_concentration" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@flush_p1_speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@flush_p1_amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@flush_p2_speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@flush_p2_amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@blank_p1_speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@blank_p1_amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@molybdate_p1_speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@molybdate_p1_amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@molybdate_p2_speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@molybdate_p2_amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@ascorbic_p1_speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@ascorbic_p1_amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@ascorbic_p2_speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@ascorbic_p2_amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@flow_cell_p1_speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@flow_cell_p1_amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@po4_standard_p1_speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@po4_standard_p1_amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@po4_sample_p1_speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@po4_sample_p1_amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@totalprimes" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port1_pp1speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port1_pp1amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port2_pp1speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port2_pp1amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port2_pp2speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port2_pp2amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port3_pp1speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port3_pp1amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port4_pp1speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port4_pp1amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port5_pp1speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port5_pp1amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port6_pp1speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port6_pp1amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port7_pp1speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port7_pp1amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port8_pp1speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@port8_pp1amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@Ascorbic_Acid_Reagent_used" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@Ascorbic_Acid_Reagent_remaining" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@Molybdate_Reagent_used" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@Molybdate_Reagent_remaining" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@PO4_Reagent_used":
                c+=1
                s=line.split()
                data[s[0]]=s[1]
            
            elif t=="@PO4_Reagent_remaining":
                c+=1
                s=line.split()
                data[s[0]]=s[1]
            
            elif t=="@water_Reagent_used":
                c+=1
                s=line.split()
                data[s[0]]=s[1]
            
            elif t=="@water_Reagent_remaining":
                c+=1
                s=line.split()
                data[s[0]]=s[1]
            
            elif t=="@t0" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@t1" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@t3" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@auxtime" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@darkscantime" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@refscantime" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@time_required" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@aux_motor_status" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@motor1_speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@motor1_amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@motor1_status" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@motor2_speed" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@motor2_amount" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@motor2_status" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@next_sample_time" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            elif t=="@delay_between_cycle" :
                c+=1
                s=line.split()
                data[s[0]]=s[1]

            else :
                print("This line hasn't been fatched ", line[0:100])
        
        if "@next_sample_time" in line: 
            f.close()
            # print("Data File Scanned : "+file_path.split("data/")[1]+" with lines: "+str(len(Lines)))
            return data

        f.close()
    
        return {}

    except:
        return {}

def read_log_files(file_path):
    data={}
    try :
        f =open(file_path,'r')
        Lines = f.readlines()

        data["INFO"]=[]
        data["DEBUG"]=[]
        data["WARNING"]=[]
        for line in Lines:
            if line != None and "INFO:" in line:
                data["INFO"].append([line.split(",")[0].replace(" ","_"),line.split("INFO:")[1]])
            elif line != None and "DEBUG:" in line:
                data["DEBUG"].append([line.split(",")[0].replace(" ","_"),line.split("DEBUG:")[1]])
            elif line != None and "WARNING:" in line:
                data["WARNING"].append([line.split(",")[0].replace(" ","_"),line.split("WARNING:")[1]])
        
        if "DEBUG:Creating new log file" in line and len(Lines)>60: 
            # print("Log File Scanned : "+file_path.split("logs/")[1]+" with lines: "+str(len(Lines)))
            f.close()
            return data
        f.close()
        return {}
    except Exception as e:
        print(e)
        return {}

def file_read(device_data):
    d={"data":[],"logs":[]}
    data_files = get_files_from_folder(os.getcwd()+"/Device/"+device_data[0]+"/data/")
    
    for i in data_files:
        result = read_data_files(os.getcwd()+"/Device/"+device_data[0]+"/data/"+i)
        if result:
            d["data"].append(result)
    print("Total Data Files Scanned : " + str(len(data_files)))
    print("Filtered Data Files : "+ str(len(d["data"])))

    log_files=get_files_from_folder(os.getcwd()+"/Device/"+device_data[0]+"/logs/")
    for i in log_files:
        result=read_log_files(os.getcwd()+"/Device/"+device_data[0]+"/logs/"+i)
        if result:
            d["logs"].append(result)
    print("Total Log Files Scanned : " + str(len(log_files)))
    print("Filtered Log Files : "+ str(len(d["logs"])))
    # d["data"] = [i for i in d["data"] if i]
    # d["logs"] = [i for i in d["logs"] if i]


    # for i in d["data"]:
    #     if i :
    #         print(len(i))
    #         continue
    #     else:
    #         print()
    #         d["data"].remove(i)
    return d

data=file_read(device_data)
