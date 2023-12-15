import socket
import threading
from os import remove, makedirs, getcwd, listdir
import struct
import logging
from serial import Serial                          
from time import sleep, time
from datetime import date, datetime
from pandas import Series, DataFrame               
from numpy import vstack, shape, array, log10, mean
# import matplotlib.pyplot as plt 
#        
# import RPi.GPIO as GPIO 
# import pdb
from csv import reader, writer
from os.path import exists, abspath, dirname, join, getsize
from os import system as syst
import sys
from shutil import rmtree
import gc
import os
from global_variables import state_dict,current_state, next_state

lock = threading.Lock()

HOST = '0.0.0.0'
PORT1 = 8097       # Port to listen on (non-privileged ports are > 1023)
PORT2 = 8052

                                # CREATE LOG FILE 
timestamp = str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')[:-7])

logs = dirname(abspath(__file__))+f"/.tmp/{timestamp.split('_')[0]}"
if not exists(logs):
        makedirs(logs)
log_file = logs+f"/{timestamp}_pfiona.log"

logging.basicConfig(filename=log_file,
                format='%(asctime)s (%(threadName)s) %(levelname)s:%(message)s',
                filemode='w',
                level=logging.DEBUG)
# Creating an object
logger = logging.getLogger()

                                # CREATE DIRECTORIES AND FILES 
parent_repo_directory = dirname(dirname(abspath(__file__)))
base_save_directory = f'{parent_repo_directory}/pFIONA/saved_data/'
if not exists(dirname(base_save_directory)):
        makedirs(dirname(base_save_directory))

# stage amount used to file to be committed in case of power loss

if sys.platform == 'win32':
    tmp_stage_file = join(dirname(abspath(__file__)), '.tmp\\staged_reagents.csv')

elif sys.platform == 'linux' or sys.platform == 'linux2':
    tmp_stage_file = join(dirname(abspath(__file__)), '.tmp/staged_reagents.csv')
    
elif sys.platform == 'darwin':
    tmp_stage_file = join(dirname(abspath(__file__)), '.tmp/staged_reagents.csv')

if not exists(dirname(tmp_stage_file)):
        file_path = join(dirname(tmp_stage_file), 'staged_reagents.csv')
        if exists(file_path):
                print("reagents file exists!")
        else:
                print("Directory ",tmp_stage_file, "does not exist. So, creatig new one")
                makedirs(dirname(tmp_stage_file))

tracker_name = base_save_directory+'reagents.csv' 

# STATE MACHINE DEFINITION 


def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def check_device_data(dir):
    return round(get_size(dir)/(10**9),2)


command_dict = {  # item is what's received from socket, key is for readability
        'REBOOT': 'REBOOT', 'IDLE': 'IDLE', 'SHUTDOWN': 'SHUTDOWN', 
        'FLUSH': 'FLUSH', 'CLEAR DATA': 'CLEAR DATA','SEND LAST DATA': 'REFRESH', 
        'STATUS UPDATE': 'UPDATE', 'STATE DARKSCAN': 'STATE DARKSCAN',
        'STATE BLANK': 'STATE BLANK', 'STATE STANDARD': 'STATE STANDARD',
        'STATE SAMPLE': 'STATE SAMPLE', 'FLUSH': 'FLUSH', 'PARAM': 'PARAM'
}


# # "remove commands (101) ","restart (102)","flush (103)","refresh data (104)",
# commands=["","102","103","104","105"]

# Automatic, Pause, Full Manual

param_dict = []

# ser = Serial('/dev/ttyUSB0') # commented for test

# if the spectrometer connection is not closed properly like through a service
# this causes subsequent runs to stall at device initialization

# commented for test

# from seabreeze.pyseabreeze.api import SeaBreezeAPI
# seaAPI = SeaBreezeAPI()
# # force the connection closed so it can be used
# devs = seaAPI.list_devices()[0].close()

# from seabreeze.spectrometers import Spectrometer
# spec = Spectrometer.from_first_available()
# spec.integration_time_micros(60000)  # integration time in microseconds

# define monitoring and reference wavelengths to be used
monitoringlambda = 880
reflambda = 1050

#known concentration of standards (units of micromolar)
known_concentration = 2

# fluids to track
molybdate = 'MOLYBDATE'
water = 'WATER'
po4 = 'PO4'
ascorbic_acid = 'ASCORBIC'

# default refill amounts used on file creation
molybdate_refill_amt = 15  # mL
water_refill_amt = 500  # mL
po4_refill_amt = 15  # mL
ascorbic_refill_amt = 80  # mL

# minimum amount of reagent level before warning
reagent_warning_percent = 0.10  # minimum percent for every 
reagent_operating_percent = 0.02 # PUMP SPEED VARIABLES
#System Flush
flush_p1_speed = 100                    # pump 1 speed in uL/sec      
flush_p1_amount = 2000                  # pump 1 amount in uL (+ for dispense, - for aspirate)
flush_p2_speed = 100                    # pump 2 speed in uL/sec
flush_p2_amount = 2000                  # pump 2 amount in uL (+ for dispense, - for aspirate)         

#Blank Sample
blank_p1_speed = 60                     # pump 1 speed in uL/sec 
blank_p1_amount = 600                   # pump 1 amount in uL (+ for dispense, - for aspirate)

#Molybdate Reagent
molybdate_p1_speed = 32                 # pump 1 speed in uL/sec 
molybdate_p1_amount = 320               # pump 1 amount in uL (+ for dispense, - for aspirate)
molybdate_p2_speed = 40                 # pump 2 speed in uL/sec
molybdate_p2_amount = -400              # pump 2 amount in uL (+ for dispense, - for aspirate)

#Ascorbic Acid Reagent
ascorbic_p1_speed = 40                  # pump 1 speed in uL/sec
ascorbic_p1_amount = -400               # pump 1 amount in uL (+ for dispense, - for aspirate)
ascorbic_p2_speed = 32                  # pump 2 speed in uL/sec
ascorbic_p2_amount = 320                # pump 2 amount in uL (+ for dispense, - for aspirate)

#Flow Cell
flow_cell_p1_speed = 25                 # pump 1 speed in uL/sec
flow_cell_p1_amount = 400               # pump 1 amount in uL (+ for dispense, - for aspirate)

#PO4 Standard
po4_standard_p1_speed = 60              # pump 1 speed in uL/sec
po4_standard_p1_amount = -600           # pump 1 amount in uL (+ for dispense, - for aspirate)

#PO4 Sample
po4_sample_p1_speed = 60                # pump 1 speed in uL/sec
po4_sample_p1_amount = -600             # pump 1 amount in uL (+ for dispense, - for aspirate)

#AFTER RUNf
after_p1_speed = 50                     # pump 1 speed in uL/sec
after_p1_amount = -150                  # pump 1 amount in uL (+ for dispense, - for aspirate)

                                # PUMP PRIMING VARAIBLES

totalprimes = 3                      # indicates number of times prime cycle should repeat (set by end-user)

port1_pp1speed = 100                    # port 1, pump 1, priming speed in uL/sec
port1_pp1amount = 1000                  # port 1, pump 1, priming amount uL (+ for dispense, - for aspirate)

port2_pp1speed = 150                    # port 2, pump 1, priming speed in uL/sec
port2_pp1amount = 1000                  # port 2, pump 1, priming amount uL (+ for dispense, - for aspirate)
port2_pp2speed = 150                    # port 2, pump 2, priming speed in uL/sec
port2_pp2amount = 1000                  # port 2, pump 1, priming amount uL (+ for dispense, - for aspirate)

port3_pp1speed = 100                    # port 3, pump 1, priming speed in uL/sec
port3_pp1amount = -200                  # port 3, pump 1, priming amount uL (+ for dispense, - for aspirate)

port4_pp1speed = 100                    # port 4, pump 1, priming speed in uL/sec
port4_pp1amount = -200                  # port 4, pump 1, priming amount uL (+ for dispense, - for aspirate)

port5_pp1speed = 100                    # port 5, pump 1, priming speed in uL/sec
port5_pp1amount = -200                  # port 5, pump 1, priming amount uL (+ for dispense, - for aspirate)

port6_pp1speed = 100                    # port 6, pump 1, priming speed in uL/sec
port6_pp1amount = -200                  # port 6, pump 1, priming amount uL (+ for dispense, - for aspirate)

port7_pp1speed = 100                    # port 7, pump 1, priming speed in uL/sec
port7_pp1amount = -200                  # port 7, pump 1, priming amount uL (+ for dispense, - for aspirate)

port8_pp1speed = 100                    # port 8, pump 1, priming speed in uL/sec
port8_pp1amount = -200                  # port 8, pump 1, priming amount uL (+ for dispense, - for aspirate)

__amount_p1 = 0
__amount_p2 = 0
__speed_p1 = 0
__speed_p2 = 0
__p1_status = False
__p2_status = False
__light_status = 'OFF'

                                # PORT POSITIONS

waste_port = 1
flow_cell_port = 2
molybdate_port = 3
ascorbic_acid_port = 4
sample_port = 5
po4_port = 6
blank_port = 7

port_current = None  # starts indeterminate
positions_8_ports = {
        'port_p1': 1275, 'port_p2': 1075, 'port_p3': 887,
        'port_p4': 700, 'port_p5': 530, 'port_p6': 350,
        'port_p7': 170, 'port_p8': 0, 'port_p9': 988
}

                                # TIME VARIABLES

# time to wait until next cycle
idle_time = 710                         # Time in between full cycles. Units in seconds
next_sample_time = 3011                 # Time in between following sample runs, Units in seconds

t0 = 0.001                              # time for running pumps simutaneously
t1 = 5                                  # sleep time for valve movement and pump pause ( may be adjusted to suit end-user needs)
t3 = 30                                 # flow cell wait time for absorbance measurement (set based on end-user needs). Note this variable is no longer used and replaced by acidreagenttime
auxtime = 120                           # aux pump time for drawing sample seawater to refill sample (set based on end-user needs)
darkscantime = 5
refscantime = 5
lamptime = 30
acidreagenttime = 60*5                                                          # time to wait for chems to mix before spec
flushtime = abs(flush_p1_amount/flush_p1_speed)+t1                              # This area calculates the time needed for pumps to run.
blanktime = abs(blank_p1_amount/blank_p1_speed)+t1                              # It takes the absolute value of the pump 1 ratio of amount
molybdatetime = abs(molybdate_p1_amount/molybdate_p1_speed)+t1                  # of volume to move and the speed at which the volume is moved.
po4sampletime = abs(po4_sample_p1_amount/po4_sample_p1_speed)+t1                # This is done to ensure accurate numbers due to dispensing and
po4standardtime = abs(po4_standard_p1_amount/po4_standard_p1_speed)+t1          # aspirating values being +-. This value is then added to sleep
ascorbicacidtime = abs(ascorbic_p1_amount/ascorbic_p1_speed)+t1                 # time for valve movement and pump pause to ensure adequate time
flowcelltime = abs(flow_cell_p1_amount/flow_cell_p1_speed)+t1                   # for sequence to finish.
reprimetime = abs(after_p1_amount/after_p1_speed)+t1                              # for priming ports after run
p1primetime = abs(port1_pp1amount/port1_pp1speed)+t1   
p2primetime = abs(port2_pp1amount/port2_pp1speed)+t1
p3primetime = abs(port3_pp1amount/port3_pp1speed)+t1
p4primetime = abs(port4_pp1amount/port4_pp1speed)+t1
p5primetime = abs(port5_pp1amount/port5_pp1speed)+t1
p6primetime = abs(port6_pp1amount/port6_pp1speed)+t1
p7primetime = abs(port7_pp1amount/port7_pp1speed)+t1
p8primetime = abs(port8_pp1amount/port8_pp1speed)+t1

# non blocking timer class to allow for socket/userinput during operation
class timer():
        '''Creates a nonblocking timer to trigger a timer event when checked. Use timer_set to start the timer.
        Units: Seconds

        EX. Start and check a 90 second timer
        new_timer = timer(90)
        new_timer.timer_set()
        time.sleep(80)
        event = False
        while not event:
                event = new_timer.timer_event()
                if event:
                        print("timer complete")
                else:
                        time.sleep(1)'''

        timer_time = None

        def __init__(self, interval: float):
                try:
                        self.TIMER_INTERVAL = float(interval)
                except ValueError as e:
                        logging.warning(f'Invalid timer input: {e}\nSetting interval to None')
                        self.TIMER_INTERVAL = None

        def timer_event(self) -> bool:
                '''Checks to see if the time has passed. If it has, turns off timer and returns True. If the timer was not set,
                returns None'''
                if (self.timer_time is not None) and time() >= self.timer_time:
                        self.timer_time = None
                        logging.debug(f'{self.TIMER_INTERVAL} second long timer completed')
                        return True
                elif self.timer_time is None:
                        return None
                else:
                        return False

        def timer_event_no_reset(self) -> bool:
                '''Checks to see if the time has passed. If it has, returns True. Must be manually stopped/reset'''
                if (self.timer_time is not None) and time() >= self.timer_time:
                        # self.timer_time = None
                        return True
                elif self.timer_time is None:
                        return None
                else:
                        return False

        def timer_set(self, new_interval:float=None) -> bool:
                '''Restarts timer from time of method call'''
                if (type(new_interval) is int) or (type(new_interval) is float):
                        self.TIMER_INTERVAL = new_interval
                try:
                        self.timer_time = time() + self.TIMER_INTERVAL
                        return True
                except TypeError as e:
                        if self.TIMER_INTERVAL is None:
                                logging.info("Timer interval set to None")
                                self.timer_time = None
                        else:
                                logging.error(f'Invalid timer operation: timer interval = {self.TIMER_INTERVAL}')
                        return False

        def time_remaining(self) -> float:
                '''Checks to see if the time has passed. If it not, returns float of difference. No reset if time has passed'''
                if self.timer_time is None:
                        return None
                else:            
                        if time() >= self.timer_time:
                                return None
                        else:
                                return self.timer_time - time()

