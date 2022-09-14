# pydasp

By Paul Taylor

## Video Demo <URL HERE>

## Description

Pydasp is a Python package of tools to help musicians and programmers carry out a range of tasks related to audio digital signal processing. It was originally designed with composers in mind and therefore many of its features are especially applicable to sound synthesis and acousmatic composition.

Included within the pydasp package are five modules; their contents are sumarised as follows:

#### frequency

This module comprises a **Frequency** class, which can be initialised to represent an audio frequency in hertz. As an argument, a Frequency object can accept a numerical value or a string, defining a pitch as a note name ('A' - 'G'), optionally a sharp or flat ('#' or 'b') and an octave value ('0' - '9'); where 'C1', for example, represents the lowest C on a piano and 'C#1' represents a note one half-step higher. Its methods can be called to transpose a frequency, calculate a frequency spectrum or calculate the frequency of a specific harmonic within a frequency spectrum.

#### adsr_envelope

This module contains a class to represent an audio envelope (**Envelope**). Its attributes represent durations in seconds for attack, sustain, decay and release stages of a sound; and amplitudes for its peak and sustain levels.

#### basic_signals

When initialised, the classes within the basic_Signals module can synthesise audio signals containing white noise (**Noise**), a sine wave (**Sine**) or silence (**Rest**). All classes within this module inherit from the abstract base class, **Signal** and may call methods to play back audio through the computer's soundcard, write a .WAV file, trim a duration (specified in seconds) from the beginning or end of an audio signal, and split an audio signal into several shorter signals.

#### synthesis

Classes within the synthesis module can be used to generate more complex audio signals through additive and subtractive synthesis techniques. **Sawtooth**, **Square** and **Triangular** objects synthesise waveforms by combining sine waves; these are initialised by providing arguments to specify a frequency, adsr envelope values and a number of harmonics. The **Modulator** class can perform amplitude and frequency modulation when initialised with a carrier signal. The **Signals** class can be used to concatenate, append and mix audio signals. A delay effect can be achieved by calling its delay method. All classes in synthesis also inherit from the **Signal** class and can access its methods.

#### audio_io

Stand-alone functions are contained within the audio_io module. When provided with any number of audio signals, equalise_len equlaises their length by concatenating shorter signals with silence. The mix function mixes any number of audio signals into a single signal. Signal_from_wav, when provided with a .WAV file returns an array of samples for a mono file or sub-arrays of samples for channels 1 and 2, if sterio.