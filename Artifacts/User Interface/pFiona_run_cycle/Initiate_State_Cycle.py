from time import sleep, time
from Template_Run_New import timer_check,boot,dark_scan,blank_sample_run, po4_standard_run, po4_sample_run,new_txt_data
import threading,os,gc
from os import makedirs
from Template_Run_New import t0,t1,t3
from Template_Run_New import molybdate_port,molybdate_p1_amount,molybdate,molybdate_p1_speed,molybdate_p2_amount,molybdate_p2_speed,molybdatetime,ascorbic_acid_port,ascorbic_p1_amount,ascorbic_p1_speed,ascorbic_acid,ascorbic_p2_amount,ascorbic_p2_speed
from Template_Run_New import n,num_blank_runs,num_standard_runs,refscantime,num_sample_runs,lim_sample_runs,auxtime,ascorbicacidtime,acidreagenttime
from Template_Run_New import blank_sam_run_port_change,blank_sam_run_start_pump,blank_sam_run_wait,po4_std_run_port_change,po4_std_run_start_pump,po4_std_run_wait_time,po4_samp_run_start_AM,po4_samp_run_stop_AM,po4_samp_run_port_change,po4_samp_run_start_pump,po4_samp_run_wait_time
from Template_Run_New import auxMotorOn,current_time,auxMotorOff,move_8ports,stage_reagents,send_speed,send_amount,commit_reagents,flow_cell,reprime,system_flush,lightOff,positions_8_ports,save_list_to_string,dirname,read_reagents
import logging
from Template_Run_New import idle_timer, sample_idle_timer,sleep_time,idle_time
from os.path import exists, abspath, dirname
from Template_Run_New import blank, stand, sample, po4conc_array, sampletime_array
from Template_Run_New import logger
from Template_Run_New import blank_sample_counter, sample_run_counter, standard_sample_counter, total_sample_runs
from Template_Run_New import sample_interval_state_on
from Template_Run_New import n,lim_sample_runs
from Template_Run_New import flush_p1_speed,flush_p1_amount,flush_p2_speed,flush_p2_amount,blank_p1_speed,blank_p1_amount,flow_cell_p1_amount,flow_cell_p1_speed,po4_standard_p1_speed,po4_standard_p1_amount,po4_sample_p1_speed,po4_sample_p1_amount,totalprimes,port1_pp1speed,port1_pp1amount,port2_pp1speed,port2_pp1amount,port2_pp2speed,port2_pp2amount,port3_pp1speed,port3_pp1amount,port4_pp1speed,port4_pp1amount,port5_pp1speed,port5_pp1amount,port6_pp1speed,port6_pp1amount,port7_pp1speed,port7_pp1amount,port8_pp1speed,port8_pp1amount,darkscantime,refscantime,__speed_p1,__amount_p1,__p1_status,__speed_p2,__amount_p2,__p2_status,next_sample_time
from global_variables import state_dict,current_state,next_state
import sys

parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_folder_path)

import Server.commands_queue_server as cqs


lock = threading.Lock()
file_path = str(os.getcwd()) + '\\JSON\\server_command.json'
print(file_path)
modes={"1":"automatic","2":"pause","3":"full manual"}

command={
         "101":"blank sample",
         "102":"po4 standard",
         "103":"po4 sample",
         "104":"Restart",
         "105":"reset cycle",
         "106":"clear data",
         "107":"Flush",
         "108":"data refresh"
         }

