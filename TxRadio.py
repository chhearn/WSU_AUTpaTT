# NW 2023-04-05 factor out the receiver functions

from gnuradio import analog
from gnuradio import blocks
from gnuradio import network
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.filter import window
import osmosdr

class RadioFlowGraph(gr.top_block):
    def __init__(self, radio_id, frequency, 
        tx_rf_gain=0, tx_if_gain=3, freq_offset=0, 
        simulate=False, numSamples=None):
        """ init the transmitter radio
            radio_id is hex string radio serial number like 61555f 
            frequency is the center frequency
            freq_offset is the offset from the center freq
            simulate is a flag to run in simulation mode.  
                if false then the output is to the sdr
                if true then the output goes to vector_sink_0
            numSamples makes the transmitter only run for numSamples output TODO only works for simulation
        """
        gr.top_block.__init__(self)
        self.radio_id = radio_id # radio id string (osmosdr radio id)
        print("Radio id {:s}".format(self.radio_id))
        self.frequency = frequency
        self.freq_offset = freq_offset
        # max radio sample rate is 20Ms/sec, minimum is 2Ms/sec, due to HackRF frontend noise 
        # the ideal minimum is 8Ms/sec
        #self.radio_sample_rate = 8e6
        self.radio_sample_rate = 20e6
        #self.radio_sample_rate = 2e6
        self.bandwidth = 5e3 # set low to ensure we don't leak RF everywhere during transmit
        self.transition = 500 # used by low-pass filters
        self.set_tx_gain(tx_rf_gain,tx_if_gain)
        # intermediate sample rates for the rational resamplers, need enough resamplers and
        # sample rates chosen so no single resampler has a decimation greater than 200 due
        # to block/window limitations
        self.int1_sample_rate = 200000 # max radio sample rate = 20Ms/sec, decimate by <= 100
        self.int2_sample_rate = 10000 # int1 sample rate decimated by 10
        self.final_sample_rate = 2000 # final sample rate
        # TODO get sample rates and numbers from outside
        self.num_final_samples = 1000 # recorded samples for each point on the antenna sphere, ideal min 1000
        # calculate the total number of samples so the flowgraph buffers are empty at the
        # right time, stopping further capturing and processing of unneeded samples
        self.num_total_samples = int((float(self.num_final_samples)/self.final_sample_rate)*self.radio_sample_rate)
        ### transmitter blocks ###
        src="numchan=1 hackrf=" + self.radio_id
        print("transmitter {:s}".format(src))
        if not simulate:
            self.osmosdr_sink_0 = osmosdr.sink( args=src )
            self.osmosdr_sink_0.set_sample_rate(10e6)
            self.osmosdr_sink_0.set_center_freq(self.frequency, 0)
            self.osmosdr_sink_0.set_freq_corr(0, 0)
            self.osmosdr_sink_0.set_gain(0, 0)
            self.osmosdr_sink_0.set_if_gain(0, 0)
            self.osmosdr_sink_0.set_bb_gain(0, 0)
            self.osmosdr_sink_0.set_antenna('', 0)
            self.osmosdr_sink_0.set_bandwidth(5000, 0)
        else:
            self.vector_sink_0 = blocks.vector_sink_c(1,10000)
        if numSamples != None:
            self.head_0 = blocks.head(gr.sizeof_gr_complex,numSamples)

        self.blocks_multiply_xx_1 = blocks.multiply_vcc(1)
        self.analog_sig_source_x_2 = analog.sig_source_c(10e6, analog.GR_COS_WAVE, self.frequency, 1, 0)
        self.analog_sig_source_x_1 = analog.sig_source_c(10e6, analog.GR_COS_WAVE, 10000, 1, 0)
        ### end transmitter blocks ###

        ### transmitter connections ###
        self.connect((self.analog_sig_source_x_1, 0), (self.blocks_multiply_xx_1, 0))    
        self.connect((self.analog_sig_source_x_2, 0), (self.blocks_multiply_xx_1, 1))    
        if not simulate:
            self.connect((self.blocks_multiply_xx_1, 0), (self.osmosdr_sink_0, 0))
        else:
            self.connect((self.blocks_multiply_xx_1, 0), (self.head_0, 0))
            self.connect((self.head_0, 0), (self.vector_sink_0, 0))
        ### end transmitter connections ###
        print("finished setup_transmitter")


    def set_tx_gain(self, tx_rf_gain, tx_if_gain):
        # make sure provided gain values are within acceptable range
        # tx_rf_gain is 0 or 14 dB (no steps available)
        # tx_if_gain is 0 to 47 dB in 1 dB steps
        if tx_rf_gain == 0 or tx_rf_gain == 14:
            self.tx_rf_gain = int(tx_rf_gain)
        else:
            print("WARNING: tx_rf_gain can only be 0 or 14, setting to 0.")
            tx_rf_gain = 0
        if tx_if_gain >= 0 or tx_rf_gain <= 47:
            self.tx_if_gain = int(tx_if_gain)
        else:
            print("WARNING: tx_if_gain must be between 0 and 47, setting to 0.")
            tx_if_gain = 0
        return True
