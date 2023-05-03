#!/usr/bin/python3
#------------------------------------------------------------------------------
#'main.py'                                          Hearn WSU-ECE
#                                                   17apr23
# Open-Source Antenna Pattern Measurement System
# Performs the following project-specific functions:
#   1.input parameters from 'params.json' file (pre-loaded by user) 
#   2.menu algorithm
#   3.calls RadioFunctions    
#       a) FastScan - coherent AM quick scan
#       b) AMmeas   - coherent AM fixed measurement 
#       c) NSmeas   - Noise Subtraction measurement 
#       d) post-processing - pattern plotting options
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# WSU-ECE legal statement here
#------------------------------------------------------------------------------
from PlotGraph import PlotGraph
import RadioFunctions
import traceback
#
def main():
    quit = False
    data = None    
    #--------------------------------------------------------------------------
    # user should preload measurement parameters in "params.json" file
    #--------------------------------------------------------------------------
    param_filename="params.json"
    menu_choices = []
    menu_choices.append("FastScan AUT w/ coherent AM method")              # 1
    menu_choices.append("Measure  AUT w/ coherent AM method")              # 2
    menu_choices.append("Measure  AUT w/ NoiseSub NS method")              # 3
    menu_choices.append("Plot last run data")                              # 4
    menu_choices.append("Plot data from file")                             # 5
    menu_choices.append("Plot data from two files")                        # 6
    menu_choices.append("Capture single measurement")                      # 7
    menu_choices.append("Capture single background")                       # 8
    menu_choices.append("Quit")                                            # 9
    #
    while not quit:
        try:
            selection = show_menu(menu_choices)               
            if selection == 1: 
                params = RadioFunctions.LoadParams(param_filename)
                data = RadioFunctions.do_AMscan(params)
                print(data)
            elif selection == 2: 
                params = RadioFunctions.LoadParams(param_filename)
                data = RadioFunctions.do_AMmeas(params)
                print(data)
            elif selection == 3: 
                params = RadioFunctions.LoadParams(param_filename)
                data = RadioFunctions.do_NSmeas(params)
                print(data)
            elif selection == 4:                              
                if data is None:                              
                    print("run scan before plotting data\n")  
                    continue                                  
                title = input("Enter a title for the graph: ")
                plot_graph = PlotGraph(data, title)           
                plot_graph.show()                             
            elif selection == 5:                               
                RadioFunctions.PlotFile()                     
            elif selection == 6:                              
                RadioFunctions.PlotFiles()                    
            elif selection == 7:                              
                print("Single measurement")                   
                data = RadioFunctions.do_single(Tx=True)      
                print("RMS = {:.3e}".format(data))            
            elif selection == 8:                              
                print("Single background measurement")        
                data = RadioFunctions.do_single(Tx=False)     
                print("RMS = {:.3e}".format(data))            
            elif selection == 9:                              
                print("Exiting...\n")                         
                quit = True                                   
        except Exception as e:                                
            print("Operation failed")                         
            print(e)                                          
            print(traceback.format_exc())                     
            input("Press enter to continue")                  
    return                                                    # exit-user quit
#------------------------------------------------------------------------------
def show_menu(choices):                                       #
    if choices == []:                                         #
        return None                                           #
    row_num = 1                                               # print choices
    print("\n\n\n")                                           # on screen
    print("Please select from the following options:\n\n")    #
    for choice in choices:                                    #
        print(str(row_num)+": "+str(choice)+"\n")             #
        row_num += 1                                          #
    print("\n")                                               #
    selection = 0                                             # get response
    while selection < 1 or selection > len(choices):          #
        try:                                                  #
            selection = int(input("Please enter selection: "))#
        except ValueError:                                    #
            selection = 0                                     #
    return selection                                          #
#------------------------------------------------------------------------------
if __name__ == "__main__":                                    #
    main()                                                    # EoF

