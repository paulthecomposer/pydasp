"""
Module to represent an adsr audio envelope.

Classes:

    Envelope
"""

import numpy as np

SPS = 44100


class Envelope:
    """
    A class to represent an adsr envelope.

    ...

    Attributes
    ----------
    attack : float
        attack time in seconds
    decay : float
        decay time in seconds
    sustain : float
        sustain time in seconds
    release : float
        release time in seconds
    peak_amp : float
        amplitude for peak of attack
    sus_amp : float
        amplitude for sustain

    Methods
    -------
    make():
        Create a numpy array of all samples required for the envelope.
    """

    def __init__(self, adsr):
        self.attack = adsr[0]
        self.decay = adsr[1]
        self.sustain = adsr[2]
        self.release = adsr[3]
        self.peak_amp = adsr[4]
        self.sus_amp = adsr[5]

    @property
    def duration(self):
        """Get duration of envelope in seconds"""
        return sum((self.attack, self.decay, self.sustain, self.release))

    @property
    def adsr(self):
        """Get or set envelope values as tuple"""
        return (self.attack, self.decay, self.sustain, self.release,
                self.peak_amp, self.sus_amp)

    @adsr.setter
    def adsr(self, adsr):
        (self.attack, self.decay, self.sustain, self.release,
            self.peak_amp, self.sus_amp) = adsr

    def make(self):
        """
        Create a 1D array containing the amplitude of each sample of evelope.

        Parameters
        ----------
        None

        Returns
        -------
        1D array
        """

        return np.concatenate(

            (  # Amplitude for each sample during attack
                np.linspace(0, self.peak_amp, int(self.attack * SPS)),

                # Amplitude for each sample during decay
                np.linspace(self.peak_amp, self.sus_amp,
                            int(self.decay * SPS)),

                # Amplitude for each sample suring sustain
                np.full(int(self.sustain * SPS), self.sus_amp),

                # Amplitude for each smaple during release
                np.linspace(self.sus_amp, 0, int(self.release * SPS))
            ))
