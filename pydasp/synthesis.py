"""
Module for audio synthesis.

Classes:

    Signals
    AdditiveWaveform
    Sawtooth
    Square
    Triangular
    Modulator
    ButterworthFilter
"""

from abc import abstractmethod
import numpy as np
from scipy import signal as sp_signal
from pydasp.frequency import Frequency
from pydasp.adsr_envelope import Envelope
from pydasp.basic_signals import Signal, Rest, Noise, Sine
from pydasp.audio_io import equalise_len, mix

SPS = 44100


class Signals(Signal):
    """
    A class to combine audio signals.

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
        Trim n seconds from beginning and/or end of audio signal.
    split(self, *split_at_s):
        Split audio signal into shorter signals.
    equalise_length(arrays):
        Equalise length of n signals by appending silence to shorter signals.
    mix(*signals):
        Mix n signals into a singal audio signal.
    append(new_signal):
        Append audio signal with a new signal.
    mix_with(*signals):
        Mix n signals with audio signal.
    loop(n_times):
        Repeat signal n times.
    delay(delay_time, amp_reduction, echoes):
        Audio delay effect.
    strip_silence():
        Remove leading and trailing silence.
    modulate_frequency(modulator):
        Modulate frequency of audio signal.
    add(other):
        Return concatenated Signals object

    """

    def __init__(self, signal):
        self.signal = signal

    @property
    def signal(self):
        return self._signal

    @signal.setter
    def signal(self, signal):
        if (np.ndim(signal[1])) == 1:
            self._signal = np.concatenate(signal)
        else:
            self._signal = signal

    @property
    def duration(self):
        return len(self.signal) / SPS

    def append(self, new_signal):
        """
        Append audio signal with a new signal.

        Parameters
        ----------
        new_signal : 1D array
            Audio signal.

        Returns
        -------
        None
        """

        self.signal = np.concatenate((self.signal, new_signal))

    def mix_with(self, *signals):
        """
        Mix signals with audio signal.

        Parameters
        ----------
        *signals : 1D arrays
            Audio signals to be mixed with signal.

        Returns
        -------
        None
        """

        self.signal = mix((self.signal, *signals))

    def loop(self, n_times):
        """
        Repeat signal n times.

        Parameters
        ----------
        n_times : int
            Times to repeat signal.

        Returns
        -------
        None
        """

        self.signal = np.tile(self.signal, n_times)

    def delay(self, delay_time, amp_reduction, echoes):
        """
        Audio delay effect.

        Parameters
        ----------
        delay_time : float
            Delay time in seconds.
        amp_reduction : float
            Attenuation of each delay
        echoes : int
            Number of echoes

        Returns
        -------
        None
        """

        for i in range(echoes):
            if i == 0:
                delayed = self.signal

            else:

                # Create delayed signal
                delayed = Signals(
                    (Rest.new_signal(delay_time * i),
                        delayed * (1 - amp_reduction))
                ).signal

                # Combine voice with delayed signals
                self.mix_with(delayed)

    def strip_silence(self):
        """Remove leading and trailing silence"""

        self.signal = np.trim_zeros(self.signal)

    def modulate_frequency(self, modulator):
        """
        Modulate frequency of audio signal.

        Parameters
        ----------
        modulator : iD array
            To modulate audio signal.

        Returns
        -------
        None
        """

        self.signal = Modulator.freq_modulated(self.signal, modulator)

    def modulate_amplitude(self, modulator, sensitivity=1):
        """
        Modulate amplitude of audio signal.

        Parameters
        ----------
        modulator : iD array
            Modulate audio signal.

        Returns
        -------
        None
        """

        self.signal = Modulator.amp_modulated(
            self.signal, modulator, sensitivity)

    def __add__(self, other):
        """
        Return concatenated Signals object

        Parameters
        ----------
        other : obj
            signal or obj with signal to append.

        Returns
        -------
        Signals
        """

        if hasattr(other, 'signal'):
            return Signals((self.signal, other.signal))
        else:
            return Signals((self.signal, other))


