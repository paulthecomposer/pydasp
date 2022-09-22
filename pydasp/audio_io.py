"""
Module containing stand-alone functions for processing digital audio signals.

Functions:

    equalise_len(arrays)
    mix(*signals)
    signal_from_wav(wav_file)
"""

from scipy.io.wavfile import read
import numpy as np


def equalise_len(arrays):
    """
    Equalise length of n signals by appending silence to shorter signals.

    Parameters
    ----------
    arrays : 1D arrays
        Audio signals.

    Returns
    -------
    List of 1D arrays
    """

    # Greatest duration in arrays
    longest = len(max(arrays, key=len))
    return [

        # Concatenate the signal with silence
        np.concatenate((array, np.zeros(longest - len(array))))

        # If shorter than longest array
        if len(array) < longest else array for array in arrays
    ]


def mix(signals):
    """
    Mix signals into a single audio signal.

    Parameters
    ----------
    *signals : 1D arrays
        Audio signals to be mixed.

    Returns
    -------
    1D arrays
    """

    signals = tuple(s.signal if hasattr(s, 'signal') else s for s in signals)

    # Combine signals
    mix = sum(equalise_len(signals))
    return mix / mix.max()


def signal_from_wav(wav_file):
    """
    Get audio signal from WAV file.

    Parameters
    ----------
    wav_file : str
        .WAV file.

    Returns
    -------
    str ('BINARY' or 'MONO'), 1D array, 1D array (if 'STERIO')
    """

    signal = read(wav_file)[1] / 10000

    # If sterio
    if np.ndim(signal) == 2:

        # Get sub-arrays for channels 1 and 2
        channel_0, channel_1 = np.split(
            signal, 2, 1)[0], np.split(signal, 2, 1)[1]

        # flatten and return sub-arrays
        return 'STERIO', np.ndarray.flatten(
            channel_0), np.ndarray.flatten(channel_1)
    return 'MONO', signal
