import argparse
from psychopy import visual, core, event
import random
import numpy
from playsound import playsound
from pylsl import StreamInfo, StreamOutlet, IRREGULAR_RATE, cf_double64
#import uuid 

def main():
        
    path  = 'C:\\Users\\Client\\Desktop\\Tom\\edf tests\\'

    n_blocks = 2   # Number of blocks
    n_trials_per_block = 100   # Number of trials (targets) in each block
    isi = 2   # Inter-stimulus interval
    stim_dur = 1.2     # Stimulus duration

    #Generate random numbers (1 or 2) with a given probability (20% and 80%)
    labels = [numpy.random.choice(numpy.arange(1, 3), p=[0.2, 0.8]) for i in range(n_trials_per_block)] # Stimulus 
    
    # generate stream UID
    UID ='myuidw43536' #str(uuid.uuid4())
    # Connect to Explore and record data
    info = StreamInfo(
        name="TRIG",  # name of the stream
        type="Markers",  # stream type
        channel_count=1,  # number of values to stream
        nominal_srate=IRREGULAR_RATE,  # sampling rate in Hz or IRREGULAR_RATE
        channel_format=cf_double64,  # data type sent (dobule, float, int, str)
        source_id=UID,  # unique identifier
    )
    # next make an outlet
    outlet = StreamOutlet(info)

    # Main window
    win = visual.Window(size=(600, 800), fullscr=True, screen=0, color=[0.1, 0.1, 0.1])

    #  start Lab Recorder instruction
    wait_text_stim = visual.TextStim(win=win, text="Please start and setup LAB RECORDER/ Press S to start", color=(-1, -1, -1), height=.1, bold=True)
    
    # Block start instruction
    focus_txt = visual.TextStim(win=win, text="Try to detect the difference in pitches", color=(-1, -1, -1), height=.1, bold=True)

    def listen_session(sound_labels):
        for label in sound_labels:
            outlet.push_sample([label])   
            playsound(path+str(label)+'.wav')
            core.wait(isi)
        

    for b in range(n_blocks):
        wait_text_stim.draw()
        win.flip()
        event.waitKeys(keyList=['s'])
        focus_txt.draw()
        win.flip()
        core.wait(1)
        listen_session(labels)
        random.shuffle(labels)


    del wait_text_stim, focus_txt


if __name__ == '__main__':
    main()