lamp_timer = timer(lamptime)
mix_timer = timer(acidreagenttime)
idle_timer = timer(idle_time)
sample_idle_timer = timer(next_sample_time)
sample_interval_state_on=False

                                # AUX MOTOR AND LIGHTSOURCE PIN CALLOUT
motorPin=17                     # Define Pins for aux motor and lightsourcemove_8ports
ledPin=27

                                # OPERATION PARAMETERS
num_blank_runs = 2
num_standard_runs = 3
num_sample_runs = 3

blank = [0] * num_blank_runs
stand = [0] * num_standard_runs
sample = [0] * num_sample_runs
po4conc_array = [0] * num_sample_runs
sampletime_array = [0] * num_sample_runs


blank_sample_counter = 0
standard_sample_counter = 0
sample_run_counter = 0

# track to send to ui
total_sample_runs = 0

lim_sample_runs = 300 #user input depending on how long to run continuously. Refers to total full cycles to run for a deployment. 
n=0 #keep at 0. This value is used to track the number of full cycles which have been run. 

                                # FILE HANDLING

# string to send data over
string_data=""

wavelengths = "632.7474 633.2126 633.6778 634.1430 634.6082 635.0735 635.5387 636.0041 636.4694 636.9348 637.4002 637.8657 638.3311 638.7966 639.2622 639.7277 640.1933 640.6590 641.1246 641.5903 642.0560 642.5218 642.9876 643.4534 643.9192 644.3851 644.8510 645.3169 645.7829 646.2489 646.7149 647.1810 647.6471 648.1132 648.5793 649.0455 649.5117 649.9780 650.4442 650.9105 651.3769 651.8432 652.3096 652.7760 653.2425 653.7090 654.1755 654.6420 655.1086 655.5752 656.0419 656.5085 656.9752 657.4420 657.9087 658.3755 658.8423 659.3092 659.7761 660.2430 660.7099 661.1769 661.6439 662.1109 662.5780 663.0451 663.5122 663.9794 664.4466 664.9138 665.3810 665.8483 666.3156 666.7830 667.2503 667.7177 668.1852 668.6526 669.1201 669.5876 670.0552 670.5228 670.9904 671.4580 671.9257 672.3934 672.8612 673.3289 673.7967 674.2646 674.7324 675.2003 675.6682 676.1362 676.6042 677.0722 677.5402 678.0083 678.4764 678.9445 679.4127 679.8809 680.3491 680.8174 681.2857 681.7540 682.2223 682.6907 683.1591 683.6276 684.0960 684.5645 685.0331 685.5016 685.9702 686.4389 686.9075 687.3762 687.8449 688.3137 688.7824 689.2512 689.7201 690.1890 690.6579 691.1268 691.5957 692.0647 692.5338 693.0028 693.4719 693.9410 694.4102 694.8793 695.3485 695.8178 696.2870 696.7563 697.2257 697.6950 698.1644 698.6338 699.1033 699.5728 700.0423 700.5118 700.9814 701.4510 701.9206 702.3903 702.8600 703.3297 703.7994 704.2692 704.7391 705.2089 705.6788 706.1487 706.6186 707.0886 707.5586 708.0286 708.4987 708.9688 709.4389 709.9090 710.3792 710.8494 711.3197 711.7900 712.2603 712.7306 713.2010 713.6714 714.1418 714.6123 715.0827 715.5533 716.0238 716.4944 716.9650 717.4356 717.9063 718.3770 718.8478 719.3185 719.7893 720.2601 720.7310 721.2019 721.6728 722.1437 722.6147 723.0857 723.5568 724.0278 724.4989 724.9701 725.4412 725.9124 726.3836 726.8549 727.3262 727.7975 728.2688 728.7402 729.2116 729.6831 730.1545 730.6260 731.0976 731.5691 732.0407 732.5123 732.9840 733.4557 733.9274 734.3991 734.8709 735.3427 735.8145 736.2864 736.7583 737.2302 737.7022 738.1741 738.6462 739.1182 739.5903 740.0624 740.5345 741.0067 741.4789 741.9511 742.4234 742.8957 743.3680 743.8404 744.3128 744.7852 745.2576 745.7301 746.2026 746.6751 747.1477 747.6203 748.0929 748.5656 749.0383 749.5110 749.9837 750.4565 750.9293 751.4022 751.8751 752.3480 752.8209 753.2939 753.7669 754.2399 754.7129 755.1860 755.6591 756.1323 756.6055 757.0787 757.5519 758.0252 758.4985 758.9718 759.4452 759.9186 760.3920 760.8655 761.3389 761.8125 762.2860 762.7596 763.2332 763.7068 764.1805 764.6542 765.1279 765.6017 766.0755 766.5493 767.0231 767.4970 767.9709 768.4449 768.9189 769.3929 769.8669 770.3410 770.8151 771.2892 771.7633 772.2375 772.7117 773.1860 773.6603 774.1346 774.6089 775.0833 775.5577 776.0321 776.5066 776.9811 777.4556 777.9302 778.4047 778.8794 779.3540 779.8287 780.3034 780.7781 781.2529 781.7277 782.2025 782.6774 783.1523 783.6272 784.1022 784.5771 785.0521 785.5272 786.0023 786.4774 786.9525 787.4277 787.9029 788.3781 788.8534 789.3286 789.8040 790.2793 790.7547 791.2301 791.7055 792.1810 792.6565 793.1320 793.6076 794.0832 794.5588 795.0345 795.5102 795.9859 796.4616 796.9374 797.4132 797.8891 798.3649 798.8408 799.3168 799.7927 800.2687 800.7447 801.2208 801.6969 802.1730 802.6491 803.1253 803.6015 804.0777 804.5540 805.0303 805.5066 805.9830 806.4594 806.9358 807.4122 807.8887 808.3652 808.8418 809.3183 809.7949 810.2716 810.7482 811.2249 811.7017 812.1784 812.6552 813.1320 813.6089 814.0857 814.5627 815.0396 815.5166 815.9936 816.4706 816.9477 817.4247 817.9019 818.3790 818.8562 819.3334 819.8107 820.2879 820.7652 821.2426 821.7199 822.1973 822.6748 823.1522 823.6297 824.1072 824.5848 825.0624 825.5400 826.0176 826.4953 826.9730 827.4507 827.9285 828.4063 828.8841 829.3620 829.8399 830.3178 830.7957 831.2737 831.7517 832.2297 832.7078 833.1859 833.6640 834.1422 834.6204 835.0986 835.5769 836.0552 836.5335 837.0118 837.4902 837.9686 838.4470 838.9255 839.4040 839.8825 840.3611 840.8397 841.3183 841.7969 842.2756 842.7543 843.2331 843.7119 844.1907 844.6695 845.1484 845.6273 846.1062 846.5851 847.0641 847.5431 848.0222 848.5013 848.9804 849.4595 849.9387 850.4179 850.8971 851.3764 851.8557 852.3350 852.8143 853.2937 853.7731 854.2526 854.7321 855.2116 855.6911 856.1707 856.6503 857.1299 857.6096 858.0893 858.5690 859.0487 859.5285 860.0083 860.4882 860.9680 861.4479 861.9279 862.4078 862.8878 863.3679 863.8479 864.3280 864.8081 865.2883 865.7685 866.2487 866.7289 867.2092 867.6895 868.1698 868.6502 869.1306 869.6110 870.0914 870.5719 871.0524 871.5330 872.0136 872.4942 872.9748 873.4555 873.9362 874.4169 874.8977 875.3785 875.8593 876.3401 876.8210 877.3019 877.7829 878.2638 878.7448 879.2259 879.7069 880.1880 880.6692 881.1503 881.6315 882.1127 882.5940 883.0753 883.5566 884.0379 884.5193 885.0007 885.4821 885.9636 886.4451 886.9266 887.4081 887.8897 888.3713 888.8530 889.3347 889.8164 890.2981 890.7799 891.2617 891.7435 892.2254 892.7073 893.1892 893.6711 894.1531 894.6351 895.1172 895.5993 896.0814 896.5635 897.0457 897.5279 898.0101 898.4923 898.9746 899.4569 899.9393 900.4217 900.9041 901.3865 901.8690 902.3515 902.8340 903.3166 903.7992 904.2818 904.7645 905.2472 905.7299 906.2126 906.6954 907.1782 907.6610 908.1439 908.6268 909.1097 909.5927 910.0757 910.5587 911.0418 911.5248 912.0080 912.4911 912.9743 913.4575 913.9407 914.4240 914.9073 915.3906 915.8740 916.3574 916.8408 917.3242 917.8077 918.2912 918.7748 919.2583 919.7419 920.2256 920.7092 921.1929 921.6767 922.1604 922.6442 923.1280 923.6119 924.0957 924.5796 925.0636 925.5476 926.0316 926.5156 926.9996 927.4837 927.9679 928.4520 928.9362 929.4204 929.9047 930.3889 930.8732 931.3576 931.8419 932.3263 932.8108 933.2952 933.7797 934.2642 934.7488 935.2334 935.7180 936.2026 936.6873 937.1720 937.6567 938.1415 938.6263 939.1111 939.5960 940.0809 940.5658 941.0507 941.5357 942.0207 942.5057 942.9908 943.4759 943.9610 944.4462 944.9314 945.4166 945.9019 946.3872 946.8725 947.3578 947.8432 948.3286 948.8140 949.2995 949.7850 950.2705 950.7561 951.2417 951.7273 952.2129 952.6986 953.1843 953.6701 954.1559 954.6417 955.1275 955.6134 956.0993 956.5852 957.0711 957.5571 958.0431 958.5292 959.0153 959.5014 959.9875 960.4737 960.9599 961.4461 961.9324 962.4187 962.9050 963.3914 963.8777 964.3642 964.8506 965.3371 965.8236 966.3101 966.7967 967.2833 967.7699 968.2566 968.7433 969.2300 969.7167 970.2035 970.6903 971.1772 971.6640 972.1509 972.6379 973.1248 973.6118 974.0989 974.5859 975.0730 975.5601 976.0473 976.5345 977.0217 977.5089 977.9962 978.4835 978.9708 979.4582 979.9456 980.4330 980.9204 981.4079 981.8954 982.3830 982.8706 983.3582 983.8458 984.3335 984.8212 985.3089 985.7967 986.2845 986.7723 987.2601 987.7480 988.2359 988.7239 989.2118 989.6998 990.1879 990.6759 991.1640 991.6522 992.1403 992.6285 993.1167 993.6050 994.0933 994.5816 995.0699 995.5583 996.0467 996.5351 997.0236 997.5121 998.0006 998.4892 998.9777 999.4664 999.9550 1000.443 1000.932 1001.421 1001.909 1002.398 1002.887 1003.376 1003.865 1004.354 1004.843 1005.332 1005.821 1006.310 1006.799 1007.288 1007.777 1008.266 1008.755 1009.245 1009.734 1010.223 1010.713 1011.202 1011.691 1012.181 1012.670 1013.160 1013.649 1014.139 1014.628 1015.118 1015.607 1016.097 1016.587 1017.076 1017.566 1018.056 1018.546 1019.036 1019.525 1020.015 1020.505 1020.995 1021.485 1021.975 1022.465 1022.955 1023.446 1023.936 1024.426 1024.916 1025.406 1025.897 1026.387 1026.877 1027.368 1027.858 1028.348 1028.839 1029.329 1029.820 1030.310 1030.801 1031.292 1031.782 1032.273 1032.763 1033.254 1033.745 1034.236 1034.727 1035.217 1035.708 1036.199 1036.690 1037.181 1037.672 1038.163 1038.654 1039.145 1039.636 1040.128 1040.619 1041.110 1041.601 1042.092 1042.584 1043.075 1043.567 1044.058 1044.549 1045.041 1045.532 1046.024 1046.515 1047.007 1047.499 1047.990 1048.482 1048.974 1049.465 1049.957 1050.449 1050.941 1051.433 1051.924 1052.416 1052.908 1053.400 1053.892 1054.384 1054.876 1055.368 1055.861 1056.353 1056.845 1057.337 1057.829 1058.322 1058.814 1059.306 1059.799 1060.291 1060.784 1061.276 1061.769 1062.261 1062.754 1063.246 1063.739 1064.232 1064.724 1065.217 1065.710 1066.202 1066.695 1067.188 1067.681 1068.174 1068.667 1069.160 1069.653 1070.146 1070.639 1071.132 1071.625 1072.118 1072.611 1073.104 1073.598 1074.091 1074.584 1075.078 1075.571 1076.064 1076.558 1077.051 1077.545 1078.038 1078.532 1079.025 1079.519 1080.012 1080.506 1081.000 1081.494 1081.987 1082.481 1082.975 1083.469 1083.963 1084.457 1084.950 1085.444 1085.938 1086.432 1086.927 1087.421 1087.915 1088.409 1088.903 1089.397 1089.891 1090.386 1090.880 1091.374 1091.869 1092.363 1092.858 1093.352 1093.847 1094.341 1094.836 1095.330 1095.825 1096.319 1096.814 1097.309 1097.803 1098.298 1098.793 1099.288 1099.783 1100.278 1100.773 1101.267 1101.762 1102.257 1102.752 1103.248 1103.743 1104.238 1104.733 1105.228 1105.723 1106.219 1106.714 1107.209 1107.704 1108.200 1108.695 1109.191 1109.686 1110.182 1110.677 1111.173 1111.668 1112.164 1112.660 1113.155 1113.651 1114.147 1114.642 1115.138 1115.634 1116.130 1116.626 1117.122 1117.618 1118.114 1118.610 1119.106 1119.602 1120.098 1120.594 1121.090 1121.586 1122.083 1122.579 1123.075 1123.572 1124.068 1124.564"

