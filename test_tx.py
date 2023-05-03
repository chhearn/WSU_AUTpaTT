#!/usr/bin/python3
import numpy as np
import sys
import os
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
    print("received {:d}".format(len(d)))
    print(d[0:2])
    radio_tx_graph.head_0.reset()
    radio_tx_graph.vector_sink_0.reset()
    radio_tx_graph.run()
    d2=radio_tx_graph.vector_sink_0.data()
    print("received {:d}".format(len(d2)))
    print(d2[0:2])
    plt.plot(d)
    plt.plot(d2)
    plt.show()

if __name__ == "__main__":
    main()

