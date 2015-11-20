from music_theory import *
from rhythm import gen_rhythm

import random
import itertools  # Used for cartesian product in Chord.get_random_voicing()

CHORD_TYPES = [1, 0, 0, 1, 1, 0]  # 1 for major, 0 for minor...Gives type for chords on steps 1 => 6
ROMAN_NUMERALS = ["I", "ii", "iii", "IV", "V", "vi"]

"""
Markov chain definition of how chord progressions can be built.
0 is the begin state (i.e. chord progressions start with I, IV, or vi chord.
"""
CHORD_PROGRESSION_RULES = {
    0: [1, 4, 6],
    1: [2, 3, 4, 5, 6],
    2: [4, 5],
    3: [4, 5, 6],
    4: [1, 5, 6],
    5: [1, 4, 6],
    6: [1, 2, 3, 4, 5]
}


class Chord:
    """
    Class for chords that are typically stored in a progression (list). Must have a key for context.

    step        1-index int (1-6, for now), scale value
    chordType   str, "maj" "min" etc.
    """
    step = -1
    chord_type = ""
    key = None

    def __init__(self, step, chord_type, key):
        """
        :param step: int (step in scale of key signature)
        :param chord_type: str
        :param key:
        :return: Chord (constructor)
        """
        self.step = step
        self.chord_type = chord_type
        self.key = key

    def __str__(self):
        """
        Really just being used for debugging currently... there's no specific reasoning to this output.
        :return: str
        """
        return self.key.scale[self.step - 1] + self.chord_type + " (" + self.get_roman_numeral() + ")"

    def get_roman_numeral(self):
        """
        :return: str of roman numeral, i.e. "IV" or "ii"
        """
        return ROMAN_NUMERALS[self.step - 1]

    def note_fits(self, pitch):
        """
        :param pitch: (MusicData.Pitch)
        :return: boolean telling whether the parameter pitch can reasonably be played over this chord
        """
        pitch_step = pitch.scale_step - 1
        triad = [(self.step - 1) % 7, (self.step - 1 + 2) % 7, (self.step - 1 + 4) % 7]
        allowed_pitches = triad + [x - 1 for x in MELODIC_ALLOWANCES[
            self.step]]  # list of steps on the key-signature scale that can be played over this chord.
        return pitch_step in allowed_pitches

    def get_pitch(self,step,octave):
        """
        Args:
            step (int): 1-7
            octave (int):
        :return:
        """
        pitch = self.key.get_pitch(self.step,octave)    # root pitch

        half_steps_to_root = scale_steps[self.step-1]
        half_steps_to_pitch = scale_steps[(self.step + step) % 7 -2]
        pitch.add_half_steps(half_steps_to_pitch-half_steps_to_root)
        return pitch


    def get_random_voicing(self, duration):
        """
        Creates a random "voicing" of a chord, either with 1 and 5, or 1, 3, and 5. The voicing will be in the bass clef.
        :param duration: (int) length of note.
        :return: list of Note objects
        """
        all_scale_tones = self.key.get_all_note_values_in_key()
        if (random.random() < 0.60):
            valid_steps = [self.step, (self.step - 1 + 2) % 7 + 1, (self.step - 1 + 4) % 7 + 1]
        else:
            valid_steps = [self.step, (self.step - 1 + 4) % 7 + 1]
        tones_in_bass_clef = [x for x in all_scale_tones if
                              Pitch(x, self.key).scale_step in valid_steps and 28 <= x <= 48]
        result = []
        for step in valid_steps:
            notes_on_step = [x for x in tones_in_bass_clef if Pitch(x, self.key).scale_step == step]
            result.append(notes_on_step)
        combos = list(itertools.product(*result))  # Get all combinations of 1, 3, and 5 (or possibly just 1 and 5)
        combos = [c for c in combos if
                  max(c) - min(c) < 15 and min(c) > 35]  # filter combos to voicings that aren't too tight/loose
        final_result = combos[random.randint(0, len(combos) - 1)]
        return [Note(Pitch(x, self.key), duration) for x in final_result]


def get_next_chord(current_chord):
    """
    :param current_chord: (Chord) current chord in progression, used to find the next
    :return: (int) step of next chord
    """
    possible_chords = CHORD_PROGRESSION_RULES[current_chord.step]
    return possible_chords[random.randint(0, len(possible_chords) - 1)]


def get_type(chord_step):
    """
    :param chord_step: (int) 1-index step of chord
    :return: (string) type of chord, given by CHORD_TYPES

    This method is a bit simplistic/pointless currently, but it will be expanded to include more advanced chord types and probabilities.
    """
    return "maj" if CHORD_TYPES[chord_step - 1] == 1 else "min"


def get_chord_progression(key, num_chords):
    result = [Chord(0, None, None)]
    while len(result) - 1 < num_chords:
        next_step = get_next_chord(result[-1])
        next_type = get_type(next_step)
        chord = Chord(next_step, next_type, key)
        result.append(chord)
    return result[1:]


def levenshtein_distance(a, b):
    """
    Calculates the Levenshtein distance between a and b.
    http://hetland.org/coding/python/levenshtein.py
    :param a: str
    :param b: str
    :return:  int
    """
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]


def different_enough(prog1, prog2):
    """
    I want to ensure that Chord progressions in different sections are very different from each other. This method uses levenshtein_distance to ensure that the two progressions are different enough.
    :param prog1: list of Chord objects
    :param prog2: list of Chord objects
    :return: boolean: True if the progressions are sufficiently different from one another.
    """
    prog1_str = ''.join([str(x.step) for x in prog1])
    prog2_str = ''.join([str(x.step) for x in prog2])
    distance = float(levenshtein_distance(prog1_str, prog2_str)) / len(prog1_str)
    return distance > 0.5 and prog1[0].step != prog2[0].step

chord_tuples = [
    (3,5),
    (3,1),
    (5,1)
]

def make_chord_measure(chord,measure_duration):
    '''
    :param chord:
    :param measure_duration:
    :return: list of Note (lists), to be played by the left hand of the piano player
    '''

    rhythm = gen_rhythm(1,measure_duration,notes=[1,2,3,4])
    first_pitch = chord.get_pitch(1,2)
    first_note = Note(first_pitch,rhythm[0])
    result = [[first_note]]
    for r in rhythm[1:]:
        steps = chord_tuples[random.randint(0,len(chord_tuples)-1)]

        dist1 = scale_steps[steps[0]-1]
        dist2 = scale_steps[steps[1]-1]
        if dist2 == 0:
            dist2 = 13

        # Assuming 2-tuple
        bottom_pitch = first_pitch.add_scale_steps(dist1)
        top_pitch = first_pitch.add_scale_steps(dist2)

        result.append([Note(bottom_pitch,r),Note(top_pitch,r)])
    return result