def change_mode():
        print(" ::: Status Check For Mode ::: ")
        print("")
        sleep(1)
        device_mode = cqs.get_current_mode(file_path)
        print("Current Mode: ",modes[device_mode])
        print(" ")
        if modes[device_mode] == "automatic":
                print("into full manual")
                print("Current Mode : ",modes[cqs.get_current_mode(file_path)])
                print("The State Machine is in automatic mode, continuing with automatic state cycle")
                print()
                sleep(0.1)

        elif modes[device_mode] == "pause":
                while modes[cqs.get_current_mode(file_path)] == "pause":
                        print("Current Mode: ",modes[cqs.get_current_mode(file_path)])
                        print("Sleeping for 5 second")
                        print("")
                        sleep(5)

        elif modes[device_mode] == "full manual":
                print("into full manual")
                try:
                        while (not  cqs.is_next_button_clicked(file_path)) and modes[cqs.get_current_mode(file_path)] == "full manual":
                                print("Current Mode: ",modes[cqs.get_current_mode(file_path)])
                                print("Please press Next Button to go to next stage")
                                print("Sleeping for 5 second")
                                print("")
                                sleep(5)

                        print("Going to Next Cycle")

                except Exception as e:
                        print(str(e))
                sleep(1)

        elif modes[device_mode] == "user specified":
                blank_sample_error_counter = 3
                po4_standard_error_counter = 3
                po4_sample_error_counter = 3
                flush_error_counter = 3
                reset_cycle_error_counter = 3
                while modes[cqs.get_current_mode(file_path)] == "full manual":
                        cmd = cqs.get_command(file_path)
                        if cmd:
                                print("Current Command: ", command[cmd])

                                #command#101
                                if command[cmd] == "blank sample":
                                        
                                        print("running blank sample for once.")
                                        if blank_sample_error_counter:
                                                try : 
                                                        
                                                
                                                        print("blank_sample_run  succeessfully, please change mode to run command or go into automatic run")

                                                        cqs.remove_command(file_path)
                                                except Exception as e:
                                                        print("Error: ",str(e))
                                                        blank_sample_error_counter -= 1
                                                        print("Error counter for Blank Sample: ",blank_sample_error_counter)
                                        else:
                                                print("Error counter exceeded it's limit, Please check for technical issue")
                                                cqs.remove_command(file_path)
                                                blank_sample_error_counter = 3
                                #command#102
                                elif command[cmd] == "po4 standard":
                                        
                                        print("running po4 standard for once.")
                                        if po4_standard_error_counter:
                                                try:
                                                        po4_standard_run()

                                                        print("po4_standard_run  succeessfully, please change mode to run command or go into automatic run")

                                                        cqs.remove_command(file_path)
                                                except Exception as e:
                                                        print("Error: ",str(e))
                                                        po4_standard_error_counter -= 1
                                                        print("Error counter for Po4 Standard : ",po4_standard_error_counter)
                                        else:
                                                print("Error counter exceeded it's limit, Please check for technical issue")
                                                cqs.remove_command(file_path)
                                                po4_standard_error_counter = 3
                                #command#103
                                elif command[cmd] == "po4 sample":
        
                                        print("running po4 sample for once.")
                                        if po4_sample_error_counter:
                                                try:
                                                        po4_sample_run()

                                                        print("po4_sample_run  succeessfully, please change mode to run command or go into automatic run")
                                                        
                                                        cqs.remove_command(file_path)
                                                except Exception as e:
                                                        print("Error: ",str(e))
                                                        po4_sample_error_counter -= 1
                                                        print("Error counter for Po4 Sample : ",po4_sample_error_counter)
                                        else:
                                                print("Error counter exceeded it's limit, Please check for technical issue")
                                                cqs.remove_command(file_path)
                                                po4_sample_error_counter = 3
                                #command#104
                                elif command[cmd] == "Restart":
                                        
                                        print("Hang tight! :) , Executing Resrart Command")
                                        sleep(3)
                                        # import subprocess
                                        # restart_command = "sudo reboot"
                                        # subprocess.call(restart_command, shell=True)
                                        exit()  
                                        
                                #command#105
                                elif command[cmd] == "reset cycle":
                                        if reset_cycle_error_counter:
                                                try : 
                                                        sleep(1)
                                                        
                                                        # function to find out for reseting cycle
                                                        print("function/s to find out for reseting cycle")

                                                        cqs.remove_command(file_path)
                                                        print("cycle reseted succeessfully, please change mode, to run command or go into automatic run")
                                                except Exception as e:
                                                        print("Error: ",str(e))
                                                        reset_cycle_error_counter -= 1
                                                        print("Error counter for Flush : ",reset_cycle_error_counter)
                                        else:
                                                print("Error counter exceeded it's limit, Please check for technical issue")
                                                cqs.remove_command(file_path)
                                                reset_cycle_error_counter = 3

                                
                                elif command[cmd] == "Flush":
                                        if flush_error_counter:
                                                try : 
                                                        print("System Flush will run for once.")
                                                        system_flush()
                                                        print("System Flush run succeessfully, please change mode to run command or go into automatic run")

                                                        cqs.remove_command(file_path)
                                                except Exception as e:
                                                        print("Error: ",str(e))
                                                        flush_error_counter -= 1
                                                        print("Error counter for Flush : ",flush_error_counter)
                                        else:
                                                print("Error counter exceeded it's limit, Please check for technical issue")
                                                cqs.remove_command(file_path)
                                                flush_error_counter = 3
                                
                                elif command[cmd] == "data refresh":
                                        #data trasfer is not handeled here in this file
                                        print("Data trasfer is not goint to be handeled in this script")
                                        cqs.remove_command(file_path)
                                
                                elif command[cmd] == "clear data":
                                        #data trasfer is not handeled here in this file
                                        print("Data clear is not goint to be handeled in this script")
                                        cqs.remove_command(file_path)
                                
                                else:
                                        print("Current Mode: ",modes[cqs.get_current_mode(file_path)])
                                        print("No Command in Buffer In Pause Mode")
                                        print("Sleeping for 5 second")
                                        print("")
                                        sleep(5)

                                        
                        else:
                                print("There is no command to run, Waiting for client to send a command")
                                sleep(5)

                        sleep(5)

        elif modes[device_mode] == "Error":
                print("Into Error mode")
                sleep(20)
        
        else:
                print("The given mode is not in the list")
                                # SPECTROMETER INITIALIZATION 

