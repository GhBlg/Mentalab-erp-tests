import argparse
import matplotlib.pyplot as plt
import pandas as pd
from scipy import signal
import numpy as np

CH_LABELS = ['F3', 'F7', 'T7', 'C3']


def extract_epochs(sig, sig_times, event_times, t_min, t_max, fs):
    """ Extracts epochs from signal
    Args:
        sig: EEG signal with the shape: (N_chan, N_sample)
        sig_times: Timestamp of the EEG samples with the shape (N_sample)
        event_times: Event marker times
        t_min: Starting time of the epoch relative to the event time
        t_max: End time of the epoch relative to the event time
        fs: Sampling rate
    Returns:
        (numpy ndarray): EEG epochs
    """
    offset_st = int(t_min * fs)
    offset_end = int(t_max * fs)
    epoch_list = []
    for i, event_t in enumerate(event_times):
        idx = np.argmax(sig_times > event_t)
        epoch_list.append(sig[:, idx + offset_st:idx + offset_end])
    return np.array(epoch_list)


def reject_bad_epochs(epochs, p2p_max):
    """Rejects bad epochs based on a peak-to-peak amplitude criteria
    Args:
        epochs: Epochs of EEG signal
        p2p_max: maximum peak-to-peak amplitude

    Returns:
        (numpy ndarray):EEG epochs
    """
    temp = epochs.reshape((epochs.shape[0], -1))
    res = epochs[np.ptp(temp, axis=1) < p2p_max, :, :]
    print(f"{temp.shape[0] - res.shape[0]} epochs out of {temp.shape[0]} epochs have been rejected.")
    return res


def custom_filter(exg, lf, hf, fs, type):
    """
    Args:
        exg: EEG signal with the shape: (N_chan, N_sample)
        lf: Low cutoff frequency
        hf: High cutoff frequency
        fs: Sampling rate
        type: Filter type, 'bandstop' or 'bandpass'
    Returns:
        (numpy ndarray): Filtered signal (N_chan, N_sample)
    """
    N = 4
    b, a = signal.butter(N, [lf / fs, hf / fs], type)
    return signal.filtfilt(b, a, exg)


def main():
    parser = argparse.ArgumentParser(description="P300 analysis script")
    parser.add_argument("-f", "--filename", dest="filename", type=str, help="Recorded file name")
    args = parser.parse_args()
    fs = 250
    lf = .5
    hf = 40

    label_1 = 1 #C2
    label_2 = 2 #C4

    t_min = -.3
    t_max = 1.
    p2p_max = 500000  # rejection criteria, units in uV

    exg_filename = args.filename + '_ExG.csv'
    marker_filename = args.filename + '_Marker.csv'

    # Import data
    exg = pd.read_csv(exg_filename)
    markers = pd.read_csv(marker_filename)

    ts_sig = exg['TimeStamp'].to_numpy()
    ts_markers_label_1 = markers[markers.Code.isin(['sw_'+str(label_1)])]['TimeStamp'].to_numpy()
    ts_markers_label_2 = markers[markers.Code.isin(['sw_'+str(label_2)])]['TimeStamp'].to_numpy()
    sig = exg[['ch'+str(i) for i in range(1, 5)]].to_numpy().T
    sig -= (sig[0, :]/2)
    filt_sig = custom_filter(sig, 45, 55, fs, 'bandstop')
    filt_sig = custom_filter(filt_sig, lf, hf, fs, 'bandpass')

    label_1_epochs = extract_epochs(filt_sig, ts_sig, ts_markers_label_1, t_min, t_max, fs)
    label_2_epochs = extract_epochs(filt_sig, ts_sig, ts_markers_label_2, t_min, t_max, fs)


    label_1_epochs = reject_bad_epochs(label_1_epochs, p2p_max)
    label_2_epochs = reject_bad_epochs(label_2_epochs, p2p_max)

    erp_label_1 = label_1_epochs.mean(axis=0)
    erp_label_2 = label_2_epochs.mean(axis=0)

    t = np.linspace(t_min, t_max, erp_label_1.shape[1])
    fig, axes = plt.subplots(nrows=2, ncols=2)
    fig.tight_layout()
    for i, ax in enumerate(axes.flatten()):
        ax.plot(t, erp_label_1[i, :], label='C2')
        ax.plot(t, erp_label_2[i, :], 'tab:orange', label='C4')
        ax.plot([0, 0], [-30, 30], linestyle='dotted', color='black')
        ax.set_ylabel('\u03BCV')
        ax.set_xlabel('Time (s)')
        ax.set_title(CH_LABELS[i])
        ax.set_ylim([-50, 50])
        ax.legend()
    plt.show()


if __name__ == '__main__':
    main()