def current_time() -> str:
    t = datetime.now()
    return str(t.strftime('%Y-%m-%d_%H-%M-%S.%f')[:-7])

def create_new_folder(p,d) -> bool:
    global save_directory
    # Path
    save_directory = join(p,d)
    if not exists(save_directory):
        makedirs(save_directory)
        return True
    else:
        return False

def new_txt_data() -> str:
        '''Generate a text file to save the raw data in 
        with the first row containing a timestamp of the file creation 
        and wavelengths of the spectrometer.
        
        ex. new_file_name = new_txt_data()'''

        timestamp = current_time()
        create_new_folder(base_save_directory,timestamp.split("_")[0])
        our_file = save_directory+'/'+timestamp+'.txt'
        global wavelengths 
        # for item in spec.wavelengths():
        #         wavelengths += str(item)[0:8]+' '
        prefix='@Wavelength @Dim=1 '
        with open(our_file, 'w') as f:
            f.write('@Time '+timestamp+'\n')
            f.write(prefix + wavelengths+'\n')
        return our_file

def save_list_to_string(prefix: str, data: list, our_file=None):
        string_data = ""
        for value in data:
                string_data += str(value)+" "
        if our_file is None:
                with open(string_data_file, 'a') as f:
                        L = f"{prefix} {string_data}\n" 
                        f.write(L)
        elif our_file is not None:
                with open(our_file, 'a') as f:
                        L = f"{prefix} {string_data}\n" 
                        f.write(L)

def read_reagents(file=None) -> list:
        '''Returns tracker file contents in form of
        [molybdate_amt, 
        water_amt, 
        po4_amt, 
        ascorbic_amt] '''
        print("into read reagents")
        try:
                if file is None:
                        with open(tracker_name,'r') as f:
                                myReader = reader(f)
                                reagents = [row for row in myReader if True]
                else:
                        with open(file,'r') as f:
                                myReader = reader(f)
                                reagents = [row for row in myReader if True]

                # check if reagent needs to be refilled
                
                volumes = [int(elem[1]) for elem in reagents if elem and elem[1].isdigit()]
                for i in volumes:
                        if i<0:i=0

                percentage = int(volumes[0])/molybdate_refill_amt
                if percentage <= reagent_operating_percent:
                        logging.warning(f'Molybdate reagent is at {percentage*100:.1f} %\
                        \nStopping cycle to be refilled.')
                        raise Exception('Water empty. Ending script')
                        # TODO add functionality to halt runs here
                elif percentage <= reagent_warning_percent:
                        logging.warning(f'Molybdate reagent is at {percentage*100:.1f} %')
                
                percentage = int(volumes[1])/water_refill_amt
                if percentage <= reagent_operating_percent:
                        logging.warning(f'Water is at {percentage*100:.1f} %\
                        \nStopping cycle to be refilled.')
                        raise Exception('Water empty. Ending script')
                        
                elif percentage <= reagent_warning_percent:
                        logging.warning(f'Water reagent is at {percentage*100:.1f} %')
                
                percentage = int(volumes[2])/po4_refill_amt
                if percentage <= reagent_operating_percent:
                        logging.warning(f'PO4 reagent is at {percentage*100:.1f} %\
                        \nStopping cycle to be refilled.')
                        raise Exception('Water empty. Ending script')
                        
                elif percentage <= reagent_warning_percent:
                        logging.warning(f'PO4 reagent is at {percentage*100:.1f} %')
                
                percentage = int(volumes[3])/ascorbic_refill_amt
                if percentage <= reagent_operating_percent:
                        logging.warning(f'Ascorbic acid reagent is at {percentage*100:.1f} %\
                        \nStopping cycle to be refilled.')
                        raise Exception('Water empty. Ending script')
                        
                elif percentage <= reagent_warning_percent:
                        logging.warning(f'Ascorbic acid reagent is at {percentage*100:.1f} %')
                return volumes
        except Exception as e:
                print("Template Run Exception:  ", e)        
        
def stage_reagents(reagent_name: str, amount: int) -> bool:
        '''Temporarily stores reagents used to be commited to the final file
        
        ex. stage_reagents(water, 600) for 600 uL water consumed 
        
        This function first reads the amount in the csv file so that
        we can subtract the amount used and then update the file. This way another function
        or user could write to the csv as the rest of the script is running and refill reagents
        without having to stop the script.'''
        try:
                logging.debug(f'{reagent_name} to be used for {amount} uL')
                if exists(tmp_stage_file):
                        current_reagents = read_reagents(tmp_stage_file)
                        print("current_reagents",current_reagents)
                else:
                        current_reagents = read_reagents()
        except Exception as e:
                        print("Template Run Exception:  ", e)
        print(current_reagents)
        molyb_temp = current_reagents[0]
        water_temp = current_reagents[1]
        po4_temp = current_reagents[2]
        ascorbic_temp = current_reagents[3]

        # update reagent remaining
        if reagent_name == molybdate:
                molyb_temp -= amount
        elif reagent_name == water:
                water_temp -= amount
        elif reagent_name == po4:
                po4_temp -= amount
        elif reagent_name == ascorbic_acid:
                ascorbic_temp -= amount
        else:
                logging.error("Invalid reagent name")
                return False

        # save new amount to file
        with open(tmp_stage_file,'w') as f:
                rows = [['Molybdate uL', molyb_temp], 
                    ['Water uL', water_temp], 
                    ['PO4 uL', po4_temp], 
                    ['Ascorbic uL', ascorbic_temp]
                ] 
                refill = writer(f)
                refill.writerows(rows)
        return True

def commit_reagents() -> bool:
        '''Updates the reagents.csv file with amount of reagent used.

        ex. stage_reagents() to save the previously staged amounts'''

        global molyb_remaining
        global water_remaining
        global po4_remaining
        global ascorbic_remaining

        try:
                current_reagents = read_reagents(tracker_name)
                logging.debug(f'Committing {current_reagents} uL')
        except (OSError) as e:
                logging.error("Stage the changes before using this function to save them")
                print("Exception : ", e)
                return False
        molyb_remaining = current_reagents[0]
        water_remaining = current_reagents[1]
        po4_remaining = current_reagents[2]
        ascorbic_remaining = current_reagents[3]

        # save new amount to file
        with open(tracker_name,'w') as f:
                rows = [['Molybdate uL', molyb_remaining], 
                    ['Water uL', water_remaining], 
                    ['PO4 uL', po4_remaining], 
                    ['Ascorbic uL', ascorbic_remaining]
                ] 
                refill = writer(f)
                refill.writerows(rows)
        # remove(tmp_stage_file)
        # reset amount being pumped as active pump time is done
        __amount_p1 = 0
        __amount_p2 = 0
        __p1_status = False
        __p2_status = False
        return True

def refilled_reagent(reagent_name: str, amount: int) -> bool:
        '''Sets new value for reagents.csv file with reagent refilled.

        ex. refilled_reagent(water, 60) for 60 mL water available to be used '''

        global molyb_remaining
        global water_remaining
        global po4_remaining
        global ascorbic_remaining

        current_reagents = read_reagents()
        molyb_remaining = current_reagents[0]
        water_remaining = current_reagents[1]
        po4_remaining = current_reagents[2]
        ascorbic_remaining = current_reagents[3]
        logging.info(f'{reagent_name} refilled to {amount} mL')
        amount *= 1000
        print(refilled_reagent)

        # update reagent remaining
        if reagent_name == molybdate:
                molyb_remaining = amount
        elif reagent_name == water:
                print(water)
                water_remaining = amount
        elif reagent_name == po4:
                po4_remaining = amount
        elif reagent_name == ascorbic_acid:
                ascorbic_remaining = amount
        else:
                logging.error("Invalid reagent name")
                return False

        # save new amount to file
        with open(tracker_name,'w') as f:
                rows = [['Molybdate uL', molyb_remaining], 
                    ['Water uL', water_remaining], 
                    ['PO4 uL', po4_remaining], 
                    ['Ascorbic uL', ascorbic_remaining]
                ] 
                refill = writer(f)
                refill.writerows(rows)
        
        return True

def refill_all_reagents():
        '''use tracker_name path and resets file to default amounts'''
        logging.info(f'All reagents refilled to default mL')
        with open(tracker_name,'w') as f:
                rows = [['Molybdate uL', molybdate_refill_amt*1000], 
                    ['Water uL', water_refill_amt*1000], 
                    ['PO4 uL', po4_refill_amt*1000], 
                    ['Ascorbic uL', ascorbic_refill_amt*1000]
                ] 
                refill = writer(f)
                refill.writerows(rows)

                                # CHEM ON VALVE PORT POSITION FUNCTIONS

def move_8ports(port_num: int) -> bool:
        '''Move to a numbered port position (1 to 8)'''
        global port_current

                                # CHEM VALVE PORT VARIABLES
        num_ports = 9
        #Port Positions
        port_p1 = positions_8_ports['port_p1']                          # Waste Port position
        port_p2 = positions_8_ports['port_p2']                          # Flow Cell position
        port_p3 = positions_8_ports['port_p3']                          # Molybdate position
        port_p4 = positions_8_ports['port_p4']                          # Ascorbic Acid position
        port_p5 = positions_8_ports['port_p5']                          # PO4 Sample position
        port_p6 = positions_8_ports['port_p6']                          # PO4 Standard position
        port_p7 = positions_8_ports['port_p7']                          # Used for...?
        port_p8 = positions_8_ports['port_p8']                          # Used for...?
        port_p9 = positions_8_ports['port_p9']                          # small port which is plugged  

        if port_num in range(1, num_ports+1):
                logging.info(f"Moving to port {port_num}")
        else:
                logging.warning(f"Invalid port number: {port_num}")
                return False  # break out of function and signal unsuccessful

        if port_num == 1:
                pos_cmd ='AMA '+ str(port_p1)+'\r\n'         #Uses port_p1 variable. AMA is absolute position from 0 refernce on valve.
        elif port_num == 2:
                pos_cmd ='AMA '+ str(port_p2)+'\r\n'         #Uses port_p2 variable. AMA is absolute position from 0 refernce on valve.
        elif port_num == 3:
                pos_cmd ='AMA '+ str(port_p3)+'\r\n'         #Uses port_p3 variable. AMA is absolute position from 0 refernce on valve.
        elif port_num == 4:
                pos_cmd ='AMA '+ str(port_p4)+'\r\n'         #Uses port_p4 variable. AMA is absolute position from 0 refernce on valve.
        elif port_num == 5:
                pos_cmd ='AMA '+ str(port_p5)+'\r\n'         #Uses port_p5 variable. AMA is absolute position from 0 refernce on valve.
        elif port_num == 6:
                pos_cmd ='AMA '+ str(port_p6)+'\r\n'         #Uses port_p6 variable. AMA is absolute position from 0 refernce on valve.
        elif port_num == 7:
                pos_cmd ='AMA '+ str(port_p7)+'\r\n'         #Uses port_p7 variable. AMA is absolute position from 0 refernce on valve.
        elif port_num == 8:
                pos_cmd ='AMA '+ str(port_p8)+'\r\n'         #Uses port_p8 variable. AMA is absolute position from 0 refernce on valve.
                
        elif port_num == 9:
                pos_cmd ='AMA '+ str(port_p9)+'\r\n'         #Uses port_p9 variable. AMA is absolute position from 0 refernce on valve.
                

        encoded_cmd = bytes(pos_cmd,'UTF-8')       #Creates the output and encodes it 
        # commented for test
        # ser.write(encoded_cmd)                        #Sends encoded command to the Chem-on Valve
        sleep(t1)                                       #Wait for n seconds (based on end-user needs)
        # port_timer.timer_set(new_interval=t1)
        port_current = port_num

        return True  # signal the port move was successful

def move_6ports(port_num: int) -> bool:
        '''Move to a numbered port position (1 to 8)'''
        global port_current

                                # CHEM VALVE PORT VARIABLES
        num_ports = 6
        #Port Positions
        port_p1 = 1340                          # Waste Port position (Currently not in use)
        port_p2 = 1090                          # Flow Cell position
        port_p3 = 840                           # Molybdate position
        port_p4 = 590                           # PO4 Sample position
        port_p5 = 350                           # Ascorbic Acid position
        port_p6 = 130                           # PO4 Standard position

        if port_num in range(1, num_ports+1):
                logging.info(f"Moving to port {port_num}")
        else:
                logging.warning(f"Invalid port number: {port_num}")
                return False  # break out of function and signal unsuccessful

        if port_num == 1:
                pos_cmd ='AMA '+ str(port_p1)+'\r\n'         #Uses port_p1 variable. AMA is absolute position from 0 refernce on valve.
        elif port_num == 2:
                pos_cmd ='AMA '+ str(port_p2)+'\r\n'         #Uses port_p2 variable. AMA is absolute position from 0 refernce on valve.
        elif port_num == 3:
                pos_cmd ='AMA '+ str(port_p3)+'\r\n'         #Uses port_p3 variable. AMA is absolute position from 0 refernce on valve.
        elif port_num == 4:
                pos_cmd ='AMA '+ str(port_p4)+'\r\n'         #Uses port_p4 variable. AMA is absolute position from 0 refernce on valve.
        elif port_num == 5:
                pos_cmd ='AMA '+ str(port_p5)+'\r\n'         #Uses port_p5 variable. AMA is absolute position from 0 refernce on valve.
        elif port_num == 6:
                pos_cmd ='AMA '+ str(port_p6)+'\r\n'         #Uses port_p6 variable. AMA is absolute position from 0 refernce on valve.
                
        encoded_cmd = bytes(pos_cmd,'UTF-8')       #Creates the output and encodes it 
        # commented for test
        # ser.write(encoded_cmd)                        #Sends encoded command to the Chem-on Valve
        sleep(t1)                                       #Wait for n seconds (based on end-user needs)
        port_current = port_num

        return True  # signal the port move was successful

