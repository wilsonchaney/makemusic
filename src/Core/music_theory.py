import math  # For some weird expo/log operations in note duration (finding whether a note should have a dot

"""
The "absolute value" of a pitch is a zero-index integer that tells, essentially, how many half steps above C0 it is.

i.e.    C0 => 0
        Db0 => 1
        D0 => 2
        C1 => 12
        E1 => 16
        F#1 => 18
        Gb1 => 18
        C4 => 48 (middle C)

The "step" or "scale step" of a note is a 1-index integer, 1 through 7 inclusive, that tells where a pitch lies in a scale.

i.e. In the key of D...
        D => 1
        E => 2
        G => 4
        C# => 6
        Cn => ERROR
Notice that, as of now, accidentals will raise Exceptions. Currently, the composer ONLY works within a key signature and its valid notes.
"""

notes = ["C", ("C#", "Db"), "D", ("D#", "Eb"), "E", "F", ("F#", "Gb"), "G", ("G#", "Ab"), "A", ("A#", "Bb"), "B"]

white_keys = ["C","D","E","F","G","A","B"]

scale_steps = [0, 2, 4, 5, 7, 9, 11]
def get_scale_step(idx):
    """
    This is just a modulus-safe way to access the scale_steps array - turns out it simplifies LOTS of other code.
    """
    return scale_steps[idx % 7]

interval_names = ["SAME", "MIN_2ND", "MAJ_2ND", "MIN_3RD", "MAJ_3RD", "PER_4TH", "TRITONE", "PER_5TH", "MIN_6TH", "MAJ_6TH", "MIN_7TH", "MAJ_7TH"]

TREBLE_CLEF_RANGE = (45, 72)  # This goes from A3 (one ledger line below) to C6 (two ledger lines above)
BASS_CLEF_RANGE = (28, 48)  # This goes from E2 (one ledger line below) to C4 (one ledger line above)

"""
It's impossible to accurately describe this variable in its name only.
Input is 1-index chord step
Output is list of 1-index scale steps, OUTSIDE OF THE CHORD TRIAD, that are allowed in a melody/harmony over the chord.
"""
MELODIC_ALLOWANCES = {
    1: [2],
    2: [1],
    3: [1],
    4: [3],
    5: [1],
    6: [2, 5]
}

def get_sharp_notes():
    """
    Returns:
        list of str: All 12 enharmonic pitches using sharps (i.e. D# instead of Eb)
    """
    result = []
    for n in notes:
        if type(n) is str:
            result.append(n)
        else:
            result.append(n[0])
    return result


def get_flat_notes():
    """
    Returns:
        list(string): All 12 enharmonic pitches using flats (i.e. Eb instead of D#)
    """
    result = []
    for n in notes:
        if type(n) is str:
            result.append(n)
        else:
            result.append(n[1])
    return result


def get_note_index(note):
    """Get index of a note in global notes list, relative to C.

    Args:
        note (str): Note name - i.e. C, Eb, G#, etc.

    Returns:
        int: index of note, or -1 if note not found
    """
    if not validate_note_name(note):
        return -1
    for i, n in enumerate(notes):
        if type(n) is str:
            if (n == note):
                return i
        elif type(n) is tuple:
            if (n[0] == note):
                return i
            elif (n[1] == note):
                return i
    return (scale_steps[white_keys.index(note[0])] + (1 if note[1] == "#" else -1)) % 12


def validate_note_name(note):
    """Check whether a given note name is valid

    Used as a helped method to get_note_index

    Args:
        note (str): Note name, i.e. C, Eb, G# (ideally)

    Returns:
        bool: Is the note valid?
    """
    if type(note) != str:
        return False
    elif len(note) == 1:
        return note in white_keys
    elif len(note) == 2:
        return str(note[0]) in white_keys and (note[1] == '#' or note[1] == 'b')
    else:
        return False


