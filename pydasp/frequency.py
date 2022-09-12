"""
Module to represent frequency values in Hz

Classes:
    Frequency
"""

from itertools import count


class Frequency:
    """
    A class to represent a frequency value in Hz

    ...

    Attributes
    ----------
    hertz : int, float or str
        frequency in hertz

    Methods
    -------
    convert_from_pitch(pitch):
        Convert a string to a frequency in Hz.
    transpose_by_interval(n_intervals=1, interval_class=1, octave_div=12)
        Transpose a frequency by specified amount.
    spectrum(n_harmonics, multiplier=1)
        Calculate a frequency spectrum.
    nth_harmonic(self, nth, multiplier=1)
        Calculate nth harmonic of a frequency spectrum.

    """
    
    # Dictionary stores frequencies of white notes in 0th 8ve
    pitch_classes = {
        'c': 16.55, 'd': 18.34, 'e': 20.6, 'f': 21.83,
        'g': 24.5, 'a': 27.5, 'b': 30.87
        }   

    def __init__(self, hertz):

        self.hertz = hertz

    @property
    def hertz(self):
        """Get or set frequency value in hertz"""
        return self._hertz

    @hertz.setter
    def hertz(self, hertz):
        if isinstance(hertz, (float, int)):
            self._hertz = hertz
        else:
            self.convert_from_pitch(hertz)

    def convert_from_pitch(self, pitch):
        """
        Convert a string to a frequency in hz and store it in self.hz.

        Parameters
        ----------
        pitch : str
            Note name(A - G), optionally a # or b (representing a sharp or flat),
            numeric octave value. For, example 'A#4'.

        Returns
        -------
        none
        """

        # Validate length of pitch str
        if (len(pitch) < 2 or len(pitch) > 3):
            raise ValueError('Invalid pitch: Length of 2 or 3 is permitted')

        # Validate pitch
        if pitch[0].lower() not in self.pitch_classes:
            raise ValueError('Invalid pitch: Letters A - G are permitted')

        # Validate accidental
        if (len(pitch) == 3 and pitch[1] != '#' and pitch[1] != 'b'):
            raise ValueError('Invalid pitch: Accidentals # and b are permitted')

        # Validate octave and convert to int
        try:
            n_octaves = int(pitch[-1])
        except Exception as exc:
            raise ValueError ('Invalid pitch: Octave value 0 - 9 permitted') from exc

        # Set hz to frequency of 0th octave
        self.hertz = self.pitch_classes[pitch[0].lower()]

        # Cast 8ve value to int
        n_octaves = int(pitch[-1])

        # Transpose by n octaves
        self.transpose_by_interval(n_octaves, 12)

        # Raise by a semitone if #, lower by a semitone of b
        if pitch[1] == '#':
            self.transpose_by_interval(1)
        elif pitch[1] == 'b':
            self.transpose_by_interval(-1)

    def transpose_by_interval(self, n_intervals=1, interval_class=1, octave_div=12):
        """
        Transpose by n * interval class. By default, transpose by 1 semitione.

        Parameters
        ----------
        n_intervals : int, optional (default is 1)
            Number of intervals to transpose by.
        interval_class: int, optional (default is 1)
            Interval type, meausred by increments of octave division.
        octave_div : int, optional (default is 12)
            Number of equal octave divisions.

        Returns
        -------
        none
        """

        # Each interval = freq multiplied by 2 to the power of the octave division
        transpose_by = n_intervals * interval_class
        self.hertz *= round(((2 ** (1 / octave_div)) ** (transpose_by)), 2)


    def spectrum(self, n_harmonics, multiplier=1):
        """
        Calculate a frequency spectrum for object

        Parameters
        ----------
        n_harmonicss : int
            Number of harmonics in spectrum.
        multiplier : float, optional
            Multiplier for fundamental frequency (default is 1).

        Returns
        -------
        list
            A list of harmonic frequencies in Hz
        """

        harmonic = count(self.hertz, (self.hertz * multiplier))
        return [next(harmonic) for i in range(n_harmonics)]


    def nth_harmonic(self, nth, multiplier=1):
        """
        Calculate the nth harmonic of a frequency spectrum,
        where the fundamental frequency is self.hz.

        Parameters
        ----------
        nth : int
            nth harmonic in spectrum.
        multiplier : float, optional
            Multiplier for fundamental frequency (default is 1).

        Returns
        -------
        float
            Frequency in Hz of nth harmonic

        """

        return Frequency.spectrum(self.hertz, nth, multiplier)[-1]