class AdditiveWaveform(Signal):
    """
    An abstract class to represent an additive waveform.

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
    equalise_length(arrays):
        Equalise length of n signals by appending silence to shorter signals.
    mix(*signals):
        Mix n signals into a single audio signal.
    make_wave(freq, phase_shift=0, nth_phase_increment=0):
        Return a new sine audio signal with nth phase increment.
    new_signal(freq, env, n_harmonics):
        Class method to return a new audio signal.
    make_signal()
        Abstract method.

    """

    @property
    def freq(self):
        """Get and set frequency for wave"""
        return self._freq

    @freq.setter
    def freq(self, freq):
        if isinstance(freq, Frequency):
            self._freq = freq
        else:
            self._freq = Frequency(freq)

    @property
    def env(self):
        """Get and set envelope for wave"""
        return self._env

    @env.setter
    def env(self, env):
        self._env = Envelope(env)

    @property
    def signal(self):
        """Return audio signal for wave"""
        return self._make_signal()

    def _make_wave(
            self, freq, phase_shift=0, nth_phase_increment=0):

        # calculate phase for nth increment
        phase = phase_shift * nth_phase_increment

        # Return phase between 0 and 360
        phase -= (360 * (phase // 360))

        return Sine.new_signal(freq, self.env.adsr, phase)

    @classmethod
    def new_signal(cls, freq, env, n_harmonics):
        """
        Class method to return a new audio signal.

        Parameters
        ----------
        freq : int, float ot str
            Frequency in hertz or pitch (Note name(A - G), optionally a # or b
            (sharp or flat), numeric octave value. For, example 'A#4').
        env : tuple
            Values for envelope a, d, s, r, peak amp, sus amp.
        n_harmonics : int
            Number of harmonics in wave.

        Returns
        -------
        1D array
        """
        return cls(freq, env, n_harmonics).signal

    @abstractmethod
    def _make_signal(self):
        pass


class Sawtooth(AdditiveWaveform):
    """
    An abstract class to represent a sawtooth waveform.

    ...

    Attributes
    ----------
    freq : int, float ot str
        Frequency in hertz or pitch (Note name(A - G), optionally a # or b
        (sharp or flat), numeric octave value. For, example 'A#4').
    env : tuple
        Values for envelope a, d, s, r, peak amp, sus amp.
    n_harmonics : int
        Number of harmonics in wave.


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
    equalise_length(arrays):
        Equalise length of n signals by appending silence to shorter signals.
    mix(*signals):
        Mix n signals into a single audio signal.
    make_wave(freq, phase_shift=0, nth_phase_increment=0):
        Return a new sine audio signal with nth phase increment.
    new_signal(freq, env, n_harmonics):
        Class method to return a new sawtooth audio signal.

    """

    def __init__(self, freq, env, n_harmonics):
        self.freq = freq
        self.env = env
        self.n_harmonics = n_harmonics

    def _make_signal(self):

        # Calculate required sine frequencies (n odd harmonics)
        harmonics = self.freq.spectrum(self.n_harmonics, multiplier=1)

        # Combine sine waves to make required wave type
        return mix([self._make_wave(harmonic) * 1 / (i + 1)
                    for i, harmonic in enumerate(harmonics)])


class Square(AdditiveWaveform):
    """
    An abstract class to represent a square waveform.

    ...

    Attributes
    ----------
    freq : int, float ot str
        Frequency in hertz or pitch (Note name(A - G), optionally a # or b
        (sharp or flat), numeric octave value. For, example 'A#4').
    env : tuple
        Values for envelope a, d, s, r, peak amp, sus amp.
    n_harmonics : int
        Number of harmonics in wave.


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
    equalise_length(arrays):
        Equalise length of n signals by appending silence to shorter signals.
    mix(*signals):
        Mix n signals into a single audio signal.
    make_wave(freq, phase_shift=0, nth_phase_increment=0):
        Return a new sine audio signal with nth phase increment.
    new_signal(freq, env, n_harmonics):
        Class method to return a new square audio signal.

    """

    def __init__(self, freq, env, n_harmonics):
        self.freq = freq
        self.env = env
        self.n_harmonics = n_harmonics

    def _make_signal(self):

        # Calculate required sine frequencies (n odd harmonics)
        harmonics = self.freq.spectrum(self.n_harmonics, multiplier=2)

        # Combine sine waves to make required wave type
        return mix([self._make_wave(harmonic) * 1 / (i * 2 + 1)
                    for i, harmonic in enumerate(harmonics)])


class Triangular(AdditiveWaveform):
    """
    An abstract class to represent an additive waveform.

    ...

    Attributes
    ----------
    freq : int, float ot str
        Frequency in hertz or pitch (Note name(A - G), optionally a # or b
        (sharp or flat), numeric octave value. For, example 'A#4').
    env : tuple
        Values for envelope a, d, s, r, peak amp, sus amp.
    n_harmonics : int
        Number of harmonics in wave.


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
    equalise_length(arrays):
        Equalise length of n signals by appending silence to shorter signals.
    mix(*signals):
        Mix n signals into a single audio signal.
    make_wave(freq, phase_shift=0, nth_phase_increment=0):
        Return a new sine audio signal with nth phase increment.
    new_signal(freq, env, n_harmonics):
        Class method to return a new triangualar audio signal.

    """

    def __init__(self, freq, env, n_harmonics):
        self.freq = freq
        self.env = env
        self.n_harmonics = n_harmonics

    def _make_signal(self):

        def harmonic_amplitude(harmonic):

            # Calculate mode number (relative frequency to the fundamental)
            mode_number = harmonic / self.freq.hertz
            return 1 / (mode_number ** 2)

        # Calculate required sine frequencies (n odd harmonics)
        harmonics = self.freq.spectrum(self.n_harmonics, multiplier=2)

        # Combine sines, change the phase of every other harmonic by 180°
        return mix(
            [self._make_wave(harmonic, 180, i) * harmonic_amplitude(harmonic)
                for i, harmonic in enumerate(harmonics)]
            )


class Modulator(Signal):
    """
    A class audio signal modulation.

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
    equalise_length(arrays):
        Equalise length of n signals by appending silence to shorter signals.
    mix(*signals):
        Mix n signals into a single audio signal.
    modulate_amplitude(modulator, sensitivity=1):
        Modulate audio signal's amplitude with modulator signal.
    modulate_frequency(modulator):
        Modulate audio signal's frequency with modulator signal.

    """

    def __init__(self, signal):
        self.signal = signal

    @property
    def signal(self):
        return self._signal

    @signal.setter
    def signal(self, signal):
        self._signal = signal

    def modulate_amplitude(self, modulator, sensitivity=1):
        """
         Modulate audio signal's amplitude with modulator signal.

        Parameters
        ----------
        modulator : 1D array
            To modulate audio signal.
        sensitivity : float
            Amplitude sensitivity of the modulator (the constant Ka).

        Returns
        -------
        none
        """

        (self.signal, modulator) = equalise_len((self.signal, modulator))
        self.signal *= (1.0 + sensitivity * modulator)

    def modulate_frequency(self, modulator):
        """
         Modulate audio signal's frequency with modulator signal.

        Parameters
        ----------
        modulator : 1D array
            To modulate audio signal.

        Returns
        -------
        none
        """

        (self.signal, modulator) = equalise_len((self.signal, modulator))
        self.signal *= np.cos(self.signal + modulator)

    @classmethod
    def amp_modulated(cls, carrier, modulator, sensitivity=1):
        """
         Class method to return amplitude modulated signal.

        Parameters
        ----------
        carrier : iD array
            To be modulated
        modulator : 1D array
            To modulate carrier.
        sensitivity : float
            Amplitude sensitivity of the modulator (the constant Ka).

        Returns
        -------
        1D array
        """
        modulated = cls(carrier)
        modulated.modulate_amplitude(modulator, sensitivity)
        return modulated.signal

    @classmethod
    def freq_modulated(cls, carrier, modulator):
        """
         Class method to return frequency modulated signal.

        Parameters
        ----------
        carrier : iD array
            To be modulated
        modulator : 1D array
            To modulate carrier.

        Returns
        -------
        1D array
        """

        modulated = cls(carrier)
        modulated.modulate_frequency(modulator)
        return modulated.signal


class ButterworthFilter(Signal):
    """
    Class to represent a Butterworth.

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
    equalise_length(arrays):
        Equalise length of n signals by appending silence to shorter signals.
    mix(*signals):
        Mix n signals into a single audio signal

    """

    def __init__(self, signal):
        self.signal = signal

    @property
    def signal(self):
        return self._signal

    @signal.setter
    def signal(self, signal):
        self._signal = signal

    def low_pass(self, cut_off_hz, nth_order):
        """
        Apply low-pass filter to signal.

        Parameters
        ----------
        cut_off_hz : int or float
            Cut-off frequency in hertz.
        nth_order : int
            Nth order roll-off

        Returns
        -------
        none
        """
        self._filter_signal(cut_off_hz, nth_order, 'lowpass')

    def high_pass(self, cut_off_hz, nth_order):
        """
        Apply high-pass filter to signal.

        Parameters
        ----------
        cut_off_hz : int or float
            Cut-off frequency in hertz.
        nth_order : int
            Nth order roll-off

        Returns
        -------
        none
        """
        self._filter_signal(cut_off_hz, nth_order, 'highpass')

    def band_pass(self, lowcut_hz, highcut_hz, nth_order):
        """
        Apply band-pass filter to signal.

        Parameters
        ----------
        lowcut_hz : int or float
            Low cut-off frequency in hertz.
        highcut_hz : int or float
            High cut-off frequency in hertz.
        nth_order : int
            Nth order roll-off

        Returns
        -------
        none
        """
        self._filter_signal((lowcut_hz, highcut_hz), nth_order, 'bandpass')

    def band_stop(self, lowcut_hz, highcut_hz, nth_order):
        """
        Apply band-cut filter to signal.

        Parameters
        ----------
        lowcut_hz : int or float
            Low cut-off frequency in hertz.
        highcut_hz : int or float
            High cut-off frequency in hertz.
        nth_order : int
            Nth order roll-off

        Returns
        -------
        none
        """
        self._filter_signal((lowcut_hz, highcut_hz), nth_order, 'bandstop')

    def _filter_signal(self, cut_off_hz, nth_order, filter_type):
        if isinstance(cut_off_hz, (int, float)):

            # cutoff value = fraction of Nyquist frequency(2 * Hz / SPS)
            cut_off_hz = 2 * cut_off_hz / SPS
        elif isinstance(cut_off_hz, (tuple)):
            cut_off_hz = tuple(2 * hz / SPS for hz in cut_off_hz)

        numerator, denominator = sp_signal.butter(
            nth_order, cut_off_hz, filter_type)
        self.signal = sp_signal.filtfilt(numerator, denominator, self.signal)
