#------------------------------------------------------------------------------
#'RadioFunctions.py'                                Hearn WSU-ECE
#                                                   17apr23
# Open-Source Antenna Pattern Measurement System
#
# RadioFunctions-contains the helper functions for the radio system that are
# not part of any other class
#  
# Performs the following project-specific functions:
#   LoadParams = imports 'json' file with inputs
#   InitMotor   
#   OpenDatafile
#   rms
#   do_single
#   do_AMscan
#   do_AMmeas
#   do_NSmeas
#   get_plot_data
#   PlotFile()
#   PlotFiles()
#
#   RxRadio
#   Tx Radio
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# WSU-ECE legal statement here
#------------------------------------------------------------------------------
import numpy as np
from PlotGraph import PlotGraph
import json
import RxRadio
import TxRadio
from MotorController import MotorController
import matplotlib.pyplot as plt
import time
#------------------------------------------------------------------------------
def LoadParams(filename=None):
    """ Load parameters file
        parameters are a dictionary saved in a json file
        if filename is not given then a default file will be used
        any parameters not given in the file will be used from the default file
        if the file cannot be found it will raise an exception
    """
    try:
        defaults=json.load(open("params_default.json"))
    except Exception as e:
        print("params_default.json file is missing")
        raise e 
    if filename==None:
        return defaults
    try:
        params=json.load(open(filename))
    except Exception as e:
        print("Failed to load parameter file {:s}".format(filename))
        raise e
    #--------------------------------------------------------------------------
    # print(params)
    # go through all parameters given in the params file and
    # overwrite the defaults with any that are given
    #--------------------------------------------------------------------------
    for p in defaults:
        if p in params:
            defaults[p]=params[p]
        else:
            print("Parameter {:s} not specified in {:s} using default of ".format(p,filename),defaults[p])
    #--------------------------------------------------------------------------        
    # make sure freqency is within hackrf range
    #--------------------------------------------------------------------------
    if defaults["frequency"] < 30e6 or defaults["frequency"] > 6e9:
        #raise Excpetion("Frequency {:e} out of range".format(defaults["frequency"]))
        raise Exception("Frequency {:e} out of range".format(defaults["frequency"]))
    return defaults
#------------------------------------------------------------------------------
def InitMotor(params):
    motor_controller = MotorController(
    params["usb_port"],
    params["baudrate"])
    try:
        motor_controller.connect()
        print("Success: Motor controller fully connected.")
    except Exception as e:
        print("Error: Motor controller not responding, verify connections.")
        raise e
    motor_controller.reset_orientation()
    return motor_controller
#------------------------------------------------------------------------------
def OpenDatafile(params):
    filename= time.strftime("%d-%b-%Y_%H-%M-%S") + params["filename"]
    datafile_fp = open(filename, 'w')
    datafile_fp.write(params["notes"]+"\n")
    datafile_fp.write("% Mast Angle, Arm Angle, Background RSSI, Transmission RSSI\n")
    return datafile_fp
#------------------------------------------------------------------------------
def rms(data):
    """ return the rms of a data vector """
    return np.sqrt(np.square(data).mean())
#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
def do_single(Tx=True):
    params=LoadParams()
    if Tx:
        radio_tx_graph = TxRadio.RadioFlowGraph(
            params["tx_radio_id"], 
            params["frequency"], 
            params["tx_freq_offset"])
    radio_rx_graph = RxRadio.RadioFlowGraph(
        params["rx_radio_id"], 
        params["frequency"], 
        params["rx_freq_offset"],
        numSamples=10000)
    if Tx:
        radio_tx_graph.start()
    radio_rx_graph.start()
    radio_rx_graph.wait()
    if Tx:
        radio_tx_graph.stop()
    rxd=radio_rx_graph.vector_sink_0.data()
    plt.plot(rxd)
    plt.show()
    return rms(rxd)
