# -*- coding: utf-8 -*-
"""GIGA_Piano_Composer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oz9qdqAeOlzGYumIG8NPi_Et7nJc-O9b

# GIGA Piano Composer (ver. 1.0)

***

Powered by tegridy-tools: https://github.com/asigalov61/tegridy-tools

***

Credit for GPT2-RGA code used in this colab goes out @ Sashmark97 https://github.com/Sashmark97/midigen and @ Damon Gwinn https://github.com/gwinndr/MusicTransformer-Pytorch

***

WARNING: This complete implementation is a functioning model of the Artificial Intelligence. Please excercise great humility, care, and respect. https://www.nscai.gov/

***

#### Project Los Angeles

#### Tegridy Code 2022

***

# (Setup Environment)
"""

#@title nvidia-smi gpu check
!nvidia-smi

#@title Install all dependencies (run only once per session)

!git clone https://github.com/asigalov61/GIGA-Piano

!pip install torch

!pip install tqdm
!pip install matplotlib
!pip install torch-summary

!apt install fluidsynth #Pip does not work for some reason. Only apt works
!pip install midi2audio
!pip install pretty_midi

#@title Import all needed modules

print('Loading needed modules. Please wait...')
import os
import random
import copy

from collections import OrderedDict

from tqdm import tqdm

import matplotlib.pyplot as plt

from torchsummary import summary

print('Loading core modules...')
os.chdir('/content/GIGA-Piano')

import TMIDIX
from GPT2RGAX import *

print('Loading aux modules...')

from midi2audio import FluidSynth
import pretty_midi
import librosa.display
from IPython.display import Audio

os.chdir('/content/')

print('Done!')
print('Enjoy!!')

"""# (MODEL LOAD)"""

# Commented out IPython magic to ensure Python compatibility.
#@title Unzip Pre-Trained GIGA Piano Model
# %cd /content/GIGA-Piano/Model

print('=' * 70)
print('Unzipping pre-trained GIGA Piano model...Please wait...')

!cat /content/GIGA-Piano/Model/GIGA_Piano_Trained_Model.zip* > GIGA-Piano-Trained-Model.zip
print('=' * 70)

!unzip -j GIGA-Piano-Trained-Model.zip
print('=' * 70)

print('Done! Enjoy! :)')
print('=' * 70)
# %cd /content/

#@title Load/Reload the model

full_path_to_model_checkpoint = "/content/GIGA-Piano/Model/GIGA_Piano_Trained_Model_120000_steps_0.8075_loss.pth" #@param {type:"string"}

print('Loading the model...')
config = GPTConfig(128, 
                   1024,
                   dim_feedforward=1024,
                   n_layer=16, 
                   n_head=16, 
                   n_embd=1024,
                   enable_rpr=True,
                   er_len=1024)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = GPT(config)

state_dict = torch.load(full_path_to_model_checkpoint, map_location=device)

new_state_dict = OrderedDict()
for k, v in state_dict.items():
    name = k[7:] #remove 'module'
    new_state_dict[name] = v

model.load_state_dict(new_state_dict)

model.to(device)

model.eval()

print('Done!')

summary(model)

"""# (GENERATE)

# Load Custom MIDI / MIDI seed
"""

#@title Custom MIDI option
full_path_to_custom_MIDI = "/content/GIGA-Piano/GIGA-Piano-Seed-1.mid" #@param {type:"string"}
simulated_or_constant_velocity = False #@param {type:"boolean"}

print('Loading custom MIDI file...')

#print('Loading MIDI file...')
score = TMIDIX.midi2ms_score(open(full_path_to_custom_MIDI, 'rb').read())

events_matrix = []

itrack = 1

while itrack < len(score):
    for event in score[itrack]:         
        if event[0] == 'note' and event[3] != 9:
            events_matrix.append(event)
    itrack += 1

# Sorting...
events_matrix.sort(key=lambda x: x[4], reverse=True)
events_matrix.sort(key=lambda x: x[1])

# recalculating timings
for e in events_matrix:
    e[1] = int(e[1] / 16)
    e[2] = int(e[2] / 32)

# final processing...

melody = []
melody_chords = []

pe = events_matrix[0]
for e in events_matrix:

    time = max(0, min(126, e[1]-pe[1]))
    dur = max(1, min(126, e[2]))

    ptc = max(1, min(126, e[4]))

    melody_chords.append([time, dur, ptc])

    if time != 0:
      melody.append([time, dur, ptc])

    pe = e

inputs = []

for m in melody_chords:
  inputs.extend([127])
  inputs.extend(m)
  
inputs.extend([127])

print('Done!')

out1 = inputs