class Pitch:
    """
    A pitch, with a key for context.

    The simplest form of representation is just an absolute value (int) - i.e. 0 for C0, 2 for D0, 12 for C1, etc.

    Fields:
        value (int)         Absolute index of the pitch (octave*12+step), beginning with C0
        octave (int)        Zero-index octave of the pitch
        key (KeySignature)  key that the pitch is in
        scale_step (int)    One-index int representing where the pitch is on the scale
        letter (str)        Note letter, i.e. "C", "Eb", etc.
    """

    value = None
    octave = None
    key = None
    scale_step = None
    letter = None

    def __init__(self, value, key):
        """
        Args:
            value (int): absolute value of pitch - see top of music_theory.py
            key (KeySignature): The key signature of this pitch, for context in the scale
        """
        self.value = value
        self.key = key
        self.set_up()

    def set_up(self):
        """Set up the fields for a pitch

        Used essentially as a helper function, but also to re-setup fields after adding half steps to a pitch.
        """
        self.octave = self.value / 12
        self.scale_step = Pitch.get_step_in_scale(self.value, self.key)
        self.letter = self.key.scale[self.scale_step - 1]
        if len(self.letter) == 2:
            if self.letter[1] == 'b':
                self.sharp_or_flat = -1
            elif self.letter[1] == '#':
                self.sharp_or_flat = 1
        else:
            self.sharp_or_flat = 0

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            condition = (self.value == other.value and self.key == other.key)
            return condition
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return str(self.letter)+str(self.octave)

    def add_half_steps(self,half_steps):
        """ Increments this pitch by the given number of half steps.

        Args:
            half_steps (int): Number of half steps to increment by
        """
        original_value = self.value
        original_key = self.key
        try:
            self.value += half_steps
            self.set_up()
        except ValueError:
            self.value = original_value
            self.key = original_key
            self.set_up()
            errorMsg = "Error - Adding " + str(half_steps) + " to " + self.letter + " in the key of " + self.key.root_note + " is not valid."
            raise ValueError(errorMsg)

    def get_interval(self, base_pitch):
        """Get interval between a lower pitch and this one.         ***Perhaps I should implement __le__ in-case self < base_pitch?***

        Args:
            base_pitch (Pitch): The lower pitch
                ** base_pitch must have the same key as self **
        Returns:
            0-index interval, with octaves "removed". i.e. C2 to E4 returns 4.
        """
        if self.value < base_pitch.value:
            raise ValueError("Param base_pitch must be lower than the pitch calling get_interval!")
        elif self.key != base_pitch.key:
            raise ValueError("Param base_pitch must share the same key with the pitch calling get_interval!")
        top_pitch = (self.value % 12) + 12
        bottom_pitch = base_pitch.value % 12
        interval = (top_pitch - bottom_pitch) % 12
        return interval

    @staticmethod
    def get_abs_value(note, octave):
        """
        Args:
            note (str): Note name, i.e. "C", "Db", etc.
            octave (int)

        Returns:
            (int): Absolute value of note, relative to C0
        """
        index = get_note_index(note)
        return 12 * octave + index

    @staticmethod
    def get_step_in_scale(value, key):
        """
        Args:
            value (int): Absolute value of a pitch
            key (KeySignature): The key signature of the pitch
        Returns:
            (int): 1-index step in scale of key - i.e. 3 for an E in the key of C, 1 for D in the key of D
        """
        note_val = value % 12
        relative_step = (note_val - key.value + 12) % 12  # + 12 needed => when/if key val is higher that note_val!!
        return scale_steps.index(relative_step) + 1

    def add_scale_steps(self,scale_steps):
        """ Returns a NEW pitch, with the given # of scale steps.

        Args:
            scale_steps (int): Number of scale steps to increment by
        """
        new_pitch = Pitch(self.value,self.key)
        while scale_steps > 0:
            # increment by that scale_step
            num_half_steps = (12+get_scale_step(new_pitch.scale_step)-get_scale_step(new_pitch.scale_step-1)) % 12
            new_pitch.value += num_half_steps
            scale_steps -= 1
            new_pitch.set_up()
        return new_pitch

class Note(object):
    """A musical note, made up of a pitch and a duration.

    Fields:
        pitch (Pitch)       The pitch of the note
        duration (int)      The duration of the note, in beats.
        type (str)          The type of the note, assuming quarter note is 1 beat. i.e. "eighth" - this doesn't address dotted notes, just the "base" type
        dot (bool)          Is this note a dotted note?
        tie (str)           Is this the beginning of a tie ("start"), the end of one ("stop"), or not tied (None)?
    """
    pitch = None
    duration = None
    type = None
    dot = None
    tie = None

    def __init__(self, pitch, duration,tie=None):
        """
        Args:
            pitch (Pitch)
            duration (int)
            tie (str)

        See Note documentation for argument details.
        """
        self.pitch = pitch
        self.duration = duration
        if duration < 0:
            print self.duration
            raw_input()
        self.type = Note.duration_names[2 ** (math.floor(math.log(duration, 2)))]
        if (math.log(float(duration) * 2 / 3, 2) % 1 == 0):
            self.dot = True
        else:
            self.dot = False
        self.tie = tie

    def __str__(self):
        result = str(self.pitch) + ", " + str(self.duration)
        if self.tie == "start":
            result = result+" /"
        elif self.tie == "stop":
            result = result+" \\"
        return result

    def split_into_tied_notes(self,first_duration):
        """Split into two tied notes with a total duration equal to self.duration - doesn't alter self.

        Args:
            first_duration (int): Portion of self that should become the first tied note
        Returns:
            (tuple of Note): The two notes
        """
        second_duration = self.duration-first_duration
        return (Note(self.pitch,first_duration,"start"),Note(self.pitch,second_duration,"stop"))

    duration_names = {
        0.25: "16th",
        0.5: "eighth",
        1: "quarter",
        2: "half",
        4: "whole"
    }



