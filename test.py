#!/usr/bin/python3

def main():
    radio_listener = RadioListener()
    radio_listener.start()

    radio_tx_graph = RadioFlowGraph(
        params["tx_radio_id"],
        params["frequency"], 
        params["tx_freq_offset"], 
        params["data_port"])
    radio_tx_graph.set_tx_gain(0, 0)
    radio_tx_graph.setup_flowgraph(transmitter=True)
    radio_rx_graph = RadioFlowGraph(
        params["rx_radio_id"], 
        params["frequency"], 
        params["rx_freq_offset"], 
        params["data_port"])
    radio_rx_graph.setup_flowgraph(transmitter=False)

    mast_angles = linspace(
        params["mast_start_angle"], 
        params["mast_end_angle"], 
        params["mast_steps"])
    arm_angles  = linspace(
        params["arm_start_angle"], 
        params["arm_end_angle"], 
        params["arm_steps"])

    for mast_angle in mast_angles: # simulate n readings around antenna
         for arm_angle in arm_angles: # simulate n readings around antenna

             background_rssi = 0.0
             transmission_rssi = 0.0

             print("Target Mast Angle: "+str(mast_angle))
             print("Target Arm Angle: "+str(arm_angle))
             print("Moving antenna...")
             motor_controller.rotate_mast(mast_angle)
             motor_controller.rotate_arm(arm_angle)
             print("Movement complete")
             print("Taking background noise sample...")                    # background rssi reading
             radio_rx_graph.start()
             radio_rx_graph.wait()
             if radio_listener.is_data_available():
                 background_rssi = radio_listener.get_data_average()
                 print("Background RSSI: "+str(background_rssi))
             else:
                 print("ERROR: Background RSSI unavailable!")
# Transmission rssi reading
             print("Taking transmitted signal sample...")
             radio_tx_graph.start()
             time.sleep(1.3) # give the transmitter flowgraph enough time to actually broadcast
             radio_rx_graph.start()
             radio_rx_graph.wait()
             radio_tx_graph.stop()
             radio_tx_graph.wait()
             if radio_listener.is_data_available():
                 transmission_rssi = radio_listener.get_data_average()
                 print("Transmission RSSI: "+str(transmission_rssi))
             else:
                 print("ERROR: Transmission RSSI unavailable!")
# write rssi readings to file
             print("Saving samples")
             datafile_fp.write(
                 str(mast_angle) + ',' + 
                 str(arm_angle) + ',' + 
                 str(background_rssi) + ',' + 
                 str(transmission_rssi) + '\n'
                 )
             antenna_data.append((mast_angle, arm_angle, background_rssi, transmission_rssi))
# return mast and arm to home position (0 degrees, 0 degrees)
    print("Returning mast and arm to home position...")
    motor_controller.rotate_mast(0)
    motor_controller.rotate_arm(0)
    print("Mast and arm should now be in home position")
 #   print("Scan completed, data saved in "+str(filename))
    radio_listener.stop()
    net_listener.stop()
    return antenna_data
#
#
def do_AMscan(params):
    AMantenna_data   = []
    motor_controller.rotate_mast(-180);
#
    radio_tx_graph = RadioFlowGraphAM.RadioFlowGraph(
        params["tx_radio_id"], 
        params["frequency"],
        params["tx_freq_offset"],
        params["data_port"])
    radio_tx_graph.setup_flowgraph(transmitter=True)
    radio_rx_graph = RadioFlowGraphAM.RadioFlowGraph(
        params["rx_radio_id"],
        params["frequency"],
        params["rx_freq_offset"], 
        params["data_port"])
    radio_rx_graph.setup_flowgraph(transmitter=False)
    radio_tx_graph.start()
    # give the transmitter flowgraph enough time to actually broadcast
    time.sleep(3)  
    t1 = threading.Thread(target=radio_rx_graph.start);
    t2 = threading.Thread(target=radio_rx_graph.wait);
    t1.start();      #start reciever
    t2.start();      #wait until motor has completed full 360 degree turn
    motor_controller.rotate_mast(180);
#                   #Radio rx stop is creates a loop and the program gets stuck?
#                    #radio_rx_graph.stop(); #stop reciever
    radio_tx_graph.stop();                                 #stop transmitter
    t1.join();
    t2.join();
    motor_controller.rotate_mast(0);                       #reset antenna position
   
    antenna_data = fromfile(open("antenna_data.bin"), dtype=scipy.float32);

    antenna_pow = [];
    for i in range(len(antenna_data)):
        antenna_pow.append(antenna_data[i]*antenna_data[i]);
    antenna_pow = delete(antenna_pow, range(1000));

    avg = [];
    asum = 0;
    for i in range(len(antenna_pow)):
        asum += antenna_pow[i];
        if (i+1)%1000 == 0:
            asum = asum/1000;
            avg.append(asum);
            asum = 0;

    avg = array(avg);
    avg = sqrt(avg);
    rad = linspace(-180, 180, len(avg));
    
    arm_angle = zeros(len(avg));
    background_rssi = zeros(len(avg));

    for i in range(len(avg)):
        params["datafile_fp"].write(
                str(rad[i]) + ',' + 
                str(arm_angle[i]) + ',' + 
                str(background_rssi[i]) + ',' + 
                str(avg[i]) + '\n'
                )
        AMantenna_data.append((rad[i], arm_angle[i], background_rssi[i], avg[i]))

    params["datafile_fp"].close();
    print("datafile closed")

    return AMantenna_data