if len(out1) != 0:
    
    song = out1
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    son = []

    song1 = []

    for s in song:
      if s != 127:
        son.append(s)

      else:
        if len(son) == 3:
          song1.append(son)
        son = []

    song2 = []
    cho = []
    for s in song1:
      if s[0] == 0:
        cho.append(s)
      else:
        song2.append(cho)
        cho = []
        cho.append(s)
    
    for s in song2:
      if len(s) > 0:

        channel = 0

        if simulated_or_constant_velocity:
          if len(s) == 1:
            vel = s[0][2] + 10
          else:
            vel = s[0][2] + 30
        else:
          vel = 90
        
        for ss in s:

          time += ss[0] * 16
              
          dur = ss[1] * 32
          
          pitch = ss[2]
                                    
          song_f.append(['note', time, dur, channel, pitch, vel ])

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'GIGA Piano',  
                                                        output_file_name = '/content/GIGA-Piano-Music-Composition', 
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 0, 0, 0, 0, 0],
                                                        number_of_ticks_per_quarter=500)

    print('Done!')


print('Displaying resulting composition...')
fname = '/content/GIGA-Piano-Music-Composition'

pm = pretty_midi.PrettyMIDI(fname + '.mid')

# Retrieve piano roll of the MIDI file
piano_roll = pm.get_piano_roll()

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', fmin=1, hop_length=160, sr=16000, cmap=plt.cm.hot)
plt.title(fname)

FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
Audio(str(fname + '.wav'), rate=16000)

"""# GENERATE PRIME COMPOSITION BLOCK"""

#@title Single Continuation Block Generator

#@markdown NOTE: Play with the settings to get different results

custom_MIDI_or_improvisation = True #@param {type:"boolean"}
number_of_prime_tokens = 256 #@param {type:"slider", min:32, max:512, step:8}
temperature = 0.8 #@param {type:"slider", min:0.1, max:1, step:0.1}
number_of_batches = 2 #@param {type:"slider", min:1, max:8, step:1}
show_stats = True #@param {type:"boolean"}

#===================================================================
print('=' * 70)
print('GIGA Piano Music Model Continuation Generator')
print('=' * 70)

print('Generation settings:')
print('=' * 70)
print('Number of prime tokens:', number_of_prime_tokens)
print('Model temperature:', temperature)
print('Number of batches:', number_of_batches)
print('=' * 70)
print('Generating...')

if custom_MIDI_or_improvisation:
  inp = inputs[:number_of_prime_tokens+1]
else:
  inp = [127]

rand_seq = model.generate_batches(torch.Tensor(inp), 
                                          target_seq_length=1024,
                                          temperature=temperature,
                                          num_batches=number_of_batches,
                                          verbose=show_stats)
  
out1 = rand_seq[0].cpu().numpy().tolist()

print('Done!')

#@title Explore generated continuations
batch_number = 0 #@param {type:"slider", min:0, max:7, step:1}
simulated_or_constant_velocity = False #@param {type:"boolean"}

if batch_number >= number_of_batches:
  bn = 0
else:
  bn = batch_number

print('=' * 70)
print('Displaying batch #:',bn )
print('=' * 70)

out2 = []

out1 = rand_seq[bn].cpu().numpy().tolist()

final_composition = copy.deepcopy(out1)

if len(out1) != 0:
    
    song = out1
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    son = []

    song1 = []

    for s in song:
      if s != 127:
        son.append(s)

      else:
        if len(son) == 3:
          song1.append(son)
        son = []

    song2 = []
    cho = []
    for s in song1:
      if s[0] == 0:
        cho.append(s)
      else:
        song2.append(cho)
        cho = []
        cho.append(s)
    
    for s in song2:
      if len(s) > 0:

        channel = 0

        if simulated_or_constant_velocity:
          if len(s) == 1:
            vel = s[0][2] + 10
          else:
            vel = s[0][2] + 30
        else:
          vel = 90
        
        for ss in s:

          time += ss[0] * 16
              
          dur = ss[1] * 32
          
          pitch = ss[2]
                                    
          song_f.append(['note', time, dur, channel, pitch, vel ])

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'GIGA Piano',  
                                                        output_file_name = '/content/GIGA-Piano-Music-Composition', 
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 0, 0, 0, 0, 0],
                                                        number_of_ticks_per_quarter=500)

    print('Done!')


print('Displaying resulting composition...')
fname = '/content/GIGA-Piano-Music-Composition'

pm = pretty_midi.PrettyMIDI(fname + '.mid')

# Retrieve piano roll of the MIDI file
piano_roll = pm.get_piano_roll()

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', fmin=1, hop_length=160, sr=16000, cmap=plt.cm.hot)
plt.title(fname)

FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
Audio(str(fname + '.wav'), rate=16000)

"""# MAIN COMPOSITION LOOP

### RUN CELLS BELOW IN A LOOP
"""

#@title Single Continuation Block Generator

#@markdown NOTE: Play with the settings to get different results
regenerate_same_block_again = False #@param {type:"boolean"}
number_of_prime_tokens = 512 #@param {type:"slider", min:256, max:768, step:8}
temperature = 0.8 #@param {type:"slider", min:0.1, max:1, step:0.1}
number_of_batches = 2 #@param {type:"slider", min:1, max:8, step:1}
show_stats = True #@param {type:"boolean"}

