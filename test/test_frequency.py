from pydasp import Frequency

def test_pitch_case():
    for note_name in ['C', 'D', 'E', 'F', 'G', 'A', 'B']:
        lower = Frequency(f'{note_name.lower()}0')
        assert Frequency(f'{note_name}0').hertz == lower.hertz

def test_zeroth_8ve_pitch():
    for p in Frequency.pitch_classes:
        freq = Frequency(f'{p}0')
        freq == Frequency.pitch_classes[p]

def test_a():
    for i, a in enumerate([27.5, 55, 110, 220, 440]):
        Frequency(f'a{i + 1}').hertz == a


