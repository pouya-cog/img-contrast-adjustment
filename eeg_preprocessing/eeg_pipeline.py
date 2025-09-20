"""
EEG Preprocessing Pipeline (Demo with MNE sample dataset)

Author: Pouya Mokari
Part of MSc Thesis Project - Trypophobia Perception
"""

import mne

# --------------------------------------------------
# 1. Load demo EEG dataset from MNE
# --------------------------------------------------
print("Loading sample EEG dataset...")
data_path = mne.datasets.sample.data_path()
raw_file = data_path + "/MEG/sample/sample_audvis_raw.fif"
raw = mne.io.read_raw_fif(raw_file, preload=True)

# --------------------------------------------------
# 2. Preprocessing
# --------------------------------------------------
# Filter: 1–40 Hz band-pass
raw.filter(1., 40., fir_design='firwin')

# Set EEG average reference
raw.set_eeg_reference('average', projection=True)

# --------------------------------------------------
# 3. Events & Epoching
# --------------------------------------------------
# Load events from the dataset
events = mne.find_events(raw, stim_channel='STI 014')

# Define event IDs (this demo has auditory/visual events)
event_id = {'auditory/left': 1, 'auditory/right': 2,
            'visual/left': 3, 'visual/right': 4}

# Create epochs: -0.2s to 0.5s around each event
epochs = mne.Epochs(raw, events, event_id, tmin=-0.2, tmax=0.5,
                    baseline=(None, 0), preload=True)

# --------------------------------------------------
# 4. Compute and plot ERPs
# --------------------------------------------------
evoked = epochs['auditory/left'].average()
evoked.plot()

print("EEG preprocessing demo finished successfully!")