def send_speed(speed: int, pump_num: int) -> bool:
        '''Choose speed in uL/sec and pump 1 or pump 2 and send over serial'''

        global __speed_p1, __speed_p2
        
        if pump_num == 1:
                speed_cmd = f'CVM {speed}*EU\r\n'
                __speed_p1 = speed
        elif pump_num == 2:
                speed_cmd = f'DVM {speed}*EU\r\n'
                __speed_p2 = speed
        else:
                logging.warning(f"Invalid pump number: {pump_num}")
                return False
        
        speed_bytes = bytes(speed_cmd,'UTF-8')
        # commented for test
        # ser.write(speed_bytes)
        return True

def send_amount(amount: int, pump_num: int) -> bool:
        '''Choose amount in uL and pump 1 or pump 2 and send over serial.
        + value for dispense, - for aspirate
        
        Optionally provide the reagent supply used from to track
        amount remaining. 
        Valid supply names:
        ['MOLYB', 'WATER', 'PO4', 'ASCORBIC']'''

        global __amount_p1, __amount_p2
        if pump_num == 1:
                amount_cmd = f'CMR {amount}*EU\r\n'
                __amount_p1 = amount
                __p1_status = True
        elif pump_num == 2:
                amount_cmd = f'DMR {amount}*EU\r\n'
                __amount_p2 = amount
                __p2_status = True
        else:
                logging.warning(f"Invalid pump number: {pump_num}")
                return False
        amount_bytes = bytes(amount_cmd,'UTF-8')
        # commented for test
        # ser.write(amount_bytes)
        return True

                                        # SYSTEM FLUSH FUNCTION

def system_flush():
        logging.info("System Flush In Progress")
        print("System Flush In Progress")
        # commented for test
        # move_8ports(1)
        # move_8ports(flow_cell_port)
        # stage_reagents(water,flush_p1_amount)
        # send_speed(flush_p1_speed, 1)                         #Pump 1 moves at speed set by flush_p1_speed variable
        # send_amount(flush_p1_amount, 1)                        #Pump 1 dispenses amount set by flush_p1_amount varaible
        sleep(t0)
        # stage_reagents(water,flush_p2_amount)
        # send_speed(flush_p2_speed, 2)                        #Pump 2 moves at speed set by flush_p2_speed variable
        # send_amount(flush_p2_amount, 2)                        #Pump 2 dispenses amount set by flush_p2_amount varaible
        logging.debug(f'Sleeping for {flushtime} seconds')
        print("Sleeping for {flushtime} seconds")
        # sleep(flushtime)
        commit_reagents()
                                        
                                        # DISPENSE/ASPIRATE FUNCTIONS

def molybdate_reagent():
        '''Moves the CoV to a specified port then activates pumps to send predetermined amount of fluid at a set speed.'''
        # commented for test
        # move_8ports(molybdate_port)
        logging.info(f"Dispensing {molybdate_p1_amount} uL pump_1/ Aspirating {abs(molybdate_p2_amount)} uL pump_2") 
        print("Dispensing {molybdate_p1_amount} uL pump_1/ Aspirating {abs(molybdate_p2_amount)} uL pump_2")
        # stage_reagents(molybdate,-molybdate_p1_amount)
        # send_speed(molybdate_p1_speed, 1)                     #Pump 1 moves at speed set by molybdate_p1_speed variable
        # send_amount(molybdate_p1_amount, 1)                   #Pump 1 dispenses amount set by molybdate_p1_amount varaible
        sleep(t0)
        # stage_reagents(molybdate,-molybdate_p2_amount)                   
        # send_speed(molybdate_p2_speed, 2)                     #Pump 2 moves at speed set by molybdate_p2_speed variable
        # send_amount(molybdate_p2_amount, 2)                   #Pump 2 aspirates amount set by molybdate_p2_amount varaible
        logging.debug(f'Sleeping for {molybdatetime} seconds')
        print("Sleeping for {molybdatetime} seconds")
        sleep(molybdatetime)                                  #Wait for n seconds
        commit_reagents()

def ascorbic_acid_reagent():
        '''Moves the CoV to a specified port then activates pumps to send predetermined amount of fluid at a set speed.'''
        # commented for test
        # move_8ports(ascorbic_acid_port)
        
        logging.info(f"Aspirating {abs(ascorbic_p1_amount)} uL @ {ascorbic_p1_speed} uL/s pump_1/ Dispensing {ascorbic_p2_amount} uL @ {ascorbic_p2_speed} uL/s pump_2") 
        print("Aspirating {abs(ascorbic_p1_amount)} uL @ {ascorbic_p1_speed} uL/s pump_1/ Dispensing {ascorbic_p2_amount} uL @ {ascorbic_p2_speed} uL/s pump_2")
        # stage_reagents(ascorbic_acid, -ascorbic_p1_amount)
        # send_speed(ascorbic_p1_speed, 1)                      #Pump 1 moves at speed set by ascorbic_p1_speed variable
        # send_amount(ascorbic_p1_amount, 1)                    #Pump 1 aspirates amount set by ascorbic_p1_amount varaible
        sleep(t0)
        # stage_reagents(ascorbic_acid, -ascorbic_p2_amount)                      
        # send_speed(ascorbic_p2_speed, 2)                      #Pump 2 moves at speed set by ascorbic_p2_speed variable
        # send_amount(ascorbic_p2_amount, 2)                    #Pump 2 aspirates amount set by ascorbic_p2_amount varaible
        logging.debug(f'Sleeping for {ascorbicacidtime} seconds')
        print("Sleeping for {ascorbicacidtime} seconds")
        sleep(ascorbicacidtime)                                 #Wait for n seconds
        commit_reagents()

def flow_cell():
        '''Moves the CoV to a specified port then activates pumps to send predetermined amount of fluid at a set speed.'''
        # commented for test
        # move_8ports(flow_cell_port)
        logging.info(f"Dispensing {flow_cell_p1_amount} uL @ {flow_cell_p1_speed} uL/s pump_1 into flow cell")
        print("Dispensing {flow_cell_p1_amount} uL @ {flow_cell_p1_speed} uL/s pump_1 into flow cell")
        # stage_reagents(water,flow_cell_p1_amount)
        # send_speed(flow_cell_p1_speed, 1)                     #Pump 1 moves at speed set by flow_cell_p1_speed variable
        # send_amount(flow_cell_p1_amount, 1)                   #Pump 1 dispenses amount set by flow_cell_p1_amount varaible
        print(flowcelltime)
        logging.debug(f'Sleeping for {flowcelltime} seconds')
        print("Sleeping for {flowcelltime} seconds")
        # sleep(flowcelltime)                                     #Wait for n seconds                                     
        commit_reagents()

def spectro_darkscan(spec):
        '''
        Inputs:
        -Spectrophotometer read from Seabreeze Library

        Outputs:
        -Intensity values across all wavelengths taken with lamp off.
        '''

        wavelengths = spec.wavelengths()
        intensities = spec.intensities()
        column_names = ['wavelengths','intensities']
        combine = vstack((wavelengths, intensities)).T
        shape(combine)

        darkscan = DataFrame(data=combine, columns=column_names) # produces dataframe from most recent scan taken from spec.

        dark_spec = []
        # dark_spec = darkscan['intensities']

        # plt.figure()
        # plt.xlabel('Wavelength nm')
        # plt.ylabel('Intensity')
        # plt.title('Darkscan Calibration')
        # plt.plot(wavelengths,dark_spec)
        # #plt.show()
        # plt.savefig(f'{graph_directory}/spectro_darkscan.png', bbox_inches='tight')
        # # sleep(5)
        # plt.close()

        return dark_spec

def spectro_refscan(spec):
        '''
        Inputs:
        -Spectrophotometer read from Seabreeze Library
    
        Outputs:
        -Intensity values across all wavelengths taken with lamp on, no sample in flow cell.
        '''

        refscan_intensity = []

        samples_to_average = 20

        for i in range(samples_to_average):

            wavelengths = spec.wavelengths()
            intensities = spec.intensities()
            column_names = ['wavelengths','intensities']
            combine = vstack((wavelengths, intensities)).T
            shape(combine)
            refscan = DataFrame(data=combine, columns=column_names)  # produces dataframe from most recent scan taken from spec.

            refscan_intensity.append(refscan['intensities'])
            sleep(0.25)

        ref_spec = array(refscan_intensity).mean(axis=0)

        # plt.figure()
        # plt.xlabel('Wavelength nm')
        # plt.ylabel('Intensity')
        # plt.title('Reference Scan')
        # plt.plot(wavelengths,intensities)
        # #plt.show()
        # plt.savefig(f'{graph_directory}/spectro_refscan.png', bbox_inches='tight')
        # # sleep(5)
        # plt.close()

        return ref_spec

def spectro_samplescan(spec):
        '''
        Inputs:
        -Spectrophotometer read from Seabreeze Library

        Outputs:
        -Intensity values across all wavelengths taken with lamp on, sample in flow cell.
        '''

        sampscan_intensity = []
   
        samples_to_average = 20

        for i in range(samples_to_average):

            wavelengths = spec.wavelengths()
            intensities = spec.intensities()
            column_names = ['wavelengths','intensities']
            combine = vstack((wavelengths, intensities)).T
            shape(combine)
            sampscan = DataFrame(data=combine, columns=column_names) #produces dataframe from most recent scan taken from spec.

            sampscan_intensity.append(sampscan['intensities'])
   
            sleep(0.25)

        samp_spec = array(sampscan_intensity).mean(axis=0)

        samp_lambdas = sampscan['wavelengths']

        # plt.figure()
        # plt.xlabel('Wavelength nm')
        # plt.ylabel('Intensity')
        # plt.title('Sample Scan')
        # plt.plot(wavelengths,intensities)
        # #plt.show()
        # plt.savefig(f'{graph_directory}/spectro_samplescan.png', bbox_inches='tight')
        # # sleep(5)
        # plt.close()

        return samp_spec, samp_lambdas
    
def spectro_calcAbsorbance(dark_spec,ref_spec,samp_spec,samp_lambdas) -> list:

        '''
        This function uses outputs from the following functions for its input: "darkscan", "referencescan", "samplescan". Note that these functions must be run prior to running this function.

        The inputs are defined are follows:
        dark_spec = darkscan(spec)
        ref_spec = referencescan(spec)
        samp_spec, samp_lambdas = samplescan(spec)[:]

        Absorbance is calculated using the equation: A = log_10 (Io - dark signal / I - dark signal), where Io is the intensity from the reference scan, and I is the intensity from the sample scan.

        Outputs:
        -Final absorbance value to be used in calculating concentration of analyte.
        -Absorbance spectrum across all available wavelengths
        '''

        absorbances_unfiltered = log10((ref_spec - dark_spec) / (samp_spec - dark_spec))     #absorbance ranges 0 to 1

        ##smoothing spectrum using moving average
        window_size = 20
        numbers_series = Series(absorbances_unfiltered)
        windows = numbers_series.rolling(window_size)
        moving_averages = windows.mean()
        moving_averages_list = moving_averages.tolist()
        absorbances_filtered = moving_averages_list[window_size - 1:]
        wavelengths_filtered = samp_lambdas[:-19]

        #organizing filtered outputs into dataframe
        column_names = ['wavelengths_filtered','absorbances_filtered']
        combine = vstack((wavelengths_filtered, absorbances_filtered)).T
        absorbances_final = DataFrame(data=combine, columns=column_names)

        #calculating absorbance value at monitoring wavelength
        abs_monitoring = absorbances_final[(absorbances_final['wavelengths_filtered'] < (monitoringlambda + 1)) & (absorbances_final['wavelengths_filtered'] > (monitoringlambda - 1))]
        abs_monitoring_mean = mean(abs_monitoring['absorbances_filtered'])

        ##calculating absorbance value at reference wavelength
        abs_reference = absorbances_final[(absorbances_final['wavelengths_filtered'] < (reflambda + 1)) & (absorbances_final['wavelengths_filtered'] > (reflambda - 1))]
        abs_reference_mean = mean(abs_reference['absorbances_filtered'])

        abs_final = abs_monitoring_mean - abs_reference_mean
        logging.info(f'abs_final = {abs_final}')
        print(absorbances_final['absorbances_filtered'].mean())


        # plotting absorbance spectrum

        # plt.figure()
        # plt.ylabel('Absorbance')
        # plt.xlabel('Wavelength (nm)')
        # plt.title('Sample Absorbance')
        # plt.xlim(600,1100)
        # plt.plot(absorbances_final['wavelengths_filtered'],absorbances_final['absorbances_filtered'])
        # # plt.show()
        # plt.savefig(f'{graph_directory}/spectro_calcAbsorbance.png', bbox_inches='tight')
        # # sleep(5)
        # plt.close()
        
        return [abs_final,absorbances_final['absorbances_filtered']]

                                        # SYSTEM PRIMING FUNCTION

