#!/usr/bin/python3
import numpy as np
import sys
import os
import RxRadio
import TxRadio
import RadioFunctions
import traceback
import time
import matplotlib.pyplot as plt

def main():
    params=RadioFunctions.LoadParams()
    radio_tx_graph = TxRadio.RadioFlowGraph(
        params["tx_radio_id"], 
        params["frequency"], 
        params["tx_freq_offset"],
        simulate=True, 
        numSamples=10000)
#    radio_tx_graph.set_tx_gain(0, 0)
    radio_tx_graph.run()
    d=radio_tx_graph.vector_sink_0.data()
    radio_rx_graph = RxRadio.RadioFlowGraph(
        params["rx_radio_id"], 
        params["frequency"], 
        params["rx_freq_offset"],
        simulation=True,
        numSamples=10000)
#    radio_tx_graph.set_tx_gain(0, 0)
    radio_rx_graph.vector_source_0.set_data(d)
    radio_rx_graph.run()
    rxd=radio_rx_graph.vector_sink_0.data()
    print("received {:d}".format(len(rxd)))
    print(rxd[0:2])
    plt.plot(rxd)
    plt.show()
    plt.figure("input")
    plt.plot(d)
    plt.show()

if __name__ == "__main__":
    main()