def run_new_cycle():

        # global idle_timer, start_time, sample_idle_timer,sleep_time
        # global string_data_file, logger

        global blank, stand, sample, po4conc_array, sampletime_array
        # global ref_spec
        global blank_sample_counter, sample_run_counter, standard_sample_counter, total_sample_runs
        global mean_abs_stand, mean_abs_blank
        global current_state, next_state, sample_interval_state_on,start_time
        global n,lim_sample_runs

        # when reformat events, can combine timers together to be one 
        # evt = check_for_event()
        timer_check()

        '''Moves state machine to next state and runs code for that state'''
        print()
        print("Current State : ", current_state)

        if current_state == state_dict['Boot']: #0
                sleep(0.1)
                
                if boot():
                        next_state = state_dict['Darkscan']
                else:
                        next_state = state_dict['Error']
 
        elif (current_state == state_dict['Darkscan']):#1
                # if no command from user
                sleep(0.1)
                num_sample_runs
                num_blank_runs
                num_standard_runs

                if dark_scan():
                        try:
                                next_state = state_dict['BSR Set Valve to Port 2']
                        except Exception as e:
                                print("Exception: ", e)
                else:
                        next_state = state_dict['Error']

        #blank sample run        
        # fix all the if with having elif and else statement for worst case scenario
        # elif (current_state == state_dict['Blank Sample Run']):#2

                
        elif current_state == state_dict['BSR Set Valve to Port 2']: #21
                print("Blank Sample counter : ", blank_sample_counter)
                if (blank_sample_counter == 0):
                        
                        start_time = time()
                        # text file to hold data and timestamp on creation
                        string_data_file = new_txt_data()
                        blank = [0] * num_blank_runs

                if (blank_sample_counter < num_blank_runs):
                        logging.info(f'**Starting blank run sequence {blank_sample_counter}**')
                        # sleep(refscantime)
                        # ref_spec=spectro_refscan(spec)

                        print("Into Set Valve to Port 2")
                        sleep(0.1)


                        if blank_sam_run_port_change():
                                next_state = state_dict['BSR Start Pump 1']
                        else:
                                next_state = state_dict['Error']
                else:
                        print("condition does not satisfy")
                        next_state = state_dict['PStR Set Valve to Port 6']

        elif current_state == state_dict['BSR Start Pump 1']: #22
                
                sleep(0.1)
                
                if blank_sam_run_start_pump:
                        next_state = state_dict['BSR Wait']
                else:
                        next_state = state_dict['Error']

        elif current_state == state_dict['BSR Wait']: #23
                
                sleep(0.1)

                if blank_sam_run_wait():
                        next_state = state_dict['Acid_Reagent']
                else:
                        next_state = state_dict['Error']

        #p04 standard run devided
        # elif (current_state == state_dict['PO4 Standard Run']):#3
                

        elif current_state == state_dict['PStR Set Valve to Port 6']: #31
                
                print("PO4 Standard counter : ", standard_sample_counter)
                # run section once 
                if (standard_sample_counter == 0):
                        stand = [0] * num_standard_runs

                if (standard_sample_counter < num_standard_runs):
                        logging.info(f'**Starting PO4 standard sequence {standard_sample_counter}**')

                        try:
                                sleep(refscantime)
                                # ref_spec=spectro_refscan(spec)
                                sleep(0.1)
                                if po4_std_run_port_change():
                                        next_state = state_dict['PStR Start Pump 1']
                                else:
                                        next_state = state_dict['Error']
                        
                        except Exception as e:
                                print("Exception: ", e)
                
                else:
                        next_state = state_dict['PSaR Start Aux Motor']

        elif current_state == state_dict['PStR Start Pump 1']: #32
                
                sleep(0.1)
                if po4_std_run_start_pump():
                        next_state = state_dict['PStR Wait']
                else:
                        next_state = state_dict['Error']
        
        elif current_state == state_dict['PStR Wait']: #33
                
                sleep(0.1)

                if po4_std_run_wait_time():
                        next_state = state_dict['Acid_Reagent']
                else:
                        next_state = state_dict['Error']

        #po4 sample run devided

        # elif current_state == state_dict['PO4 Sample Run']: #4
                

        elif current_state == state_dict['PSaR Start Aux Motor']: #41
                
                print("PO4 Sample counter : ", sample_run_counter)
                if (sample_run_counter == 0):
                        sample = [0] * num_sample_runs
                        po4conc_array = [0] * num_sample_runs
                        sampletime_array = [0] * num_sample_runs
                if (sample_run_counter < num_sample_runs):
                        logging.info(f'**Starting PO4 sample sequence {sample_run_counter}**')

                        try:
                                # sleep(refscantime)
                                # ref_spec=spectro_refscan(spec)
                        
                                sleep(0.1)
                                
                                if po4_samp_run_start_AM():
                                        next_state = state_dict['PSaR Stop Aux Motor']
                                else:
                                        next_state = state_dict['Error']
                        except Exception as e:
                                print("Exception: ", e)
                else:
                        print("All the sample taken. Now, moving to save everyhing to TXT file")
                        next_state = state_dict['Create new text and log file']

        elif current_state == state_dict['PSaR Stop Aux Motor']: #42
                
                sleep(0.1)
               
                if po4_samp_run_stop_AM():
                        next_state = state_dict['PSaR Set Valve to Port 4']
                else:
                        next_state = state_dict['Error']

        elif current_state == state_dict['PSaR Set Valve to Port 4']: #43
            
                sleep(0.1)
               
                if po4_samp_run_port_change():
                        next_state = state_dict['PSaR Start Pump 1']
                else:
                        next_state = state_dict['Error']

        elif current_state == state_dict['PSaR Start Pump 1']: #44
            
                sleep(0.1)
                if po4_samp_run_start_pump():
                        next_state = state_dict['PSaR Wait']
                else:
                        next_state = state_dict['Error']

        elif current_state == state_dict['PSaR Wait']: #45
            
                sleep(0.1)
                
                if po4_samp_run_wait_time():
                        next_state = state_dict['Acid_Reagent']
                else:
                        next_state = state_dict['Error']

        #Acid and Reagent flow devided
        elif current_state == state_dict['Acid_Reagent']:#100
                '''depricatred
                
                Pump molybdate reagent then ascorbic reagent then the flow cell and wait 5 min.'''
                print('Into acid_reagent state')
                lock.acquire()
                if True:
                        next_state = state_dict['AR Set Valve to Port 3(reagent)']
                else:
                        next_state = state_dict['Error']
                lock.release()

        elif current_state == state_dict['AR Set Valve to Port 3(reagent)']: #101
                try:
                        lock.acquire()
                        '''Moves the CoV to a specified port then activates pumps to send predetermined amount of fluid at a set speed.'''
                        move_8ports(molybdate_port)        
                        next_state = state_dict['AR Start Pump 1']
                except Exception as e:
                        print("Exception: ", e)
                        next_state = state_dict['Error']
                lock.release()

        elif current_state == state_dict['AR Start Pump 1']: #102
            
                try:
                        lock.acquire()
                        logging.info(f"Dispensing {molybdate_p1_amount} uL pump_1/ Aspirating {abs(molybdate_p2_amount)} uL pump_2") 
                        stage_reagents(molybdate,-molybdate_p1_amount)
                        send_speed(molybdate_p1_speed, 1)                     #Pump 1 moves at speed set by molybdate_p1_speed variable
                        send_amount(molybdate_p1_amount, 1)                   #Pump 1 dispenses amount set by molybdate_p1_amount varaible
                        # sleep(t0)
                        next_state = state_dict['AR Start Pump 2']
                except Exception as e:
                        print("Exception: ", e)
                        next_state = state_dict['Error']
                lock.release()

        elif current_state == state_dict['AR Start Pump 2']: #103
                sleep(0.1)
                try:
                        lock.acquire()
                        stage_reagents(molybdate,-molybdate_p2_amount)   
                        print('stage_reagents done')                
                        send_speed(molybdate_p2_speed, 2)                     #Pump 2 moves at speed set by molybdate_p2_speed variable
                        print('send_speed done')
                        send_amount(molybdate_p2_amount, 2)                   #Pump 2 aspirates amount set by molybdate_p2_amount varaible
                        print('send_amount done')
                        next_state = state_dict['AR Wait 1']
                except Exception as e:
                        print("Exception: ", e)
                        next_state = state_dict['Error']
                lock.release()
        
        elif current_state == state_dict['AR Wait 1']: #104
            
                try:
                        lock.acquire()
                        logging.debug(f'Sleeping for {molybdatetime} seconds')
                        # sleep(molybdatetime)
                        commit_reagents()
                        next_state = state_dict['AR Set Valve to Port 5(acid)']
                except Exception as e:
                        print("Exception: ", e)
                        next_state = state_dict['Error']
                lock.release()

        elif current_state == state_dict['AR Set Valve to Port 5(acid)']: #105
            
                try:
                        lock.acquire()
                        '''Moves the CoV to a specified port then activates pumps to send predetermined amount of fluid at a set speed.'''
                        move_8ports(ascorbic_acid_port)
                        next_state = state_dict['AR Set Valve to Port 2(Dispense solution for Flow Cell)']
                except Exception as e:
                        print("Exception: ", e)
                        next_state = state_dict['Error']
                lock.release()

        elif current_state == state_dict['AR Set Valve to Port 2(Dispense solution for Flow Cell)']: #106
            
                try:
                        lock.acquire()
                        next_state = state_dict['AR Start Pump 1 2']
                        logging.info(f"Aspirating {abs(ascorbic_p1_amount)} uL @ {ascorbic_p1_speed} uL/s pump_1/ Dispensing {ascorbic_p2_amount} uL @ {ascorbic_p2_speed} uL/s pump_2") 

                        stage_reagents(ascorbic_acid, -ascorbic_p1_amount)
                        send_speed(ascorbic_p1_speed, 1)                      #Pump 1 moves at speed set by ascorbic_p1_speed variable
                        send_amount(ascorbic_p1_amount, 1)                    #Pump 1 aspirates amount set by ascorbic_p1_amount varaible
                        sleep(t0)
                except Exception as e:
                        print("Exception: ", e)
                        next_state = state_dict['Error']
                lock.release()

        elif current_state == state_dict['AR Start Pump 1 2']: #107
            
                try:
                        lock.acquire()
                        stage_reagents(ascorbic_acid, -ascorbic_p2_amount)                      
                        send_speed(ascorbic_p2_speed, 2)                      #Pump 2 moves at speed set by ascorbic_p2_speed variable
                        send_amount(ascorbic_p2_amount, 2)                    #Pump 2 aspirates amount set by ascorbic_p2_amount varaible
                        logging.debug(f'Sleeping for {ascorbicacidtime} seconds')
                        next_state = state_dict['AR Wait 2']
                except Exception as e:
                        print("Exception: ", e)
                        next_state = state_dict['Error']
                lock.release()

        elif current_state == state_dict['AR Wait 2']: #108
            
                try:
                        lock.acquire()
                        sleep(0.1)
                        # sleep(ascorbicacidtime)  #Wait for n seconds
                        commit_reagents()
                        flow_cell()
                        logging.debug(f'Sleeping for {acidreagenttime} seconds to mix')
                        # sleep(acidreagenttime)
                        next_state = state_dict['AR Get Absorbances']
                except Exception as e:
                        print("Exception: ", e)
                        next_state = state_dict['Error']
                lock.release()

        elif current_state == state_dict['AR Get Absorbances']: #109
                
                print("Blank sample counter : ",blank_sample_counter)
                print("Standard sample counter : ",standard_sample_counter)
                print("Sample run counter : ",sample_run_counter)
                print()
                lock.acquire()
                try:
                        if blank_sample_counter < num_blank_runs :
                                print("Incrementing blank sample counter")
                                try:
                                        # blank[blank_sample_counter], blank_vals = check_acid_reagent(ref_spec)
                                        blank_vals = ""
                                        logging.debug('Saving absorbances for blank_sample')
                                        prefix = f'@blank_sample_value_2048_{blank_sample_counter+1} @Dim=1'
                                        # save_list_to_string(prefix, blank_vals)
                                        blank_sample_counter += 1
                                        if cqs.get_current_mode(file_path) == "3":
                                                cqs.remove_next_button_clicked()
                                        next_state = state_dict['AR System flush']
                                except Exception as e:
                                        print("Exception: ", e)
                                        next_state = state_dict['Error']
                                print("Blank sample counter incremented to : ",blank_sample_counter)
                        
                        elif standard_sample_counter < num_standard_runs :
                                print("Incrementing standard sample counter")
                                try:
                                        # stand[standard_sample_counter], standard_vals = check_acid_reagent(ref_spec)
                                        logging.debug('Saving absorbances for blank_sample')
                                        prefix = f'@po4_standard_value_2048_{standard_sample_counter+1} @Dim=1'
                                        # save_list_to_string(prefix, standard_vals)
                                        standard_sample_counter += 1
                                        if cqs.get_current_mode(file_path) == "3":
                                                cqs.remove_next_button_clicked()
                                        reprime()
                                        next_state = state_dict['AR System flush']
                                except Exception as e:
                                        print(e)
                                        next_state = state_dict['Error']
                                print("Standard sample counter incremented to : ",standard_sample_counter)
                        
                        elif sample_run_counter < num_sample_runs:
                                print("Incrementing sample run counter")

                                try:
                                        # sample[sample_run_counter], sample_vals  = check_acid_reagent(ref_spec)
                                        logging.debug('Saving absorbances for sample_run')
                                        prefix = f'@po4_sample_value_2048_{sample_run_counter+1} @Dim=1'
                                        # save_list_to_string(prefix, sample_vals)
                                        if (num_standard_runs > 0) and (num_blank_runs > 0):
                                                try:
                                                        po4conc_array[sample_run_counter] = (sample[sample_run_counter]-mean_abs_blank)*(known_concentration/(mean_abs_stand-mean_abs_blank))
                                                except Exception as e:
                                                        print("Issue generated while creating po4conc array",e)
                                                        po4conc_array[sample_run_counter] = "NAN"


                                        else:
                                                po4conc_array[sample_run_counter] = "NAN"

                                        total_sample_runs += 1
                                        sample_run_counter += 1
                                        if cqs.get_current_mode(file_path) == "3":
                                                cqs.remove_next_button_clicked()

                                        reprime()
                        
                                        next_state = state_dict['AR System flush']
                                except Exception as e:
                                        print(e)
                                        next_state = state_dict['Error']
                                print("Sample run counter incremented to : ",sample_run_counter)

                        else:
                                print("Does not satisfy less than condition. So, Last sample run.")
                                next_state = state_dict['AR System flush']
                except Exception as e:
                        print("Exception: ", e)
                        next_state = state_dict['Error']
                lock.release()
        
        elif current_state == state_dict['AR System flush']: #110
                print("Blank sample counter : ",blank_sample_counter , " num_blank_runs : ",num_blank_runs)
                print("Standard sample counter : ",standard_sample_counter, " num_standard_runs : ",num_standard_runs)
                print("Sample run counter : ",sample_run_counter, " num_sample_runs : ", num_sample_runs)
                print()
                
                try:
                        lock.acquire()
                        system_flush()

                        if (blank_sample_counter < num_blank_runs):
                                next_state = state_dict['BSR Set Valve to Port 2']
                
                        elif (blank_sample_counter == num_blank_runs):
                                logging.info('Blank runs complete')
                                next_state = state_dict['PStR Set Valve to Port 6']

                                if len(blank)>0:
                                        mean_abs_blank=sum(blank)/len(blank)
                                else:
                                        mean_abs_blank=0
                                # save_list_to_string('@blank_sample_absorbances', blank)
                                # save_list_to_string('@blank_sample_count', [num_blank_runs])

                                # blank_sample_counter = 0
                                logging.debug(f'New state set: {[index for index in state_dict if state_dict[index] == next_state][0]}')

                        elif (standard_sample_counter < num_standard_runs):
                                next_state = state_dict['PStR Set Valve to Port 6']
                        
                        elif (standard_sample_counter == num_standard_runs):
                                logging.info('Standard runs complete')
                                next_state = state_dict['PSaR Start Aux Motor']
                                
                                if len(stand)>0:
                                        # and standard_sample_counter>0:
                                        
                                        #mean_abs_stand=sum(stand)/len(stand)
                                        # ignores first standard run
                                        mean_abs_stand = mean(stand[-2:])
                                        
                                else:
                                        mean_abs_stand=0
                                # save_list_to_string('@po4_standard_absorbances', stand)
                                # save_list_to_string('@po4_standard_count', [num_standard_runs])

                                # standard_sample_counter = 0
                                logging.debug(f'New state set: {[index for index in state_dict if state_dict[index] == next_state][0]}')

                        elif (sample_run_counter < num_sample_runs):
                                next_state == state_dict['PSaR Start Aux Motor']

                        elif (sample_run_counter == num_sample_runs):
                                logging.info('Sample runs complete')
                                next_state = state_dict['AR Save Absorbances as txt file on device']
                                
                                lightOff()
                                # sample_run_counter = 0

                                logging.debug(f'New state set: {[index for index in state_dict if state_dict[index] == next_state][0]}')

                        else:
                                print("All the sample is done. Start Moving forward with the new sample cycle.")

                except Exception as e:
                        print(e)
                        next_state = state_dict['Error']
                lock.release()
                
        elif current_state == state_dict['AR Save Absorbances as txt file on device']: #111
                string_data_file=""
                try:
                        lock.acquire()
                        logging.info(f'Saving data to {string_data_file}')
                        next_state = state_dict['BSR Set Valve to Port 2']

                        # save_list_to_string('@po4_sample_absorbances', sample)
                        with open(string_data_file, 'a') as f:
                                f.write(f'@po4_sample_count {num_sample_runs}\n')
                                f.write(f'@num_of_sample_run {total_sample_runs}\n')
                                f.write(f'@num_ports {8}\n')
                        for pre, pos in positions_8_ports.items():
                                save_list_to_string(f'@{pre}', [pos])
                        with open(string_data_file, 'a') as f:
                                f.write(f'@monitoringlambda {monitoringlambda}\n')
                                f.write(f'@reflambda {reflambda}\n')
                                f.write(f'@known_concentration {known_concentration}\n')
                        save_list_to_string('@po4_concentrations', po4conc_array)
                        save_list_to_string('@sample_times', sampletime_array)
                        with open(string_data_file, 'a') as f:
                                f.write(f'@flush_p1_speed {flush_p1_speed}\n')
                                f.write(f'@flush_p1_amount {flush_p1_amount}\n')
                                f.write(f'@flush_p2_speed {flush_p2_speed}\n')
                                f.write(f'@flush_p2_amount {flush_p2_amount}\n')
                                f.write(f'@blank_p1_speed {blank_p1_speed}\n')
                                f.write(f'@blank_p1_amount {blank_p1_amount}\n')
                                f.write(f'@molybdate_p1_speed {molybdate_p1_speed}\n')
                                f.write(f'@molybdate_p1_amount {molybdate_p1_amount}\n')
                                f.write(f'@molybdate_p2_speed {molybdate_p2_speed}\n')
                                f.write(f'@molybdate_p2_amount {molybdate_p2_amount}\n')
                                f.write(f'@ascorbic_p1_speed {ascorbic_p1_speed}\n')
                                f.write(f'@ascorbic_p1_amount {ascorbic_p1_amount}\n')
                                f.write(f'@ascorbic_p2_speed {ascorbic_p2_speed}\n')
                                f.write(f'@ascorbic_p2_amount {ascorbic_p2_amount}\n')
                                f.write(f'@flow_cell_p1_speed {flow_cell_p1_speed}\n')
                                f.write(f'@flow_cell_p1_amount {flow_cell_p1_amount}\n')
                                f.write(f'@po4_standard_p1_speed {po4_standard_p1_speed}\n')
                                f.write(f'@po4_standard_p1_amount {po4_standard_p1_amount}\n')
                                f.write(f'@po4_sample_p1_speed {po4_sample_p1_speed}\n')
                                f.write(f'@po4_sample_p1_amount {po4_sample_p1_amount}\n')
                                f.write(f'@totalprimes {totalprimes}\n')
                                f.write(f'@port1_pp1speed {port1_pp1speed}\n')
                                f.write(f'@port1_pp1amount {port1_pp1amount}\n')
                                f.write(f'@port2_pp1speed {port2_pp1speed}\n')
                                f.write(f'@port2_pp1amount {port2_pp1amount}\n')
                                f.write(f'@port2_pp2speed {port2_pp2speed}\n')
                                f.write(f'@port2_pp2amount {port2_pp2amount}\n')
                                f.write(f'@port3_pp1speed {port3_pp1speed}\n')
                                f.write(f'@port3_pp1amount {port3_pp1amount}\n')
                                f.write(f'@port4_pp1speed {port4_pp1speed}\n')
                                f.write(f'@port4_pp1amount {port4_pp1amount}\n')
                                f.write(f'@port5_pp1speed {port5_pp1speed}\n')
                                f.write(f'@port5_pp1amount {port5_pp1amount}\n')
                                f.write(f'@port6_pp1speed {port6_pp1speed}\n')
                                f.write(f'@port6_pp1amount {port6_pp1amount}\n')
                                f.write(f'@port7_pp1speed {port7_pp1speed}\n')
                                f.write(f'@port7_pp1amount {port7_pp1amount}\n')
                                f.write(f'@port8_pp1speed {port8_pp1speed}\n')
                                f.write(f'@port8_pp1amount {port8_pp1amount}\n')
                        vols = read_reagents()
                        with open(string_data_file, 'a') as f:
                                f.write(f'@Ascorbic_Acid_Reagent_used {ascorbic_refill_amt-vols[3]/1000}\n')
                                f.write(f'@Ascorbic_Acid_Reagent_remaining {vols[3]/1000}\n')
                                f.write(f'@Molybdate_Reagent_used {molybdate_refill_amt-vols[0]/1000}\n')
                                f.write(f'@Molybdate_Reagent_remaining {vols[0]/1000}\n')
                                f.write(f'@PO4_Reagent_used {po4_refill_amt-vols[2]/1000}\n')
                                f.write(f'@PO4_Reagent_remaining {vols[2]/1000}\n')
                                f.write(f'@water_Reagent_used {water_refill_amt-vols[1]/1000}\n')
                                f.write(f'@water_Reagent_remaining {vols[1]/1000}\n')
                                f.write(f'@t0 {t0}\n')
                                f.write(f'@t1 {t1}\n')
                                f.write(f'@t3 {t3}\n')
                                f.write(f'@auxtime {auxtime}\n')
                                f.write(f'@darkscantime {darkscantime}\n')
                                f.write(f'@refscantime {refscantime}\n')
                                f.write(f'@time_required {time()-start_time}\n')
                                f.write(f'@aux_motor_status {__aux_motor_status}\n')
                                f.write(f'@motor1_speed {__speed_p1}\n')
                                f.write(f'@motor1_amount {__amount_p1}\n')
                                f.write(f'@motor1_status {__p1_status}\n')
                                f.write(f'@motor2_speed {__speed_p2}\n')
                                f.write(f'@motor2_amount {__amount_p2}\n')
                                f.write(f'@motor2_status {__p2_status}\n')
                                f.write(f'@next_sample_time {next_sample_time}\n')

                        idle_timer.timer_set(new_interval=idle_time)
                        n += 1

                        logging.debug("Creating new log file")
                        timestamp = current_time()
                        logs = dirname(abspath(__file__))+f"/.tmp/{timestamp.split('_')[0]}"
                        if not exists(logs):
                                makedirs(logs)
                        log_file = logs+f"/{timestamp}_pfiona.log"

                        logger.handlers = []
                        fh = logging.FileHandler(log_file)
                        fh.setLevel(logging.DEBUG)
                        fh.setFormatter(logging.Formatter('%(asctime)s (%(threadName)s) %(levelname)s:%(message)s'))
                        logger.addHandler(fh)

                        # free up memory here so we don't crash?
                        print(gc.collect())
                        # del ref_spec

                        # state_var_dict['Save var done'] = True

                        logging.debug(f'Waiting for next cycle')
                        return None
                except Exception as e:
                        print("Error: ",str(e))
                        next_state = state_dict['Error']
                lock.release()

        #If not blank sample run devided
        
        # elif current_state == state_dict['NBSR Set Valve to Port 3(reagent)']: #91
        #         lock.acquire()
        #         sleep(0.1)
        #         t = threading.Thread(target=boot)
        #         t.start()
        #         t.join()
        #         if state_flag:
        #                 next_state = state_dict['NBSR Start Pump 1']
        #         else:
        #                 next_state = state_dict['Error']
        #         lock.release()
            
        # elif current_state == state_dict['NBSR Start Pump 1']: #92
                
        #         sleep(0.1)
        #         t = threading.Thread(target=boot)
        #         t.start()
        #         t.join()
        #         if state_flag:
        #                 next_state = state_dict['NBSR Wait 1']
        #         else:
        #                 next_state = state_dict['Error']

        # elif current_state == state_dict['NBSR Wait 1']: #93
                
        #         sleep(0.1)
        #         t = threading.Thread(target=boot)
        #         t.start()
        #         t.join()
        #         if state_flag:
        #                 next_state = state_dict['NBSR Set Valve to Port 6(PO4 standard)']
        #         else:
        #                 next_state = state_dict['Error']

        # elif current_state == state_dict['NBSR Set Valve to Port 6(PO4 standard)']: #94
                
        #         sleep(0.1)
        #         t = threading.Thread(target=boot)
        #         t.start()
        #         t.join()
        #         if state_flag:
        #                 next_state = state_dict['NBSR Start Pump 1']
        #         else:
        #                 next_state = state_dict['Error']

        # elif current_state == state_dict['NBSR Start Pump 1']: #95
                
        #         sleep(0.1)
        #         t = threading.Thread(target=boot)
        #         t.start()
        #         t.join()
        #         if state_flag:
        #                 next_state = state_dict['NBSR Wait 2']
        #         else:
        #                 next_state = state_dict['Error']

        # elif current_state == state_dict['NBSR Wait 2']: #96
                
        #         sleep(0.1)
        #         t = threading.Thread(target=boot)
        #         t.start()
        #         t.join()
        #         if state_flag:
        #                 next_state = state_dict['Create new text and log file']
        #         else:
        #                 next_state = state_dict['Error']


        #state 71
        elif current_state == state_dict['Save variables to txt file']: #71
                
                sleep(0.1)
                # t = threading.Thread(target=boot)
                # t.start()
                # t.join()
                # if state_flag:
                next_state = state_dict['Create new text and log file']
                # else:
                #         next_state = state_dict['Error']

        elif current_state == state_dict['Create new text and log file']: #72
                
                # sleep(0.1)
                # t = threading.Thread(target=boot)
                # t.start()
                # t.join()
                sleep(0.1)
                # if state_flag:
                next_state = state_dict['Wait for next cycle']
                # else:
                # next_state = state_dict['Error']
        
        elif current_state == state_dict['Wait for next cycle']: #73
                
                # sleep(0.1)
                # t = threading.Thread(target=boot)
                # t.start()
                # t.join()
                sleep(10)
                # if state_flag:
                next_state = state_dict['BSR Set Valve to Port 2']
                blank_sample_counter=0
                standard_sample_counter=0
                sample_run_counter=0

                # else:
                # next_state = state_dict['Error']

        else:
                sleep(1)
                print("Invalid State", current_state)
                state_name = [index for index in state_dict if state_dict[index] == current_state] 
                logging.error(f'{state_name} is not a valid state')
                print('{state_name} is not a valid state')
                raise Exception(f'{state_name} is not a valid state')

        print("Next state: " , next_state)
        current_state = next_state
        print()
        change_mode()
        return 1



if __name__ == '__main__':
        while 1:
                try:
                        device_mode  = cqs.get_current_mode(file_path)
                        if device_mode:
                                print("Current Mode: ",device_mode)
                                while  n < lim_sample_runs:
                                        print("running cycle")
                                        if run_new_cycle():
                                                pass
                                        else:
                                                print("there is some error while running cycle")
                                print("number of cycle specified is completed")
                                sleep(3)
                                change_mode()
                        else:
                                print("There was a issue while fetching a file: final_dashboard\JSON\server_command.json")
                        
                except Exception as e:
                        logging.exception(e)
                        print(e)
                        # GPIO.cleanup()  # commented for test
                        # ser.close() # commented for test
        
       
logging.info("script finished")