def prime_port(port_num:int) -> bool:
        '''Prime the system at the given port (1 to 8)'''

        # Move to the given port to be primed
        if move_8ports(port_num):
                logging.info(f"Priming port {port_num}")
        else:
                logging.debug(f"Invalid port to be primed: {port_num}")
                return False  # break out of function and signal unsuccessful

        if port_num == 1: 
                stage_reagents(water, port1_pp1amount)
                send_speed(port1_pp1speed, 1)
                send_amount(port1_pp1amount, 1)
                logging.debug(f'Sleeping for {p1primetime} seconds')
                sleep(p1primetime)
                
        elif port_num == 2:
                stage_reagents(water, port2_pp1amount)
                send_speed(port2_pp1speed, 1)
                send_amount(port2_pp1amount, 1)
                sleep(t0)
                
                stage_reagents(water, port2_pp2amount)
                send_speed(port2_pp2speed, 2)
                send_amount(port2_pp2amount, 2)
                logging.debug(f'Sleeping for {p2primetime} seconds')
                sleep(p2primetime)
                
        elif port_num == molybdate_port:
                stage_reagents(molybdate, -port3_pp1amount)
                send_speed(port3_pp1speed,1)
                send_amount(port3_pp1amount,1)
                logging.debug(f'Sleeping for {p3primetime} seconds')
                sleep(p3primetime)
                
        elif port_num == sample_port:
                stage_reagents(None, port4_pp1amount)
                send_speed(port4_pp1speed,1)
                send_amount(port4_pp1amount,1)
                logging.debug(f'Sleeping for {p4primetime} seconds')
                sleep(p4primetime)
                # aspirates seawater which we do not care about rn
                 
        elif port_num == ascorbic_acid_port:
                stage_reagents(ascorbic_acid, -port5_pp1amount)
                send_speed(port5_pp1speed,1)
                send_amount(port5_pp1amount,1)
                logging.debug(f'Sleeping for {p5primetime} seconds')
                sleep(p5primetime)
                
        elif port_num == po4_port:
                stage_reagents(po4, -port6_pp1amount)
                send_speed(port4_pp1speed,1) 
                send_amount(port4_pp1amount,1)
                logging.debug(f'Sleeping for {p6primetime} seconds')
                sleep(p6primetime)
                
        elif port_num == blank_port:
                stage_reagents(water, -port7_pp1amount)
                send_speed(port7_pp1speed,1)
                send_amount(-port7_pp1amount,1)
                logging.debug(f'Sleeping for {p7primetime} seconds')
                sleep(p7primetime)
                # To be determined
                
        elif port_num == 8:
                stage_reagents(None, -port8_pp1amount)
                send_speed(port8_pp1speed,1)
                send_amount(port8_pp1amount,1)
                logging.debug(f'Sleeping for {p8primetime} seconds')
                sleep(p8primetime)
                # To be determined

        elif port_num == 7:
                stage_reagents(None, -port7_pp1amount)
                send_speed(-port7_pp1speed,1)
                send_amount(port7_pp1amount,1)
                logging.debug(f'Sleeping for {p8primetime} seconds')
                sleep(p8primetime)

        
        commit_reagents()
        return True

def prime():
        for i in range(totalprimes):
                move_8ports(1)
                #prime_port(2)
                #move_8ports(1)
                prime_port(3)
                move_8ports(1)
                prime_port(1)
                prime_port(4)
                move_8ports(1)
                prime_port(2)
                move_8ports(1)
                #prime_port(5)
                #move_8ports(1)
                #prime_port(6)
                #move_8ports(1)
                #prime_port(blank_port)
                #move_8ports(1)
                #prime_port(8)
                #prime_port(1)
                #auxMotor()
        logging.info('Prime Complete')

                                        # AUX MOTOR AND LIGHTSOURCE FUNCTIONS

def auxMotorOn():
        global __aux_motor_status

        logging.info('Aux start')
        # GPIO.output(motorPin,GPIO.HIGH) # commented for test
        __aux_motor_status = 'ON'

def auxMotorOff():
        global __aux_motor_status

        # GPIO.output(motorPin,GPIO.LOW) # commented for test
        __aux_motor_status = 'OFF'  
        logging.info('Aux stopped')

def lightOn():
        global __light_status
        # GPIO.output(ledPin,GPIO.HIGH)  # commented for test
        __light_status = 'ON'
        logging.info('Light On')

def lightOff():
        global __light_status
        # GPIO.output(ledPin,GPIO.LOW)  # commented for test
        __light_status = 'OFF'
        logging.info('Light Off')

                                        # BLANK/STANDARD/SAMPLE RUN FUNCTIONS

def acid_reagent():
        '''depricatred
        
        Pump molybdate reagent then ascorbic reagent then the flow cell and wait 5 min.'''
        
        molybdate_reagent()

        ascorbic_acid_reagent()

        flow_cell()

        logging.debug(f'Sleeping for {acidreagenttime} seconds to mix')
        print("Sleeping for {{acidreagenttime}} seconds to mix")
        sleep(acidreagenttime)
        
def check_acid_reagent(refspec) -> list:
        '''After acid_reagent(), get sample absorbances'''

        # global last_darkspec,spec
        # samp_spec, samp_lambdas = spectro_samplescan(spec)[:]
        # absorbances=spectro_calcAbsorbance(last_darkspec,refspec,samp_spec, samp_lambdas)
        absorbances = "" 
        return absorbances

def blank_sample_run() -> list:
        sleep(refscantime)
        # ref_spec=spectro_refscan(spec)

        blank_sample()
        acid_reagent()
        # absorbance_blank = check_acid_reagent(ref_spec)
        system_flush()
        absorbance_blank="calculated data"

        return absorbance_blank

def reprime():
        # commented for test
        # move_8ports(molybdate_port)
        logging.info(f"Aspirating {after_p1_amount} uL pump_1 at {after_p1_speed} uL/s")
        print("Aspirating {after_p1_amount} uL pump_1 at {after_p1_speed} uL/s")
        # stage_reagents(molybdate, -(after_p1_amount))
        # send_speed(after_p1_speed,1)
        # send_amount(after_p1_amount,1)
        logging.debug(f'Sleeping for {reprimetime} seconds')
        print('Sleeping for {reprimetime} seconds')
        sleep(reprimetime)

        commit_reagents()

        # move_8ports(po4_port)
        logging.info(f"Aspirating {after_p1_amount} uL pump_1 at {after_p1_speed} uL/s")
        print("Aspirating {after_p1_amount} uL pump_1 at {after_p1_speed} uL/s")
        # stage_reagents(po4,after_p1_amount)
        # send_speed(after_p1_speed,1)
        # send_amount(after_p1_amount,1)
        logging.debug(f'Sleeping for {reprimetime} seconds')
        print('Sleeping for {reprimetime} seconds')
        sleep(reprimetime)

        commit_reagents()

def po4_standard_run() -> list:
        sleep(refscantime)
        # ref_spec=spectro_refscan(spec)

        reprime() #moved priming step to beginning of standard run to avoid carryover

        po4_standard()
        acid_reagent()
        # absorbance_po4std = check_acid_reagent(ref_spec)
        absorbance_po4std="calculated data"
        
        system_flush()

        return absorbance_po4std

def po4_sample_run() -> list:

        sleep(refscantime)
        # ref_spec=spectro_refscan(spec)

        auxMotorOn()
        logging.debug(f'Sleeping for {auxtime} seconds')
        print('Sleeping for {auxtime} seconds')
        sleep(auxtime)
        auxMotorOff()
        po4_sample()
        acid_reagent()
        # absorbance_po4samp = check_acid_reagent(ref_spec)
        absorbance_po4samp="calculated data"
        reprime()

        system_flush()
        return absorbance_po4samp

                                        # DATA SENDING FUNCTIONS

client_connected = False

def my_server_command():
	try:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s1:
			s1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			s1.bind(("", PORT2))
			s1.listen(5)
			while 1:
				conn, addr = s1.accept()
				with conn:
					cmd = conn.recv(1024).decode()
					logging.info(cmd)
					data = "Ok".encode()
					conn.send(data)
					if cmd == "restart":
						logging.info("Restart Command Called")
					elif cmd == "flush":
						logging.info("Flush command called")
					
	except OSError as e:
		logging.exception(f"command function error : {e}")

def convert_to_string(l:list) -> bytes:
        '''Convert a 1D list of data to a string'''
        string=""
        for line in l:
                string+=line
                string+="\n"
        return string.encode()

def fileOpener():
        '''Get the latest text data file and return the file object,
        raw data, directory, and the file path.'''
        d = date.today()
        path = getcwd()+"/saved_data/"+str(d)+"/"
        file_path = path + sorted(listdir(path))[-1]
        print(file_path)
        # logging.info(file_path)
        f =open(file_path,'rb')

        data = f.read()
        return f,data,file_path,sorted(listdir(path))[-1]

def my_server_data():
        global total_sample_runs
        n = 0
        try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
                        s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        logging.info("Server Started waiting for client to connect")

                        s2.bind((HOST, PORT1))
                        s2.listen(5)
                        while n < lim_sample_runs:
                                # data_file_name = start()
                                # problematic behavior blocking the next run while waiting for connection
                                conn, addr = s2.accept()
                                with conn:
                                        logging.info(f'Connected by {addr}')
                                        #while True:
                                        f,data,path,f_name =fileOpener()
                                        f.close()
                                        conn.send(struct.pack('>I', len(f_name)))
                                        conn.send(f_name.encode())
                                        filesize = getsize(path) 
					# filesize = bin(filesize)[2:].zfill(32) # encode filesize as 32 bit binary s.send(filesize)
                                        conn.send(struct.pack('>I', int(filesize)))
                                        conn.sendall(data)
                                        n += 1
                                        # break
                                        sleep(next_sample_time)
        except OSError as e:
                logging.exception(f"data function error : {e}")

def reset_state_vars(state:int):
        '''Reset the vars and state to resume cycle at given state in state_dict
        
        ex. reset_state_vars(state_dict['PO4 Sample Run'])'''
        global blank_sample_counter, standard_sample_counter, sample_run_counter, current_state

        current_state = state

        if (state < state_dict['Blank Sample Run']):
                # state_var_dict['Booted'] = True
                blank_sample_counter = 0
        if (state < state_dict['PO4 Standard Run']):
                # state_var_dict['Blank Done'] = True
                standard_sample_counter = 0
        if (state < state_dict['PO4 Sample Run']):
                # state_var_dict['Standard Done'] = True
                sample_run_counter = 0
        if (state < state_dict['Save vars']):
                # state_var_dict['Sample Done'] = True
                pass
        
        # if (state == state_dict['Boot']):
        #         for key, item in state_var_dict.items():
        #                 state_var_dict[key] = False
                
        # elif (state == state_dict['Darkscan']):
        #         for key, item in state_var_dict.items():
        #                 if (key == 'Booted'):
        #                         state_var_dict[key] = True
        #                 else:
        #                         state_var_dict[key] = False
                
        # elif (state == state_dict['Blank Sample Run']):
        #         for key, item in state_var_dict.items():
        #                 if (key == 'Booted') or (key == 'Darkscan'):
        #                         state_var_dict[key] = True
        #                 else:
        #                         state_var_dict[key] = False
                
        # elif (state == state_dict['PO4 Standard Run']):
        #         for key, item in state_var_dict.items():
        #                 if (key == 'Booted') or (key == 'Darkscan') or (key == 'Blank Sample Run'):
        #                         state_var_dict[key] = True
        #                 else:
        #                         state_var_dict[key] = False
                
        # elif (state == state_dict['PO4 Sample Run']):
        #         for key, item in state_var_dict.items():
        #                 if (key == 'Booted') or (key == 'Darkscan') or (key == 'Blank Sample Run') or \
        #                         (key == 'PO4 Standard Run'):
        #                         state_var_dict[key] = True
        #                 else:
        #                         state_var_dict[key] = False
                
        # elif (state == state_dict['Save vars']):
                for key, item in state_var_dict.items():
                        if (key == 'Booted') or (key == 'Darkscan') or (key == 'Blank Sample Run') or \
                                (key == 'PO4 Standard Run') or (key == 'Save vars'):
                                state_var_dict[key] = True
                        else:
                                state_var_dict[key] = False  

def check_for_event():
    print("check_for_event")
    return None

def timer_check():
    
    global sample_idle_timer,idle_timer
    global current_state,next_state,sample_interval_state_on
    if sample_idle_timer.timer_event() is not None:
            # wait until timer is finished
            while (not sample_idle_timer.timer_event()) and (sample_idle_timer.timer_event() is not None):
                    sleep(5)
            
            if (sample_interval_state_on) and (current_state == state_dict['PO4 Sample Run']):
                    lightOn()
                    sample_idle_timer.timer_set(new_interval=lamptime)
                    logging.debug('Warming up lamp for next sample run')
                    sample_interval_state_on=False
            while (not sample_idle_timer.timer_event()) and (sample_idle_timer.timer_event() is not None):
                    sleep(5)
            event = None
            
    elif idle_timer.timer_event() is not None:
            # wait until timer is finished
            while (not idle_timer.timer_event()) and (idle_timer.timer_event() is not None):
                    sleep(5)
            reset_state_vars(state_dict['Darkscan'])
            event = None

    else:
            # read some input from socket connection as event
            event = None

