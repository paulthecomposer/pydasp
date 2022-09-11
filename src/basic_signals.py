"""
Module for synthesis of basic audio signals.

Classes:

    Signal
    Rest
    Noise
    Sine
"""

import time
from abc import ABC, abstractmethod
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from adsr_envelope import Envelope
from frequency import Frequency
from audio_io import equalise_len, mix


SPS = 44100

class Signal(ABC):
    """
    An abstract class to represent a digital audio signal.

    ...

    Attributes
    ----------

    Methods
    -------
    play(attenuation=0.3):
        Play audio signal.
    write_wave(file_name, channel_1=None, attenuation=0.3):
        Write audio signal to WAV file.
    trim(trim_to_s=0, trim_from_s=None):
        Trim n seconds from beginning and/or end of audio signal
    split(self, *split_at_s):
        Split audio signal into shorter signals.
    mix(*signals):
        Mix n signals into a single audio signal

    """

    @property
    @abstractmethod
    def signal(self):
        """Abstract method required to get or set signal"""

    @property
    def duration(self):
        """Get duration in seconds"""
        return len(self.signal) / SPS

    def play(self, attenuation=0.3):
        """
        Play audio signal.

        Parameters
        ----------
        attenuation : float
            Attenuate audio signal by value.

        Returns
        -------
        none
        """

        sd.play(self.signal * attenuation, SPS)
        time.sleep(len(self.signal) / SPS + 0.5)
        sd.stop()

    def write_wav(self, file_name, channel_1=None, attenuation=0.3):
        """
        Write audio signal to WAV file.

        Parameters
        ----------
        file_name : str
            Name of WAV file.
        channel_1 : 1D array, optional (default is None)
            Signal for 2nd audio channel.
        attenuation : float, optional (default is 0.3)
            Attenuate audio signal by value.

        Returns
        -------
        none
        """

        #Check whether a second audio channel was provided
        if np.any(channel_1):

            # Ensure channels are of equal length and make a 2D array
            # containing each channel's audio in its respective row
            sterio = np.vstack(equalise_len((self.signal, channel_1)))

            # Reshape the array to contain each channel's audio in its respective column.
            # Attenuate and convert to int16 data-type
            sound = np.int16((sterio.transpose() * attenuation) * 32767)

        else:

            # Attenuate and convert to int16 data-type
            sound = np.int16((self.signal * attenuation) * 32767)
        write(file_name, SPS, sound)

    def trim(self, trim_to_s=0, trim_from_s=None):
        """
        Trim n seconds from beginning and/or end of audio signal.

        Parameters
        ----------
        trim_to_s : float
            Trim from beginning to time-point (in seconds) in signal.
        trim_from_s : float
            Trim from time_point (in seconds)in signal to end.

        Returns
        -------
        1D array
        """
        if not trim_from_s:

            # Set trim_from_S to end of signal
            trim_from_s = self.duration

        trimmed_signal = self.signal
        if trim_to_s > 0:

            # Delete samples from beginning to trim_to_s
            trimmed_signal = np.delete(trimmed_signal, np.s_[0:int(trim_to_s * SPS)])

        # Delete samples from trim_from_s to end
        if trim_from_s < self.duration:
            trimmed_signal = np.delete(trimmed_signal,
            np.s_[int(trim_from_s * SPS):int(self.duration * SPS)])
        return trimmed_signal

    def split(self, *split_at_s):
        """
        Split audio signal into shorter signals.

        Parameters
        ----------
        *split_at_s : *floats
            Split signal at time-points (in seconds) in signal.

        Returns
        -------
        List of 1D arrays
        """

        # Split into a list of sub-arrays at required time-points
        return np.split(self.signal, [int(s * SPS) for s in split_at_s])


class Rest(Signal):
    """
    A class to represent a silent digital audio signal.

    ...

    Attributes
    ----------
    duration : float
        Duration of silence in seconds

    Methods
    -------
    play(attenuation=0.3):
        Play audio signal.
    write_wave(file_name, channel_1=None, attenuation=0.3):
        Write audio signal to WAV file.
    trim(trim_to_s=0, trim_from_s=None):
        Trim n seconds from beginning and/or end of audio signal
    split(self, *split_at_s):
        Split audio signal into shorter signals.
    new_signal(env):
        Class mothod to return a new silent audio signal

    """

    def __init__(self, duration):
        self.duration = duration

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, duration):
        if not isinstance(duration, (int, float)):
            raise TypeError('Invalid duration: Types int and float are permitted')
        if duration <= 0:
            raise ValueError('Invalid duration: Values greater than 0 are permitted')
        self._duration = duration

    @property
    def signal(self):
        return self._make_signal()

    @classmethod
    def new_signal(cls, duration):
        """
        Class method to return a new silent audio signal.

        Parameters
        ----------
        Duration : float
            Duration of silence in seconds.

        Returns
        -------
        1D array
        """

        return cls(duration).signal

    def _make_signal(self):

        # Make an all zero array of required duration
        return np.zeros(int(self.duration * SPS))