class KeySignature:
    """
    Fields:
        value (int)                     0-octave absolute value representation, i.e. 4 for E, 8 for Ab
        root_note (str)                 String representation, i.e. "E", "Ab"
        scale (list of str)             List of note names w/ len 7, i.e. ["E", "F#", "G", "A", "B", "C#", "D#"]
    Static Fields:
        flat_or_sharp (list of int)     1 is flat, 0 is sharp => tells which to use in key signature
        key_sig_values (list of int)    Circle of fifths: i.e. -5 is 5 flats, 3 is 3 sharps, 0 is no flats or sharps
    """

    """
    root_note    String representation, i.e. E
    value       0-octave int representation, i.e. 4
    scale       List of notes (len == 7)
    """
    value = None
    root_note = None
    scale = None

    flat_or_sharp = [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0]  # STATIC =>
    key_sig_values = [0,-5,2,-3,4,-1,-6,1,-4,3,-2,5]

    def __init__(self, root_note):
        """
            Args:
                root_note (str)

            *** EDIT FUNCTIONALITY TO RESTRICT TYPE OF ROOT NOTE ***
        """
        if (isinstance(root_note, basestring)):
            self.root_note = root_note
            self.value = get_note_index(self.root_note)
            if(self.value == -1):
                raise ValueError("Invalid note name!")
        elif (isinstance(root_note, int)):
            self.value = root_note
            self.root_note = get_flat_notes()[self.value]
        else:
            raise TypeError("Invalid rootNote parameter - must be int or string.")
        self.scale = KeySignature.build_scale(self.root_note)

    def __str__(self):
        return self.root_note + "[" + str(self.value) + "]: " + ", ".join(self.scale)



    def get_root_pitch(self):
        """
        Returns:
            (Pitch): A pitch in octave 0 - the root note of the key.
        """
        return Pitch(self.value, self)

    def get_all_note_values_in_key(self):
        """
        Get all absolute values of 8 octaves worth of scales, beginning on the root note.

        Returns:
            (list of int)
        """
        all_root_notes = [n * 12 + self.value for n in range(0, 8)]
        sublisted_scale_values = [[n + root for n in scale_steps] for root in all_root_notes]
        scale_values = [item for sublist in sublisted_scale_values for item in sublist]
        return scale_values

    def get_pitch(self,step,octave=0):
        """
        Get the pitch on the given scale step and octave.

        Args:
            step (int): scale step
            octave (int)

        Returns:
            (Pitch)
        """
        octave =  octave + (step-1) / 8
        step = (step-1) % 7 + 1
        absIndex = 12*octave+self.value+scale_steps[step-1]
        return Pitch(absIndex,self)

    @staticmethod
    def get_order_of(sharps_or_flats):
        """
        Gets the order of sharps or flats.

        Args:
            sharps_or_flats (str)

        Returns:
            (list of str)
        """
        if sharps_or_flats == "Sharps":
            return ["F","C","G","D","A","E","G"]
        elif sharps_or_flats == "Flats":
            return ["B","E","A","D","G","C","F"]
        else:
            raise ValueError("Invalid parameter! 'sharps_or_flats' must be either \"Sharps\" or \"Flats\"!")

    @staticmethod
    def build_scale(letter):
        """
        Get the scale in a key. Used primarily in the KeySignature constructor.
        This new method should sort out complex keys like G flat!

        Args:
            letter (str)

        Returns:
            (list of str)

        """
        value = get_note_index(letter)

        accidental_type = "Sharps" if (KeySignature.key_sig_values[value] > 0) else "Flats"
        order = KeySignature.get_order_of(accidental_type)
        order = order[0:abs(KeySignature.key_sig_values[value])]
        finished_scale = list(white_keys)

        for i,note in enumerate(white_keys):
            if note in order:
                finished_scale[i] = note+("#" if accidental_type == "Sharps" else "b")
        starting_value = finished_scale.index(letter)

        relative_steps = [(starting_value+step) % 7 for step in range(0,7)]

        finished_scale = [finished_scale[step] for step in relative_steps]
        return finished_scale

    @staticmethod
    def uses_flats_or_sharps(letter):
        """Does the key typically use flats or sharps?
        Args:
            letter (str): root_note of the key in question
        Returns:
            (str): "Flats", "Sharps", or "None" (for C)
        """

        if letter == 'C':
            return "None"
        index = get_note_index(letter)
        return "Flats" if KeySignature.flat_or_sharp[index] == 1 else "Sharps"