#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
def do_AMscan(params):
    motor_controller = InitMotor(params)
    datafile = OpenDatafile(params) 
    radio_tx_graph = TxRadio.RadioFlowGraph(
        params["tx_radio_id"], 
        params["frequency"], 
        params["tx_freq_offset"]) 
    radio_rx_graph = RxRadio.RadioFlowGraph(
        params["rx_radio_id"], 
        params["frequency"], 
        params["rx_freq_offset"])
    AMantenna_data   = []
    radio_tx_graph.start()
    time.sleep(3)                                             # Tx latency
    print("Moving to start angle")
    motor_controller.rotate_mast(params["mast_start_angle"]);
    print("Collecting data while moving to end angle")
    radio_rx_graph.start()
    motor_controller.rotate_mast(params["mast_end_angle"]);
    radio_rx_graph.stop()
    radio_tx_graph.stop();                                    # stop Tx
    print("Finished collection, return to 0")                 #
    motor_controller.rotate_mast(0);                          # Reset AUT
    antenna_data=radio_rx_graph.vector_sink_0.data()
    n=len(antenna_data)
    print("read {:d} data_points".format(n))
    antenna_pow = np.square(antenna_data)
    numangles = params["mast_end_angle"]-params["mast_start_angle"] 
    binsize=int(n/numangles)
    print("binsize= {:d}".format(binsize))
    avg=np.zeros(numangles)
    for i in range(numangles):
        avg[i]=np.sqrt(np.square(
            antenna_data[i*binsize:(i+1)*binsize]).sum()/binsize)
    angles = range(int(params["mast_start_angle"]), int(params["mast_end_angle"]),1)
    arm_angle = np.zeros(len(avg));
    background_rssi = np.zeros(len(avg));
    plt.plot(antenna_pow)
    plt.show()
    plt.plot(avg)
    plt.show()
    print("avg {:d}".format(len(avg)),binsize)
    for i in range(len(avg)):
        datafile.write(
                str(angles[i]) + ',' + 
                str(arm_angle[i]) + ',' + 
                str(background_rssi[i]) + ',' + 
                str(avg[i]) + '\n'
                )
        AMantenna_data.append((angles[i], arm_angle[i], 
            background_rssi[i], avg[i]))

    datafile.close();
    print("datafile closed")

    return AMantenna_data
#-----------------------------------------------------------------------------
#def do_AMscan_slow(params):
#------------------------------------------------------------------------------
def do_AMmeas(params):
    motor_controller = InitMotor(params)
    datafile = OpenDatafile(params) 
    radio_tx_graph = TxRadio.RadioFlowGraph(
        params["tx_radio_id"], 
        params["frequency"], 
        params["tx_freq_offset"]) 
    radio_rx_graph = RxRadio.RadioFlowGraph(
        params["rx_radio_id"], 
        params["frequency"], 
        params["rx_freq_offset"], 
        numSamples=params["rx_samples"])
    antenna_data = []

    mast_angles = np.linspace(
        params["mast_start_angle"], 
        params["mast_end_angle"], 
        params["mast_steps"])
    arm_angles = np.linspace(params["arm_start_angle"], 
        params["arm_end_angle"], 
        params["arm_steps"])
    radio_tx_graph.start()
    time.sleep(3)                         # Tx latency 
    for mast_angle in mast_angles:        # azimuth control
        for arm_angle in arm_angles:      # elevation control (under constr)
            background_rssi = 0.0
            transmission_rssi = 0.0
            #
            print("Target Mast Angle: "+str(mast_angle))
            print("Target Arm Angle: "+str(arm_angle))
            print("Moving antenna...")
            motor_controller.rotate_mast(mast_angle)
            motor_controller.rotate_arm(arm_angle)
            print("Movement complete")
            #------------------------------------------------------------------
            # transmission rssi reading
            #------------------------------------------------------------------
            print("Taking transmitted signal sample...")
            radio_rx_graph.start()
            radio_rx_graph.wait()
            #radio_rx_graph.stop()
            # get data from the receiver and reset its output vector
            data=radio_rx_graph.vector_sink_0.data()
            radio_rx_graph.vector_sink_0.reset()
            radio_rx_graph.blocks_head_0.reset()
            #------------------------------------------------------------------
            #originally trimmed like this NW
            #data_points = delete(data_points, range(399000));
            #------------------------------------------------------------------
            print("read {:d} data_points".format(len(data)))
            transmission_rssi=np.sqrt(np.square(data).mean())
            print("Transmission RSSI: {:.3e}".format(transmission_rssi))
            print("Saving samples")
            datafile.write(
                str(mast_angle) + ',' + 
                str(arm_angle) + ',' + 
                str(background_rssi) + ',' + 
                str(transmission_rssi) + '\n'
                )
            antenna_data.append((mast_angle, arm_angle, 
                background_rssi, transmission_rssi))
    print("Returning mast and arm to home position...")
    motor_controller.rotate_mast(0)
    motor_controller.rotate_arm(0)
    print("Mast and arm should now be in home position")
    datafile.close();
    print("datafile closed")
    print("Scan completed")
    radio_tx_graph.stop()
    radio_tx_graph.wait()
    #
    return antenna_data