def do_AMscan_slow(params):
# frequency,mast_steps,mast_start_angle,mast_end_angle,arm_steps,arm_start_angle,arm_end_angle = parameters
# perform a scan with the given sweep limits and step resolution
    net_listener = NetworkListener()
    net_listener.start()

    motor_controller = MotorController(params["usb_port"], params["baudrate"])
    if motor_controller.connect():
        print("Successfully connected to motor controller.")
    else:
        print("Error: Motor controller not responding, verify connections.")
    motor_controller.reset_orientation()

    tx_freq_offset = 0
    rx_freq_offset = -7e3
    data_port = 8888
    
    header_notes = '% ';
    header_notes = header_notes + input("Enter notes for header of file: ");
    header_notes = header_notes + '\n';

    radio_listener = RadioListener()
    radio_listener.start()

    radio_tx_graph = RadioFlowGraphAMslow.RadioFlowGraph(
        params["tx_radio_id"], 
        params["frequency"], 
        params["tx_freq_offset"], 
        params["data_port"])
    print('radio_tx_graph1')
    radio_tx_graph.set_tx_gain(0, 0)
    print('radio_tx_graph2')
    radio_tx_graph.setup_flowgraph(transmitter=True)
    print('radio_tx_graph3')
    radio_rx_graph = RadioFlowGraphAMslow.RadioFlowGraph(
        params["rx_radio_id"], 
        params["frequency"], 
        params["rx_freq_offset"], 
        params["data_port"])
    print('radio_tx_graph4')
    radio_rx_graph.setup_flowgraph(transmitter=False)
    # open antenna scan log file and add data header
    print('open antenna scan log file and add data header')
    filename_prefix = time.strftime("%d-%b-%Y_%H-%M-%S")
    filename = filename_prefix + "_antenna_data.txt"
    datafile_fp = open(filename, 'w')
    datafile_fp.write(header_notes)
    datafile_fp.write("% Mast Angle, Arm Angle, Background RSSI, Transmission RSSI\n")
    antenna_data = []

    mast_angles = linspace(
        params["mast_start_angle"], 
        params["mast_end_angle"], 
        params["mast_steps"])
    arm_angles = linspace(params["arm_start_angle"], 
        params["arm_end_angle"], 
        params["arm_steps"])
    
    radio_tx_graph.start()
    time.sleep(3) # give the transmitter flowgraph enough time to actually broadcast

    for mast_angle in mast_angles: # simulate n readings around antenna
        for arm_angle in arm_angles: # simulate n readings around antenna

            background_rssi = 0.0
            transmission_rssi = 0.0

            print("Target Mast Angle: "+str(mast_angle))
            print("Target Arm Angle: "+str(arm_angle))
            print("Moving antenna...")
            motor_controller.rotate_mast(mast_angle)
            motor_controller.rotate_arm(arm_angle)
            print("Movement complete")

            # transmission rssi reading
            print("Taking transmitted signal sample...")
            radio_rx_graph.start()
            radio_rx_graph.wait()

            if radio_listener.is_data_available():
                radio_listener.trim_data();
                radio_listener.square_data();
                transmission_rssi = sqrt(radio_listener.get_data_average());
                print("Transmission RSSI: "+str(transmission_rssi))
            else:
                print("ERROR: Transmission RSSI unavailable!")

            # write rssi readings to file
            print("Saving samples")
            params["datafile_fp"].write(
                str(mast_angle) + ',' + 
                str(arm_angle) + ',' + 
                str(background_rssi) + ',' + 
                str(transmission_rssi) + '\n'
                )
            antenna_data.append((mast_angle, arm_angle, background_rssi, transmission_rssi))

    # return mast and arm to home position (0 degrees, 0 degrees)
    print("Returning mast and arm to home position...")
    motor_controller.rotate_mast(0)
    motor_controller.rotate_arm(0)
    print("Mast and arm should now be in home position")

    print("Scan completed, data saved in "+str(filename))

    params["datafile_fp"].close();
    print("datafile closed")


    radio_listener.stop()
    net_listener.stop()

    radio_tx_graph.stop()
    radio_tx_graph.wait()

    return antenna_data

if __name__ == "__main__":
    main()

