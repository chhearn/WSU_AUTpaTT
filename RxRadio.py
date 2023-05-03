# RadioFlowGraphAMslow.py
# Handles gnuradio flowgraph blocks and connections

from gnuradio import analog
from gnuradio import blocks
from gnuradio import network
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.filter import window
import osmosdr

class RadioFlowGraph(gr.top_block):
    def __init__(self, radio_id, frequency, freq_offset=0, 
            numSamples=None, simulation=False):
        """ radio_id is hex string radio serial number like 61555f """
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
        self.tx_rf_gain = 0 # dB, 0 or 14 (no steps available)
        self.tx_if_gain = 3 # dB, 0 to 47 in 1 dB steps
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
        print("receiver radio_id {:s}".format(self.radio_id))
        ### receiver blocks ###
        src="numchan=1 hackrf=" + self.radio_id
        print("receiver {:s}".format(src))
        if not simulation:
            self.osmosdr_source_0 = osmosdr.source( args=src )
            self.osmosdr_source_0.set_sample_rate(10e6)
            self.osmosdr_source_0.set_center_freq(self.frequency, 0)
            self.osmosdr_source_0.set_freq_corr(0, 0)
            self.osmosdr_source_0.set_dc_offset_mode(0, 0)
            self.osmosdr_source_0.set_iq_balance_mode(0, 0)
            self.osmosdr_source_0.set_gain_mode(False, 0)
            self.osmosdr_source_0.set_gain(10, 0)
            self.osmosdr_source_0.set_if_gain(20, 0)
            self.osmosdr_source_0.set_bb_gain(20, 0)
            self.osmosdr_source_0.set_antenna('', 0)
            self.osmosdr_source_0.set_bandwidth(50000, 0)
        else:
            self.vector_source_0 = blocks.vector_source_c([])

        self.low_pass_filter_0 = filter.fir_filter_fff(100, firdes.low_pass(
           1, 10e6, 10000, 2000, window.WIN_HAMMING, 6.76))
        self.dc_blocker_xx_0 = filter.dc_blocker_ff(32, True)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(10e6, analog.GR_COS_WAVE, self.frequency, 1, 0, 0)
#----------------------------------------------------------------------------
        
        if numSamples != None:
            self.vector_sink_0 = blocks.vector_sink_f(1,numSamples)
            self.blocks_head_0 = blocks.head(gr.sizeof_float, numSamples)
        else:
            self.vector_sink_0 = blocks.vector_sink_f(1,1000)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(10e6, analog.GR_COS_WAVE, self.frequency, 1, 0)
        ### end receiver blocks ###
### receiver connections ###
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))    
        self.connect((self.blocks_complex_to_float_0, 0), (self.low_pass_filter_0, 0))    
        self.connect((self.dc_blocker_xx_0, 0), (self.vector_sink_0, 0))    
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_complex_to_float_0, 0))
        if numSamples != None:
            self.connect((self.dc_blocker_xx_0, 0), (self.blocks_head_0, 0))

        self.connect((self.low_pass_filter_0, 0), (self.dc_blocker_xx_0, 0))    
        if not simulation:
            self.connect((self.osmosdr_source_0, 0), (self.blocks_multiply_xx_0, 0))
        else:
            self.connect((self.vector_source_0, 0), (self.blocks_multiply_xx_0, 0))
### end receiver connections ###
        print("finished setup_receiver")
        return

#    def start(self):
        # we can't reuse the flowgraph without resetting the head block which
        # limits the number of samples captured and processed
        # head block only present on receiver
#        self.blocks_head_0.reset()
#        gr.top_block.start(self)