def boot():
        try:
                print("Into Boot Function")
                lock.acquire()
                logging.info('Starting boot sequence')

                # pin initialization

                # commented for test

                # GPIO.setmode(GPIO.BCM)                  
                # GPIO.setup(motorPin,GPIO.OUT)           # Set aux motor pin to output
                # GPIO.setup(ledPin,GPIO.OUT)             # Set light source to ouput
                # GPIO.output(motorPin,GPIO.LOW)          # Aux motor output initial state of 0
                # GPIO.output(ledPin,GPIO.LOW)            # Lightsource output initial state of 0

                # create new reagent tracking file if it doesn't exist
                try:
                        read_reagents()
                        inaccurate_reagent = False
                except (OSError) as e:
                        inaccurate_reagent = True
                        logging.warning(f"Reagent tracking file does not exist. Attempting to create file at {tracker_name}")
                        refill_all_reagents()
                
                # clear out flow cell if anything was there from a faulty run
                # if inaccurate_reagent:
                        # system_flush()  # should this be run if there was an uncommitted reagent on boot?

                state_flag = True
                logging.debug(f'New state set: {[index for index in state_dict if state_dict[index] == current_state][0]}')
        except Exception as e:
                print(e)
                evt_name = "Booted" 
                state_name = [index for index in state_dict if state_dict[index] == current_state] 
                logging.error(f'Error occurred event in ({evt_name}) during state ({state_name})')
                state_flag = False
        print("Boot function complete : ",state_flag)
        lock.release()
        return state_flag

def dark_scan():
        global current_state, next_state,state_flag
        try:
                lock.acquire()

                logging.info('Starting darkscan sequence')
                print("Starting darkscan sequence")
                # darkscan_run() # commented for test
                # sleep(lamptime) #extra
                logging.debug("Lamp warm up time finished.")
                logging.debug(f'New state set: {[index for index in state_dict if state_dict[index] == current_state][0]}')
                state_flag = True
        except Exception as e:
                print("Error : Some code issue : " + str(e))
                state_name = [index for index in state_dict if state_dict[index] == current_state] 
                raise Exception(f'Invalid case: state = {state_name} Error: {str(e)}')
                state_flag = False
        print("Dark_scan function complete : ",state_flag)
        lock.release()
        return state_flag

def blank_sam_run():
        global current_state, next_state
        global blank_sample_counter
        try:
                print("into Blank Sample Run")
                lock.acquire()

                # run section once
                if (blank_sample_counter == 0):
                        start_time = time()
                        # text file to hold data and timestamp on creation
                        string_data_file = new_txt_data() # commented for test
                        blank = [0] * num_blank_runs

                if (blank_sample_counter < num_blank_runs):
                        logging.info(f'**Starting blank run sequence {blank_sample_counter}**')

                        sleep(refscantime)
                        # ref_spec=spectro_refscan(spec) # commented for test
                        sleep(6)
                        blank_sample()
                        acid_reagent()
                        # commented for test

                        # blank[blank_sample_counter], blank_vals = check_acid_reagent(ref_spec) # commented for test
                        logging.debug('Saving absorbances')
                        print("Saving absorbances")
                        # commented for test
                        
                        # prefix = f'@blank_sample_value_2048_{blank_sample_counter+1} @Dim=1' # commented for test
                        # save_list_to_string(prefix, blank_vals) # commented for test
                        blank_sample_counter += 1
                        system_flush()
                        q.put(state_dict['Blank Sample Run'])
                        
                elif blank_sample_counter == num_blank_runs:
                        logging.info('Blank runs complete')
                        

                        # commented for test

                        # if len(blank)>0:
                        #         mean_abs_blank=sum(blank)/len(blank)
                        # else:
                        #         mean_abs_blank=0
                        # save_list_to_string('@blank_sample_absorbances', blank)
                        # save_list_to_string('@blank_sample_count', [num_blank_runs])

                        blank_sample_counter = 0
                        q.put(state_dict['PO4 Standard Run'])
                        logging.debug(f'New state set: {[index for index in state_dict if state_dict[index] == current_state][0]}')
                        print("New state set: ", {[index for index in state_dict if state_dict[index] == current_state][0]})
        
        except Exception as e:
                state_name = [index for index in state_dict if state_dict[index] == current_state] 
                logging.error(f'Invalid case: state = {state_name} with error {str(e)}')
                raise Exception(f'Invalid case: state = {state_name} with error {str(e)}')
                q.put(state_dict['Error'])
        lock.release()

def po4_std_run():
        global current_state, next_state
        global standard_sample_counter
        try:
                print("into PO4 Standard Run")
                lock.acquire()

                if (standard_sample_counter == 0):
                        stand = [0] * num_standard_runs

                if (standard_sample_counter < num_standard_runs):
                        logging.info(f'**Starting PO4 standard sequence {standard_sample_counter}**')

                        sleep(refscantime)
                        # commented for test
                        # ref_spec=spectro_refscan(spec)

                        po4_standard()
                        acid_reagent()
                        # commented for test
                        # stand[standard_sample_counter], standard_vals = check_acid_reagent(ref_spec)
                        logging.debug('Saving absorbances')
                        print("Saving absorbances")
                        # commented for test
                        # prefix = f'@po4_standard_value_2048_{standard_sample_counter+1} @Dim=1'
                        # save_list_to_string(prefix, standard_vals)
                        standard_sample_counter += 1

                        reprime()
                        system_flush()
                        q.put(state_dict['PO4 Standard Run'])

                elif (standard_sample_counter == num_standard_runs):
                        logging.info('Standard runs complete')
                        
                        if len(stand)>0:
                                # and standard_sample_counter>0:
                                
                                #mean_abs_stand=sum(stand)/len(stand)
                                # ignores first standard run
                                mean_abs_stand = mean(stand[-2:])
                                
                        else:
                                mean_abs_stand=0
                        # commented for test
                        # save_list_to_string('@po4_standard_absorbances', stand)
                        # save_list_to_string('@po4_standard_count', [num_standard_runs])
                        standard_sample_counter = 0
                        logging.debug(f'New state set: {[index for index in state_dict if state_dict[index] == current_state][0]}')
                        print("New state set: ", {[index for index in state_dict if state_dict[index] == current_state][0]})
                        q.put(state_dict['PO4 Sample Run'])
        except Exception as e:
                state_name = [index for index in state_dict if state_dict[index] == current_state] 
                logging.error(f'Invalid case: state = {state_name} with error {str(e)}')
                raise Exception(f'Invalid case: state = {state_name} with error {str(e)}')
                q.put(state_dict['Error'])
        lock.release()

def po4_samp_run():
        global current_state, next_state
        global sample_run_counter
        try:
                print("into PO4 Sample Run")
                lock.acquire()
                if (sample_run_counter == 0):
                        sample = [0] * num_sample_runs
                        po4conc_array = [0] * num_sample_runs
                        sampletime_array = [0] * num_sample_runs
                        
                if (sample_run_counter < num_sample_runs):
                        logging.info(f'**Starting PO4 sample sequence {sample_run_counter}**')
                        print("**Starting PO4 sample sequence {sample_run_counter}**")
                        
                        sleep(refscantime)
                        # commented for test
                        # ref_spec=spectro_refscan(spec)
                        
                        auxMotorOn()
                        if (num_standard_runs > 0) and (num_blank_runs > 0):
                                timestamp = current_time()
                                sampletime_array[sample_run_counter] = timestamp
                        logging.debug(f'Sleeping for {auxtime} seconds')
                        print("Sleeping for {auxtime} seconds")
                        
                        sleep(auxtime)
                        auxMotorOff()
                        po4_sample()
                        acid_reagent()
                        # commented for test
                        # sample[sample_run_counter], sample_vals  = check_acid_reagent(ref_spec)
                        logging.debug('Saving absorbances')
                        # commented for test
                        # prefix = f'@po4_sample_value_2048_{sample_run_counter+1} @Dim=1'
                        # save_list_to_string(prefix, sample_vals)
                        # if (num_standard_runs > 0) and (num_blank_runs > 0):
                        #         po4conc_array[sample_run_counter] = (sample[sample_run_counter]-mean_abs_blank)*(known_concentration/(mean_abs_stand-mean_abs_blank))
                        # else:
                        #         po4conc_array[sample_run_counter] = "NAN"

                        total_sample_runs += 1
                        sample_run_counter += 1

                        reprime()
                        system_flush()

                        q.put(state_dict['Sample Interval'])

                if sample_run_counter == num_sample_runs:
                        logging.info('Sample runs complete')
                        print('Sample runs complete')
                        
                        lightOff()
                        sample_run_counter = 0
                        logging.debug(f'New state set: {[index for index in state_dict if state_dict[index] == current_state][0]}')
                        print('New state set: ',{[index for index in state_dict if state_dict[index] == current_state][0]})

                        q.put(state_dict['Save vars'])
        except Exception as e:  # some code issue          
                state_name = [index for index in state_dict if state_dict[index] == current_state] 
                logging.error(f'Invalid case: state = {state_name} with error {str(e)}')
                raise Exception(f'Invalid case: state = {state_name} with error {str(e)}')

                q.put(state_dict['Error'])
        lock.release()

def save_vars():
        global current_state, next_state
        try:
                print("into Save vars")
                lock.acquire()
                logging.info(f'Saving data to {string_data_file}')
                # commented for test
                # save_list_to_string('@po4_sample_absorbances', sample)
                # with open(string_data_file, 'a') as f:
                #         f.write(f'@po4_sample_count {num_sample_runs}\n')
                #         f.write(f'@num_of_sample_run {total_sample_runs}\n')
                #         f.write(f'@num_ports {8}\n')
                # for pre, pos in positions_8_ports.items():
                #         save_list_to_string(f'@{pre}', [pos])
                # with open(string_data_file, 'a') as f:
                #         f.write(f'@monitoringlambda {monitoringlambda}\n')
                #         f.write(f'@reflambda {reflambda}\n')
                #         f.write(f'@known_concentration {known_concentration}\n')
                # save_list_to_string('@po4_concentrations', po4conc_array)
                # save_list_to_string('@sample_times', sampletime_array)
                # with open(string_data_file, 'a') as f:
                #         f.write(f'@flush_p1_speed {flush_p1_speed}\n')
                #         f.write(f'@flush_p1_amount {flush_p1_amount}\n')
                #         f.write(f'@flush_p2_speed {flush_p2_speed}\n')
                #         f.write(f'@flush_p2_amount {flush_p2_amount}\n')
                #         f.write(f'@blank_p1_speed {blank_p1_speed}\n')
                #         f.write(f'@blank_p1_amount {blank_p1_amount}\n')
                #         f.write(f'@molybdate_p1_speed {molybdate_p1_speed}\n')
                #         f.write(f'@molybdate_p1_amount {molybdate_p1_amount}\n')
                #         f.write(f'@molybdate_p2_speed {molybdate_p2_speed}\n')
                #         f.write(f'@molybdate_p2_amount {molybdate_p2_amount}\n')
                #         f.write(f'@ascorbic_p1_speed {ascorbic_p1_speed}\n')
                #         f.write(f'@ascorbic_p1_amount {ascorbic_p1_amount}\n')
                #         f.write(f'@ascorbic_p2_speed {ascorbic_p2_speed}\n')
                #         f.write(f'@ascorbic_p2_amount {ascorbic_p2_amount}\n')
                #         f.write(f'@flow_cell_p1_speed {flow_cell_p1_speed}\n')
                #         f.write(f'@flow_cell_p1_amount {flow_cell_p1_amount}\n')
                #         f.write(f'@po4_standard_p1_speed {po4_standard_p1_speed}\n')
                #         f.write(f'@po4_standard_p1_amount {po4_standard_p1_amount}\n')
                #         f.write(f'@po4_sample_p1_speed {po4_sample_p1_speed}\n')
                #         f.write(f'@po4_sample_p1_amount {po4_sample_p1_amount}\n')
                #         f.write(f'@totalprimes {totalprimes}\n')
                #         f.write(f'@port1_pp1speed {port1_pp1speed}\n')
                #         f.write(f'@port1_pp1amount {port1_pp1amount}\n')
                #         f.write(f'@port2_pp1speed {port2_pp1speed}\n')
                #         f.write(f'@port2_pp1amount {port2_pp1amount}\n')
                #         f.write(f'@port2_pp2speed {port2_pp2speed}\n')
                #         f.write(f'@port2_pp2amount {port2_pp2amount}\n')
                #         f.write(f'@port3_pp1speed {port3_pp1speed}\n')
                #         f.write(f'@port3_pp1amount {port3_pp1amount}\n')
                #         f.write(f'@port4_pp1speed {port4_pp1speed}\n')
                #         f.write(f'@port4_pp1amount {port4_pp1amount}\n')
                #         f.write(f'@port5_pp1speed {port5_pp1speed}\n')
                #         f.write(f'@port5_pp1amount {port5_pp1amount}\n')
                #         f.write(f'@port6_pp1speed {port6_pp1speed}\n')
                #         f.write(f'@port6_pp1amount {port6_pp1amount}\n')
                #         f.write(f'@port7_pp1speed {port7_pp1speed}\n')
                #         f.write(f'@port7_pp1amount {port7_pp1amount}\n')
                #         f.write(f'@port8_pp1speed {port8_pp1speed}\n')
                #         f.write(f'@port8_pp1amount {port8_pp1amount}\n')
                # vols = read_reagents()
                # with open(string_data_file, 'a') as f:
                #         f.write(f'@Ascorbic_Acid_Reagent_used {ascorbic_refill_amt-vols[3]/1000}\n')
                #         f.write(f'@Ascorbic_Acid_Reagent_remaining {vols[3]/1000}\n')
                #         f.write(f'@Molybdate_Reagent_used {molybdate_refill_amt-vols[0]/1000}\n')
                #         f.write(f'@Molybdate_Reagent_remaining {vols[0]/1000}\n')
                #         f.write(f'@PO4_Reagent_used {po4_refill_amt-vols[2]/1000}\n')
                #         f.write(f'@PO4_Reagent_remaining {vols[2]/1000}\n')
                #         f.write(f'@water_Reagent_used {water_refill_amt-vols[1]/1000}\n')
                #         f.write(f'@water_Reagent_remaining {vols[1]/1000}\n')
                #         f.write(f'@t0 {t0}\n')
                #         f.write(f'@t1 {t1}\n')
                #         f.write(f'@t3 {t3}\n')
                #         f.write(f'@auxtime {auxtime}\n')
                #         f.write(f'@darkscantime {darkscantime}\n')
                #         f.write(f'@refscantime {refscantime}\n')
                #         f.write(f'@time_required {time()-start_time}\n')
                #         f.write(f'@aux_motor_status {__aux_motor_status}\n')
                #         f.write(f'@motor1_speed {__speed_p1}\n')
                #         f.write(f'@motor1_amount {__amount_p1}\n')
                #         f.write(f'@motor1_status {__p1_status}\n')
                #         f.write(f'@motor2_speed {__speed_p2}\n')
                #         f.write(f'@motor2_amount {__amount_p2}\n')
                #         f.write(f'@motor2_status {__p2_status}\n')
                #         f.write(f'@next_sample_time {next_sample_time}\n')

                idle_timer.timer_set(new_interval=idle_time)
                n += 1

                # logging.debug("Creating new log file")
                # timestamp = current_time()
                # logs = dirname(abspath(__file__))+f"/.tmp/{timestamp.split('_')[0]}"
                # if not exists(logs):
                #         makedirs(logs)
                # log_file = logs+f"/{timestamp}_pfiona.log"

                # logger.handlers = []
                # fh = logging.FileHandler(log_file)
                # fh.setLevel(logging.DEBUG)
                # fh.setFormatter(logging.Formatter('%(asctime)s (%(threadName)s) %(levelname)s:%(message)s'))
                # logger.addHandler(fh)

                # free up memory here so we don't crash?
                # print(gc.collect())
                # del ref_spec

                logging.debug(f'Waiting for next cycle')
                print('Waiting for next cycle')

                q.put(state_dict['Idle'])
                               
        except Exception as e:  # some code issue
                state_name = [index for index in state_dict if state_dict[index] == current_state] 
                logging.error(f'Invalid case: state = {state_name} with error {str(e)}')
                raise Exception(f'Invalid case: state = {state_name} with error {str(e)}')

                q.put(state_dict['Error'])
        lock.release()

