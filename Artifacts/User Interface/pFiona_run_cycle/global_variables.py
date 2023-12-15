state_dict = {

        'Boot': 0, 'Darkscan': 1, 'Blank Sample Run': 2, 'PO4 Standard Run': 3, 'PO4 Sample Run': 4, #all of the main runs
        'Idle': 6, 'Sample Interval': 8, 'Error': None, 

        'BSR Set Valve to Port 2':21,'BSR Start Pump 1':22,'BSR Wait':23, #blank sample run devided

        'PStR Set Valve to Port 6':31,'PStR Start Pump 1':32,'PStR Wait':33, #p04 standard run devided


        'PSaR Start Aux Motor':41,'PSaR Stop Aux Motor':42,'PSaR Set Valve to Port 4':43, #po4 sample run devided
        'PSaR Start Pump 1':44, 'PSaR Wait':45,

        'Save vars': 7,'Save variables to txt file':71,'Create new text and log file':72,'Wait for next cycle':73, 

        'Acid_Reagent':100,
        'AR Set Valve to Port 3(reagent)':101,'AR Start Pump 1':102,'AR Start Pump 2':103,'AR Wait 1':104,  #Acid and Reagent flow devided
        'AR Set Valve to Port 5(acid)':105,'AR Set Valve to Port 2(Dispense solution for Flow Cell)':106,'AR Start Pump 1 2':107,
        'AR Wait 2':108,'AR Get Absorbances':109,'AR System flush':110,'AR Save Absorbances as txt file on device':111,

        'NBSR Set Valve to Port 3(reagent)':91,'NBSR Start Pump 1':92,'NBSR Wait 1':93, #If not blank sample run devided
        'NBSR Set Valve to Port 6(PO4 standard)':94,'NBSR Start Pump 1':95,'NBSR Wait 2':96

}


current_state = state_dict['Boot']
next_state = ""