#===================================================================
print('=' * 70)
print('GIGA Piano Music Model Continuation Generator')
print('=' * 70)

print('Generation settings:')
print('=' * 70)
print('Number of prime tokens:', number_of_prime_tokens)
print('Model temperature:', temperature)
print('Number of batches:', number_of_batches)
print('=' * 70)
print('Generating...')

if out2 == []:
  inp = copy.deepcopy(out1[-number_of_prime_tokens:])
else:
  inp = copy.deepcopy(out2[-number_of_prime_tokens:])

if regenerate_same_block_again:
  inp = copy.deepcopy(out2[:number_of_prime_tokens])

rand_seq = model.generate_batches(torch.Tensor(inp), 
                                          target_seq_length=1024,
                                          temperature=temperature,
                                          num_batches=number_of_batches,
                                          verbose=show_stats)

print('Done!')

#@title Explore generated continuations
batch_number = 1 #@param {type:"slider", min:0, max:7, step:1}
simulated_or_constant_velocity = False #@param {type:"boolean"}

if batch_number >= number_of_batches:
  bn = 0
else:
  bn = batch_number

print('=' * 70)
print('Displaying batch #:',bn )
print('=' * 70)

out2 = rand_seq[bn].cpu().numpy().tolist()

if len(out2) != 0:
    
    song = out2[number_of_prime_tokens:]
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    son = []

    song1 = []

    for s in song:
      if s != 127:
        son.append(s)

      else:
        if len(son) == 3:
          song1.append(son)
        son = []

    song2 = []
    cho = []
    for s in song1:
      if s[0] == 0:
        cho.append(s)
      else:
        song2.append(cho)
        cho = []
        cho.append(s)
    
    for s in song2:
      if len(s) > 0:

        channel = 0

        if simulated_or_constant_velocity:
          if len(s) == 1:
            vel = s[0][2] + 10
          else:
            vel = s[0][2] + 30
        else:
          vel = 90
        
        for ss in s:

          time += ss[0] * 16
              
          dur = ss[1] * 32
          
          pitch = ss[2]
                                    
          song_f.append(['note', time, dur, channel, pitch, vel ])

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'GIGA Piano',  
                                                        output_file_name = '/content/GIGA-Piano-Music-Composition', 
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 0, 0, 0, 0, 0],
                                                        number_of_ticks_per_quarter=500)

    print('Done!')


print('Displaying resulting composition...')
fname = '/content/GIGA-Piano-Music-Composition'

pm = pretty_midi.PrettyMIDI(fname + '.mid')

# Retrieve piano roll of the MIDI file
piano_roll = pm.get_piano_roll()

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', fmin=1, hop_length=160, sr=16000, cmap=plt.cm.hot)
plt.title(fname)

FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
Audio(str(fname + '.wav'), rate=16000)

"""# ADD/REMOVE LAST GENERATED BLOCK"""

#@title ADD BLOCK
final_composition = final_composition + out2[number_of_prime_tokens:]
print('Block added!')

#@title REMOVE BLOCK
final_composition = final_composition[:-number_of_prime_tokens]
print('Block removed!')

"""# PLAY/PLOT FINAL COMPOSITION"""

#@title Display final composition
if len(final_composition) != 0:
    
    song = final_composition
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    son = []

    song1 = []

    for s in song:
      if s != 127:
        son.append(s)

      else:
        if len(son) == 3:
          song1.append(son)
        son = []

    song2 = []
    cho = []
    for s in song1:
      if s[0] == 0:
        cho.append(s)
      else:
        song2.append(cho)
        cho = []
        cho.append(s)
    
    for s in song2:
      if len(s) > 0:

        channel = 0

        if simulated_or_constant_velocity:
          if len(s) == 1:
            vel = s[0][2] + 10
          else:
            vel = s[0][2] + 30
        else:
          vel = 90
        
        for ss in s:

          time += ss[0] * 16
              
          dur = ss[1] * 32
          
          pitch = ss[2]
                                    
          song_f.append(['note', time, dur, channel, pitch, vel ])

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'GIGA Piano',  
                                                        output_file_name = '/content/GIGA-Piano-Music-Composition', 
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 0, 0, 0, 0, 0],
                                                        number_of_ticks_per_quarter=500)

    print('Done!')


print('Displaying resulting composition...')
fname = '/content/GIGA-Piano-Music-Composition'

pm = pretty_midi.PrettyMIDI(fname + '.mid')

# Retrieve piano roll of the MIDI file
piano_roll = pm.get_piano_roll()

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', fmin=1, hop_length=160, sr=16000, cmap=plt.cm.hot)
plt.title(fname)

FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
Audio(str(fname + '.wav'), rate=16000)

"""# Congrats! You did it! :)"""