def idle():
        global current_state, next_state
        global idle_timer
        try:
                print("Into Idle")
                logging.info("Idle timer complete. Next cycle to start.")
                print("Idle timer complete. Next cycle to start.")
                
                reset_state_vars(next_state)
                logging.debug(f'idle_timer time remaining: {idle_timer.time_remaining()}')
                if idle_timer.time_remaining() is None:
                        logging.info('Idle timer incorrectly set. Restarting timer')
                        idle_timer.timer_set()   

                q.put(state_dict['Darkscan'])  

        except Exception as e:
                state_name = [index for index in state_dict if state_dict[index] == current_state] 
                logging.error(f'Invalid case: state = {state_name} with error {str(e)}')
                raise Exception(f'Invalid case: state = {state_name} with error {str(e)}')
                q.put(state_dict['Error'])

# def check_finished():

#         return not lock.locked()

sleep_time={
        "boot":20,
        "dark_scan":20,
        "blank_sam_run":20,
        "po4_std_run":20,
        "po4_samp_run":20,
        "save_vars":20,
        "idle":20
}       

# New functions created for new cycle

def log_error_and_raise_exception(e):
        state_name = [index for index in state_dict if state_dict[index] == current_state] 
        logging.error(f'Invalid case: state = {state_name} with error {str(e)}')
        raise Exception(f'Invalid case: state = {state_name} with error {str(e)}')

def blank_sam_run_port_change():
        try :
                lock.acquire()
                '''Moves the CoV to a specified port then activates pumps to send predetermined amount of fluid at a set speed.'''
                # commented for test
                # move_8ports(waste_port) 

                state_flag = True
        except Exception as e:
                state_flag = False
                log_error_and_raise_exception(e)
        lock.release()
        return state_flag

def blank_sam_run_start_pump():
        try: 
                lock.acquire()
                logging.info(f"Dispensing Blank Sample: {blank_p1_amount} uL at {blank_p1_speed} uL/sec")    
                print("Dispensing Blank Sample: {blank_p1_amount} uL at {blank_p1_speed} uL/sec")
                stage_reagents(water,blank_p1_amount)
                # send_speed(blank_p1_speed, 1)                         #Pump 1 moves at speed set by blank_p1_speed variable
                # send_amount(blank_p1_amount, 1)                       #Pump 1 dispenses amount set by blank_p1_amount varaible
                state_flag = True
        except Exception as e:
                state_flag = False
                log_error_and_raise_exception(e)
        lock.release()
        return state_flag

def blank_sam_run_wait():
        try: 
                lock.acquire()
                logging.debug(f'Sleeping for {blanktime} seconds')
                print("Sleeping for {blanktime} seconds")
                # sleep(blanktime)                                      #wait for n seconds
                commit_reagents() # commented for test
                state_flag = True
        except Exception as e :
                state_flag = False
                log_error_and_raise_exception(e)
        lock.release()
        return state_flag

def po4_std_run_port_change():
        try:
                lock.acquire()
                '''Moves the CoV to a specified port then activates pumps to send predetermined amount of fluid at a set speed.'''
                # commented for test
                # move_8ports(po4_port)
                state_flag = True
        except Exception as e:
                state_flag = False
                log_error_and_raise_exception(e)
        lock.release()
        return state_flag

def po4_std_run_start_pump():
        try:
                lock.acquire()
                logging.info(f"Aspirating {abs(po4_standard_p1_amount)} uL pump_1 ")
                print("Aspirating {po4_standard_p1_amount} uL pump_1 ")
                stage_reagents(po4, -(po4_standard_p1_amount))
                # send_speed(po4_standard_p1_speed, 1)                  #Pump 1 moves at speed set by po4_standard_p1_speed variable
                # send_amount(po4_standard_p1_amount, 1)                #Pump 1 aspirates amount set by po4_standard_p1_amount varaible
                state_flag = True
        except Exception as e:
                state_flag = False
                log_error_and_raise_exception(e)
        lock.release()
        return state_flag

def po4_std_run_wait_time():
        try:
                lock.acquire()
                logging.debug(f'Sleeping for {po4standardtime} seconds')
                print("Sleeping for {po4standardtime} seconds")
                # sleep(po4standardtime)                                  #Wait for n seconds
                commit_reagents()
                state_flag = True
        except Exception as e:
                state_flag = False
                log_error_and_raise_exception(e)
        lock.release()
        return state_flag

def po4_samp_run_start_AM():
        try:
                lock.acquire()
                auxMotorOn()
                if (num_standard_runs > 0) and (num_blank_runs > 0):
                        timestamp = current_time()
                        sampletime_array[sample_run_counter] = timestamp
                logging.debug(f'Sleeping for {auxtime} seconds')
                print("Sleeping for {auxtime} seconds")
                auxMotorOff()
                # sleep(auxtime)
                state_flag = True
        except Exception as e:
                state_flag = False
                log_error_and_raise_exception(e)
        lock.release()
        return state_flag

def po4_samp_run_stop_AM():
        try: 
                lock.acquire()
                auxMotorOff()
                state_flag = True
        except Exception as e:
                state_flag = False
                log_error_and_raise_exception(e)
        lock.release()
        return state_flag

def po4_samp_run_port_change():
        global state_flag
        try:
                lock.acquire()
                '''Moves the CoV to a specified port then activates pumps to send predetermined amount of fluid at a set speed.'''
                # commented for test
                # move_8ports(sample_port)
                state_flag = True
        except Exception as e:
                state_flag = False
                log_error_and_raise_exception(e)
        lock.release()
        return state_flag

def po4_samp_run_start_pump():
        try: 
                lock.acquire()
                logging.info(f"Aspirating {abs(po4_sample_p1_amount)} uL pump_1 ")  
                print("Aspirating {po4_sample_p1_amount} uL pump_1 ")
                
                # send_speed(po4_sample_p1_speed, 1)                     #Pump 1 moves at speed set by po4_sample_p1_speed variable
                # send_amount(po4_sample_p1_amount, 1)                   #Pump 1 aspirates amount set by po4_sample_p1_amount varaible
                state_flag = True
        except Exception as e:
                state_flag = False
                log_error_and_raise_exception(e)
        lock.release()
        return state_flag

def po4_samp_run_wait_time():
        try:
                lock.acquire()
                logging.debug(f'Sleeping for {po4sampletime} seconds')
                print('Sleeping for {po4sampletime} seconds')
                # sleep(po4sampletime)                                     #Wait for n seconds
                state_flag = True
        except Exception as e:
                state_flag = False
                log_error_and_raise_exception(e)
        lock.release()
        return state_flag

def AR_port_change_reagent():
        global state_flag
        try: 
                '''Moves the CoV to a specified port then activates pumps to send predetermined amount of fluid at a set speed.'''
                # commented for test
                # move_8ports(molybdate_port)
                state_flag = True
        except Exception as e:
                state_flag = False
                log_error_and_raise_exception(e)

def Ar_start_pump_1_102():
        global state_flag
        try: 
                logging.info(f"Dispensing {molybdate_p1_amount} uL pump_1/ Aspirating {abs(molybdate_p2_amount)} uL pump_2") 
                print("Dispensing {molybdate_p1_amount} uL pump_1/ Aspirating {abs(molybdate_p2_amount)} uL pump_2")
                # stage_reagents(molybdate,-molybdate_p1_amount)
                # send_speed(molybdate_p1_speed, 1)                     #Pump 1 moves at speed set by molybdate_p1_speed variable
                # send_amount(molybdate_p1_amount, 1)                   #Pump 1 dispenses amount set by molybdate_p1_amount varaible
                # sleep(t0)
                state_flag = True
        except Exception as e:
                state_flag = False
                log_error_and_raise_exception(e)

def Ar_start_pump_2_103():
        global state_flag
        try:
                # stage_reagents(molybdate,-molybdate_p2_amount)                   
                # send_speed(molybdate_p2_speed, 2)                     #Pump 2 moves at speed set by molybdate_p2_speed variable
                # send_amount(molybdate_p2_amount, 2)                   #Pump 2 aspirates amount set by molybdate_p2_amount varaible
                state_flag = True
        except Exception as e:
                state_flag = False
                log_error_and_raise_exception(e)
                
def Ar_wait_1():
        global state_flag
        try:
                logging.debug(f'Sleeping for {molybdatetime} seconds')
                print("Sleeping for {molybdatetime} seconds")
                # sleep(molybdatetime)                                  #Wait for n seconds
                commit_reagents()
                state_flag = True
        except Exception as e:
                state_flag = False
                log_error_and_raise_exception(e)
    

#START OF CODE
#The system will run the blank sample sequence twice, then it will follow with the PO4 standard twice, then
#there will be one PO4 seawater sample run only three times. The system will then post process to calculate the
#the PO4 concentration. The system will then sleep for ~40 mins., then run only the PO4 seawater sample again, followed by
#and additional sleep cycle. This will be repeated again, then calibration process will be restarted(Running the complete
#code from the beginning)


device_state={
    "0":"status_check",
    "1":"operation_mode",
    "2":"sending_mode",
    "3":"collection_mode",
    "4":"command_buffer_status",
    "5":"data_collection_status",
    "6":"sleep",
    "7":"software_update",
    "8":"next_state_input",
    "9":"delay"
}

device_mode = "1"
error_restart_counter = 5
current_cycle_state = 0
next_cycle_state = 1
disk_full = 0
discard_history = 0

def check_device_data(dir):
    return round(get_size(dir)/(10**9),2)

def remove_device_data(start_path = '.'):
    # remove all the files
    f=0
    try : 
        for dirpath, dirnames, filenames in os.walk(start_path):
            try :
                for d in dirnames:
                    dp = join(dirpath, d)
                    os.system("sudo rm -rf " + "\"" + dp + "\"")
            except Exception as e:
                print("Error while removing folder : ",str(e))
                f=1
    except Exception as e:
        print(str(e))
        return False
    return True if f==0 else False

# Old Functions

# def run_cycle():

#         global idle_timer, start_time, sample_idle_timer,sleep_time
#         global string_data_file, logger
#         global blank, stand, sample, po4conc_array, sampletime_array
#         global ref_spec
#         global blank_sample_counter, sample_run_counter, standard_sample_counter, total_sample_runs
#         global mean_abs_stand, mean_abs_blank
#         global current_state, next_state, sample_interval_state_on
#         global n,lim_sample_runs
#         global q
#         # when reformat events, can combine timers together to be one 
#         # evt = check_for_event()
#         timer_check()
        
#         '''Moves state machine to next state and runs code for that state'''

#         print("Moves state machine to next state and runs code for that state")

#         if current_state == state_dict['Boot']: #1
                
#                 t = threading.Thread(target=boot )
#                 t.start()
#                 t.join()
                        
#                 next_state = q.get()
#                 change_mode()
        
#         elif (current_state == state_dict['Darkscan']):
#                 # if no command from user
#                 t = threading.Thread(target=dark_scan )
#                 t.start()
#                 t.join()

#                 next_state = q.get()
#                 change_mode()
                        
#         elif (current_state == state_dict['Blank Sample Run']):
                
#                 # if no command from user
#                 t = threading.Thread(target=blank_sam_run )
#                 t.start()
#                 t.join()

#                 next_state = q.get()
#                 change_mode()
                
#         elif (current_state == state_dict['PO4 Standard Run']):
        