#------------------------------------------------------------------------------
# non-coherent noise-subtraction method (1st algorithm)
def do_NSmeas(params):
    motor_controller = InitMotor(params)
    datafile = OpenDatafile(params) 
    radio_tx_graph = TxRadio.RadioFlowGraph(
        params["tx_radio_id"], 
        params["frequency"], 
        params["tx_freq_offset"]) 
    radio_rx_graph = RxRadio.RadioFlowGraph(
        params["rx_radio_id"], 
        params["frequency"], 
        params["rx_freq_offset"], 
        numSamples=params["rx_samples"])
    antenna_data = []
    mast_angles = np.linspace(
        params["mast_start_angle"], 
        params["mast_end_angle"], 
        params["mast_steps"])
    arm_angles  = np.linspace(
        params["arm_start_angle"], 
        params["arm_end_angle"], 
        params["arm_steps"])

    for mast_angle in mast_angles:                           # azimuth
         for arm_angle in arm_angles:                        # elevation

             background_rssi = 0.0
             transmission_rssi = 0.0

             print("Target Mast Angle: "+str(mast_angle))
             print("Target Arm Angle: "+str(arm_angle))
             print("Moving antenna...")
             motor_controller.rotate_mast(mast_angle)
             motor_controller.rotate_arm(arm_angle)
             print("Movement complete")
             print("Taking background noise sample...")       # bkgrnd rssi 
             radio_rx_graph.start()
             radio_rx_graph.wait()
             #-----------------------------------------------------------------
             # get data from the receiver and reset its output vector
             # TODO the other scans use RMS, this just does average? 
             #-----------------------------------------------------------------
             data=radio_rx_graph.vector_sink_0.data()
             print("received {:d} background samples".format(len(data)))
             radio_rx_graph.vector_sink_0.reset()
             radio_rx_graph.blocks_head_0.reset()
             background_rssi = rms(data)
             #-----------------------------------------------------------------
             # Transmission rssi reading
             #-----------------------------------------------------------------
             print("Taking transmitted signal sample...")
             radio_tx_graph.start()
             time.sleep(1.3)                                  # Tx latency
             radio_rx_graph.start()
             radio_rx_graph.wait()
             radio_tx_graph.stop()
             radio_tx_graph.wait()
             # get data from the receiver and reset its output vector
             data=radio_rx_graph.vector_sink_0.data()
             print("received {:d} transmitted samples".format(len(data)))
             radio_rx_graph.vector_sink_0.reset()
             radio_rx_graph.blocks_head_0.reset()
             #-----------------------------------------------------------------
             # TODO the other scans use RMS, this just does average? 
             #-----------------------------------------------------------------
             transmission_rssi = rms(data)
             #-----------------------------------------------------------------
             # write rssi readings to file print("Saving samples")
             #-----------------------------------------------------------------
             datafile.write(
                 str(mast_angle) + ',' + 
                 str(arm_angle) + ',' + 
                 str(background_rssi) + ',' + 
                 str(transmission_rssi) + '\n'
                 )
             print("Sample angle={:f} bkgnd={:e} received={:e}".format(
                 mast_angle, background_rssi,transmission_rssi))
             antenna_data.append((mast_angle, arm_angle, 
                background_rssi, transmission_rssi))
    print("Returning mast and arm to home position...")
    motor_controller.rotate_mast(0)
    motor_controller.rotate_arm(0)
    print("Mast and arm should now be in home position")
    datafile.close()
    return antenna_data
#------------------------------------------------------------------------------
# plot functions for menu
#------------------------------------------------------------------------------
def get_plot_data(text):
    dataPoint = 0
    fileData = []
    for dataString in text:
        dataPointString = ''
        dataTuple = []
        for tempChar in dataString:
            if tempChar == ',' or tempChar == '\n':
                dataPoint = float(dataPointString)
                dataTuple.append(dataPoint)
                dataPointString = ''
            else:
                dataPointString += tempChar
        fileData.append((dataTuple[0],dataTuple[1],dataTuple[2],dataTuple[3]))
    return fileData;
def PlotFile():
    fileName = input("Enter the name of the data to plot\n")
    fr = open(fileName)
    text = fr.readlines()
    fr.close()
    text.remove(text[0])
    text.remove(text[0])
    fileData = get_plot_data(text);
    plot_graph = PlotGraph(fileData, fileName)
    plot_graph.show()
def PlotFiles():
    fileName = input("Enter the name of first file to plot\n")
    fr = open(fileName)
    text = fr.readlines()
    fr.close()
    text.remove(text[0])
    text.remove(text[0])
    fileData = get_plot_data(text);
    plot_graph1 = PlotGraph(fileData, fileName)
    fileName = input("Enter the name of the second file to plot\n")
    fr = open(fileName)
    text = fr.readlines()
    fr.close()
    text.remove(text[0])
    text.remove(text[0])
    fileData = get_plot_data(text);
    plot_graph2 = PlotGraph(fileData, fileName)
    ax1 = plt.subplot(111, projection='polar')
    ax1.set_theta_zero_location("N")
    theta1 = [angle*(np.pi/180) for angle in plot_graph1.mast_angles]
    ax1.plot(theta1, plot_graph1.rssi, label="With Gain")
    ax2 = plt.subplot(111, projection='polar')
    ax2.set_theta_zero_location("N")
    theta2 = [angle*(np.pi/180) for angle in plot_graph2.mast_angles]
    ax2.plot(theta2, plot_graph2.rssi, label="No Gain", linewidth=1)
#    
    if plot_graph1.plot_in_db == 'y':
        ax1.set_rticks([-20,-16,-12,-8,-4,0]);
        ax2.set_rticks([-20,-16,-12,-8,-4,0]);
    plt.legend(loc="lower center", bbox_to_anchor=(1, 1))
    plt.show()
#--------------------------------------------------------------------------EoF
