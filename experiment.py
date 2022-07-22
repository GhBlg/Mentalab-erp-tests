import argparse
from psychopy import visual, core, event
import random
from explorepy import Explore
from playsound import playsound
import socket


def main():
    parser = argparse.ArgumentParser(description="A script to run an audio Experiment")
    parser.add_argument("-n", "--name", dest="name", type=str, help="Name of the device.")
    parser.add_argument("-f", "--filename", dest="filename", type=str, help="Record file name")
    args = parser.parse_args()
        
    path  = 'C:\\Users\\Client\\Desktop\\Tom\\edf tests\\'

    n_blocks = 5   # Number of blocks
    n_trials_per_block = 5   # Number of trials (targets) in each block
    isi = 1   # Inter-stimulus interval
    stim_dur = 1.2     # Stimulus duration
    labels = [random.randint(1, 2) for i in range(n_trials_per_block)] # Stimulus onset labels: 10 -> nontarget and 11 -> target

    # Connect to Explore and record data
    explore = Explore()
    explore.connect(device_name=args.name)
    explore.record_data(file_name=args.filename, file_type='csv', do_overwrite=False)

    # Main window
    win = visual.Window(size=(600, 800), fullscr=True, screen=0, color=[0.1, 0.1, 0.1])

    # Block start instruction
    wait_text_stim = visual.TextStim(win=win, text="Press S to start", color=(-1, -1, -1), height=.1, bold=True)
    
    # Block start instruction
    focus_txt = visual.TextStim(win=win, text="Try to detect the difference in pitches", color=(-1, -1, -1), height=.1, bold=True)

    def listen_session(sound_labels):
        for label in sound_labels:
            explore.set_marker(label)
            clock = core.Clock()        
            playsound(path+str(label)+'.wav')
            core.wait(isi)
        

    for b in range(n_blocks):
        wait_text_stim.draw()
        win.flip()
        event.waitKeys(keyList=['s'])
        explore.set_marker(8)
        focus_txt.draw()
        win.flip()
        core.wait(1)
        listen_session(labels)
        random.shuffle(labels)

    explore.stop_recording()
    explore.disconnect()   

    del wait_text_stim, focus_txt


if __name__ == '__main__':
    main()