#                 t = threading.Thread(target=po4_std_run )
#                 t.start()
#                 t.join()

#                 next_state = q.get()
#                 change_mode()
                        
#         elif (current_state == state_dict['PO4 Sample Run']):
#                 t = threading.Thread(target=po4_samp_run )
#                 t.start()
#                 t.join()

#                 next_state = q.get()
#                 change_mode()
                                                
#         elif (current_state == state_dict['Sample Interval']):
#                 print("into Sample Interval")
                        
#                 logging.info(f'Waiting to start next sample run')
#                 print('Waiting to start next sample run')
                
#                 sample_idle_timer.timer_set(new_interval=(next_sample_time-lamptime))
#                 lightOff()
                
#                 sample_interval_state_on=True
#                 next_state = state_dict['PO4 Sample Run']

#                 change_mode()
#                 # logging.info('Light turned off')

#         elif (current_state == state_dict['Save vars']):
#                 t = threading.Thread(target=save_vars )
#                 t.start()
#                 t.join()
                
#                 next_state = q.get()
#                 change_mode()
                        
#         elif (current_state == state_dict['Idle']):
#                 print("into Save vars")
#                 t = threading.Thread(target=idle )
#                 t.start()
#                 t.join()
                
#                 next_state = q.get()
#                 change_mode()
                        
#         elif (current_state == state_dict['Error']):
#                 # code went wrong somewhere and led to an invalid state. what now?
#                 print("Into Error")
#                 return 0
        
#         else:
#                 print("Invalid State", state_name)
#                 state_name = [index for index in state_dict if state_dict[index] == current_state] 
#                 logging.error(f'{state_name} is not a valid state')
#                 print('{state_name} is not a valid state')
#                 raise Exception(f'{state_name} is not a valid state')

#         current_state = next_state
#         return 1

# def get_size(start_path = '.'):
#     try :
#         for dirpath, dirnames, filenames in os.walk(start_path):
#             for f in filenames:
#                 fp = join(dirpath, f)
#                 os.remove(fp)
#     except Exception as e:
            
#     return total_size

# def user_command(evt:str):
#         '''Change the state or do an action depending on the string passed in'''

#         event = evt.upper().split('-')
#         # if it is not a parameter change
#         if (len(event) == 1):
#                 cmd = event[0]
#                 logging.debug(f'Received command: {cmd}')
#                 if (cmd == command_dict['REBOOT']):
#                         logging.info('Rebooting')
#                         syst('sudo shutdown -r now')
#                 elif (cmd == command_dict['SHUTDOWN']):
#                         logging.info('Shutting down')
#                         syst('sudo shutdown -h now')
#                 elif (cmd == command_dict['FLUSH']):
#                         logging.info('Flushing system then Darkscan')
#                         system_flush()
#                         reset_state_vars(state_dict['Darkscan'])
#                 elif (cmd == command_dict['CLEAR DATA']):
#                         logging.info('Fethcing data files and deleting folder')
#                         # handle data files here
#                         logging.debug('Handling data files before deletion incomplete')
#                         # delete and remake directory 
#                         rmtree(dirname(base_save_directory))
#                         makedirs(dirname(base_save_directory))
#                         logging.debug(f'Remade directory: {dirname(base_save_directory)}')
#                 elif (cmd == command_dict['SEND LAST DATA']):
#                         logging.debug('Milan to implement sending latest data file')
#                 elif (cmd == command_dict['SEND LAST DATA']):
#                         logging.debug('Milan to implement sending latest log file or set of vars')

#                         # create temp file to put all vars in 
#                         status_tmp_file = dirname(abspath(__file__))+'/.tmp/status.txt'
#                         if exists(abspath(status_tmp_file)):
#                                 remove(abspath(status_tmp_file))

#                         # copied from 'Save vars' state. do we want to change the vars?
#                         save_list_to_string('@blank_sample_absorbances', blank, our_file=status_tmp_file)
#                         save_list_to_string('@blank_sample_count', [num_blank_runs], our_file=status_tmp_file)
#                         save_list_to_string('@po4_sample_absorbances', sample, our_file=status_tmp_file)
#                         with open(status_tmp_file, 'a') as f:
#                                 f.write(f'@po4_sample_count {num_sample_runs}\n')
#                                 f.write(f'@num_of_sample_run {total_sample_runs}\n')
#                                 f.write(f'@num_ports {8}\n')
#                         for pre, pos in positions_8_ports.items():
#                                 save_list_to_string(f'@{pre}', [pos], our_file=status_tmp_file)
#                         with open(status_tmp_file, 'a') as f:
#                                 f.write(f'@monitoringlambda {monitoringlambda}\n')
#                                 f.write(f'@reflambda {reflambda}\n')
#                                 f.write(f'@known_concentration {known_concentration}\n')
#                         save_list_to_string('@po4_concentrations', po4conc_array, our_file=status_tmp_file)
#                         with open(status_tmp_file, 'a') as f:
#                                 f.write(f'@flush_p1_speed {flush_p1_speed}\n')
#                                 f.write(f'@flush_p1_amount {flush_p1_amount}\n')
#                                 f.write(f'@flush_p2_speed {flush_p2_speed}\n')
#                                 f.write(f'@flush_p2_amount {flush_p2_amount}\n')
#                                 f.write(f'@blank_p1_speed {blank_p1_speed}\n')
#                                 f.write(f'@blank_p1_amount {blank_p1_amount}\n')
#                                 f.write(f'@molybdate_p1_speed {molybdate_p1_speed}\n')
#                                 f.write(f'@molybdate_p1_amount {molybdate_p1_amount}\n')
#                                 f.write(f'@molybdate_p2_speed {molybdate_p2_speed}\n')
#                                 f.write(f'@molybdate_p2_amount {molybdate_p2_amount}\n')
#                                 f.write(f'@ascorbic_p1_speed {ascorbic_p1_speed}\n')
#                                 f.write(f'@ascorbic_p1_amount {ascorbic_p1_amount}\n')
#                                 f.write(f'@ascorbic_p2_speed {ascorbic_p2_speed}\n')
#                                 f.write(f'@ascorbic_p2_amount {ascorbic_p2_amount}\n')
#                                 f.write(f'@flow_cell_p1_speed {flow_cell_p1_speed}\n')
#                                 f.write(f'@flow_cell_p1_amount {flow_cell_p1_amount}\n')
#                                 f.write(f'@po4_standard_p1_speed {po4_standard_p1_speed}\n')
#                                 f.write(f'@po4_standard_p1_amount {po4_standard_p1_amount}\n')
#                                 f.write(f'@po4_sample_p1_speed {po4_sample_p1_speed}\n')
#                                 f.write(f'@po4_sample_p1_amount {po4_sample_p1_amount}\n')
#                                 f.write(f'@totalprimes {totalprimes}\n')
#                                 f.write(f'@port1_pp1speed {port1_pp1speed}\n')
#                                 f.write(f'@port1_pp1amount {port1_pp1amount}\n')
#                                 f.write(f'@port2_pp1speed {port2_pp1speed}\n')
#                                 f.write(f'@port2_pp1amount {port2_pp1amount}\n')
#                                 f.write(f'@port2_pp2speed {port2_pp2speed}\n')
#                                 f.write(f'@port2_pp2amount {port2_pp2amount}\n')
#                                 f.write(f'@port3_pp1speed {port3_pp1speed}\n')
#                                 f.write(f'@port3_pp1amount {port3_pp1amount}\n')
#                                 f.write(f'@port4_pp1speed {port4_pp1speed}\n')
#                                 f.write(f'@port4_pp1amount {port4_pp1amount}\n')
#                                 f.write(f'@port5_pp1speed {port5_pp1speed}\n')
#                                 f.write(f'@port5_pp1amount {port5_pp1amount}\n')
#                                 f.write(f'@port6_pp1speed {port6_pp1speed}\n')
#                                 f.write(f'@port6_pp1amount {port6_pp1amount}\n')
#                                 f.write(f'@port7_pp1speed {port7_pp1speed}\n')
#                                 f.write(f'@port7_pp1amount {port7_pp1amount}\n')
#                                 f.write(f'@port8_pp1speed {port8_pp1speed}\n')
#                                 f.write(f'@port8_pp1amount {port8_pp1amount}\n')
#                         vols = read_reagents()
#                         with open(status_tmp_file, 'a') as f:
#                                 f.write(f'@Ascorbic_Acid_Reagent_used {ascorbic_refill_amt-vols[3]/1000}\n')
#                                 f.write(f'@Ascorbic_Acid_Reagent_remaining {vols[3]/1000}\n')
#                                 f.write(f'@Molybdate_Reagent_used {molybdate_refill_amt-vols[0]/1000}\n')
#                                 f.write(f'@Molybdate_Reagent_remaining {vols[0]/1000}\n')
#                                 f.write(f'@PO4_Reagent_used {po4_refill_amt-vols[2]/1000}\n')
#                                 f.write(f'@PO4_Reagent_remaining {vols[2]/1000}\n')
#                                 f.write(f'@water_Reagent_used {water_refill_amt-vols[1]/1000}\n')
#                                 f.write(f'@water_Reagent_remaining {vols[1]/1000}\n')
#                                 f.write(f'@t0 {t0}\n')
#                                 f.write(f'@t1 {t1}\n')
#                                 f.write(f'@t3 {t3}\n')
#                                 f.write(f'@auxtime {auxtime}\n')
#                                 f.write(f'@darkscantime {darkscantime}\n')
#                                 f.write(f'@refscantime {refscantime}\n')
#                                 f.write(f'@time_required {time()-start_time}\n')
#                                 f.write(f'@aux_motor_status {__aux_motor_status}\n')
#                                 f.write(f'@motor1_speed {__speed_p1}\n')
#                                 f.write(f'@motor1_amount {__amount_p1}\n')
#                                 f.write(f'@motor1_status {__p1_status}\n')
#                                 f.write(f'@motor2_speed {__speed_p2}\n')
#                                 f.write(f'@motor2_amount {__amount_p2}\n')
#                                 f.write(f'@motor2_status {__p2_status}\n')
#                                 f.write(f'@next_sample_time {next_sample_time}\n')


#         # change parameter value
#         elif (len(event) == 3) and (event[0] == command_dict['PARAM']):
#                 param = event[1]
#                 val = event[2]
#                 logging.info(f'Received command to change {param} to {val}')
#                 for key, item in param_dict.items():
#                         if (key == param):
#                                 param_dict[key] = val
#                                 break
#                         else:
#                                 pass

                                        # STATE MACHINE FUNCTIONS


def blank_sample():
        '''Moves the CoV to a specified port then activates pumps to send predetermined amount of fluid at a set speed.'''
        # commented for test
        # move_8ports(waste_port) 
        logging.info(f"Dispensing Blank Sample: {blank_p1_amount} uL at {blank_p1_speed} uL/sec")    
        print("Dispensing Blank Sample: {blank_p1_amount} uL at {blank_p1_speed} uL/sec")
        # stage_reagents(water,blank_p1_amount)
        # send_speed(blank_p1_speed, 1)                         #Pump 1 moves at speed set by blank_p1_speed variable
        # send_amount(blank_p1_amount, 1)                       #Pump 1 dispenses amount set by blank_p1_amount varaible
        logging.debug(f'Sleeping for {blanktime} seconds')
        print("Sleeping for {blanktime} seconds")
        sleep(blanktime)                                      #wait for n seconds
        commit_reagents() # commented for test

def po4_standard():
        '''Moves the CoV to a specified port then activates pumps to send predetermined amount of fluid at a set speed.'''
        # commented for test
        # move_8ports(po4_port)
        logging.info(f"Aspirating {abs(po4_standard_p1_amount)} uL pump_1 ")
        print("Aspirating {po4_standard_p1_amount} uL pump_1 ")
        # stage_reagents(po4, -(po4_standard_p1_amount))
        # send_speed(po4_standard_p1_speed, 1)                  #Pump 1 moves at speed set by po4_standard_p1_speed variable
        # send_amount(po4_standard_p1_amount, 1)                #Pump 1 aspirates amount set by po4_standard_p1_amount varaible
        logging.debug(f'Sleeping for {po4standardtime} seconds')
        print("Sleeping for {po4standardtime} seconds")
        sleep(po4standardtime)                                  #Wait for n seconds
        commit_reagents()

def po4_sample():
        '''Moves the CoV to a specified port then activates pumps to send predetermined amount of fluid at a set speed.'''
        # commented for test
        # move_8ports(sample_port)
        logging.info(f"Aspirating {abs(po4_sample_p1_amount)} uL pump_1 ")  
        print("Aspirating {po4_sample_p1_amount} uL pump_1 ")
        
        # send_speed(po4_sample_p1_speed, 1)                     #Pump 1 moves at speed set by po4_sample_p1_speed variable
        # send_amount(po4_sample_p1_amount, 1)                   #Pump 1 aspirates amount set by po4_sample_p1_amount varaible
        logging.debug(f'Sleeping for {po4sampletime} seconds')
        print('Sleeping for {po4sampletime} seconds')
        sleep(po4sampletime)                                     #Wait for n seconds

                                        # SPECTOMETER FUNCTIONS

# def darkscan_run():
#         '''Do darkscan before each set of runs.

#         returns dark_spec from spectro_darkscan(spec)'''
#         global last_darkspec

#         if __light_status == 'ON':
#                 lightOff()
#                 sleep(darkscantime)
#         dark_spec=spectro_darkscan(spec)
#         last_darkspec = dark_spec
#         lightOn()
#         logging.debug(f'Sleeping for {lamptime} seconds')
#         sleep(lamptime)

#         return dark_spec