class Noise(Signal):
    """
    A class to represent a silent digital audio signal.

    ...

    Attributes
    ----------
    duration : float
        Duration of silence in seconds

    Methods
    -------
    play(attenuation=0.3):
        Play audio signal.
    write_wave(file_name, channel_1=None, attenuation=0.3):
        Write audio signal to WAV file.
    trim(trim_to_s=0, trim_from_s=None):
        Trim n seconds from beginning and/or end of audio signal
    split(self, *split_at_s):
        Split audio signal into shorter signals.
    new_signal(env):
        Class method to return a new silent audio signal.

    """

    def __init__(self, env):
        self.env = env

    @property
    def signal(self):
        return self._make_signal()

    @property
    def env(self):
        """Get and set envelope for audio signal"""
        return self._env

    @env.setter
    def env(self, env):
        self._env = Envelope(env)


    @classmethod
    def new_signal(cls, env):
        """
        Class method to return a new noise audio signal.

        Parameters
        ----------
        env : tuple
            Values for envelope a, d, s, r, peak amp, sus amp.

        Returns
        -------
        1D array
        """

        return cls(env).signal

    def _make_signal(self):

        # A numpy array with a uniform distribution of random values
        return np.random.uniform(
            -1, 1, int(self.env.duration * SPS)) * self.env.make()


class Sine(Signal):

    """
    A class to represent a silent digital audio signal.

    ...

    Attributes
    ----------
    freq : int, float ot str
        Frequency in hertz or pitch (Note name(A - G), optionally a # or b
        (representing a sharp or flat), numeric octave value. For, example 'A#4').
    env : tuple
        Values for envelope a, d, s, r, peak amp, sus amp.
    phase : int
        Phase off-set of sine (0 - 360)

    Methods
    -------
    play(attenuation=0.3):
        Play audio signal.
    write_wave(file_name, channel_1=None, attenuation=0.3):
        Write audio signal to WAV file.
    trim(trim_to_s=0, trim_from_s=None):
        Trim n seconds from beginning and/or end of audio signal
    split(self, *split_at_s):
        Split audio signal into shorter signals.
    new_signal(freq, env, phase=0):
        Class method to return a new sine audio signal.

    """

    def __init__(self, freq, env, phase=0):
        self.freq = freq
        self.env = env
        self.phase = phase

    @property
    def freq(self):
        """Get and set frequency for sinewave"""
        return self._freq

    @freq.setter
    def freq(self, freq):
        self._freq = Frequency(freq)

    @property
    def env(self):
        """Get and set envelope for sinewave"""
        return self._env

    @env.setter
    def env(self, env):
        self._env = Envelope(env)

    @property
    def phase(self):
        """Get, set and calculate phase for sinewave"""

        # Convert phase-offset to a fraction of 2 * pi
        return (self._phase / 360) * (2 * np.pi)

    @phase.setter
    def phase(self, phase):
        if phase > 359 or phase < 0:
            raise ValueError (
                'Invalid phase offset: Values between 0 and 359 permitted')
        self._phase = phase

    @property
    def each_sample(self):
        """Return an array containing indices for each sample of the signal"""
        return np.arange(len(self.env.make()))

    @property
    def signal(self):
        return self._make_signal()


    @classmethod
    def new_signal(cls, freq, env, phase=0):
        """
        Class method to return a new sine audio signal.

        Parameters
        ----------
        freq : int, float ot str
            Frequency in hertz or pitch (Note name(A - G), optionally a # or b
            (representing a sharp or flat), numeric octave value. For, example 'A#4').
        env : tuple
            Values for envelope a, d, s, r, peak amp, sus amp.
        phase : int
            Phase off-set of sine (0 - 360), optionl (default is 0)

        Returns
        -------
        1D array
        """
        return cls(freq, env, phase).signal

    def _make_signal(self):

        # Calculate each sample of sinewave with required frequency and adsr values
        return (np.sin(self.phase + 2 * np.pi * self.each_sample
        * self.freq.hertz / SPS)) * self.env.make()
        