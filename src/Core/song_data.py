import random
from datetime import timedelta  # For Song.getTimeWithBPM()

from music_theory import *


class Song:
    """
    The structure of a song - includes ALL song data, including a key, a section structure (ABA), and all of the notes/measures etc.

    Fields:
        key (KeySignature)                      Key of the song
        beats_per_measure (int)                 Currently, this must be the same in all measures of the song.
        section_structure (list of str)         ['A','B','A'] etc.

        _section_attributes (dict str->Section) Maps 'A' to the Section object containing all section data
        _measures (list of Measure)             All measures in the song - must be populated when section data is complete
    """
    key = None
    beats_per_measure = None
    section_structure = None
    _section_attributes = None
    _measures = None

    def __init__(self, key, beats_per_measure, section_structure, section_attributes):
        self.key = KeySignature(key)
        self.beats_per_measure = beats_per_measure
        self.section_structure = section_structure
        self._section_attributes = section_attributes
        self._measures = []

    def populate_measures(self):
        """Takes all the data in _section_attributes and correctly populates the measures in this song.
        """
        section_measures = {}
        for section_id in self.get_unique_sections():
            section_measures[section_id] = self._section_attributes[section_id].get_section_measures(
                self.beats_per_measure)
        for section_id in self.section_structure:
            for measure in section_measures[section_id]:
                self._measures.append(measure)

    def get_measures(self):
        if len(self._measures) == 0:
            raise Exception("Song measures haven't yet been populated!")
        return self._measures

    def get_measure_at_index(self, index):
        return self.get_measures()[index]

    def get_num_measures_total(self):
        return len(self._measures)

    def get_time_with_BPM(self, bpm):
        time = float(self.beats_per_measure * self.get_num_measures_total()) / bpm
        return timedelta(minutes=time)

    def num_measures_in_section(self, section):
        return self._section_attributes[section].num_measures

    def num_chords_in_section(self, section):
        return self._section_attributes[section].num_chords

    def get_unique_sections(self):
        return list(set(self.section_structure))

    def set_chord_progression(self, section, chord_progression):
        self._section_attributes[section].chord_progression = chord_progression

    def set_section_melody(self, section_id, melody):
        self._section_attributes[section_id].set_melody(melody)

    def get_section_melody(self, section_id):
        return self._section_attributes[section_id].get_melody()

    def get_chord_progression(self, section):
        return self._section_attributes[section].chord_progression

    def get_all_chord_progressions(self):
        result = []
        for section in self.get_unique_sections():
            chord_progression = self.get_chord_progression(section)
            if chord_progression is not None:
                result.append(chord_progression)
        return result

    def clear_all_chord_progressions(self):
        for section in self.get_unique_sections():
            self.set_chord_progression(section, None)

    def set_rhythm_weight(self, section_id, rhythm_weight):
        self._section_attributes[section_id].rhythm_weight = rhythm_weight

    def get_rhythm_weight(self, section_id):
        return self._section_attributes[section_id].rhythm_weight

    def append_final_measure(self, measure):
        self._measures.append(measure)


    @staticmethod
    def create_random_attributes(key_signature=None, beats_per_measure=None, unique_sections=None, total_sections=None):
        """
        measures_per_section and chords_per_section must be random. They are different for every section.
        """
        if key_signature is None:
            key_signature = get_flat_notes()[random.randint(0, 11)]
        if beats_per_measure is None:
            beats_per_measure = random.randint(2, 4)

        if unique_sections is None:
            unique_sections = random.randint(2, 4)
        if total_sections is None:
            total_sections = random.randint(4, 6)
        section_structure = Section.get_rand_sectioning(total_sections, unique_sections)
        unique_sections = set(section_structure)
        section_attributes = {}
        for section in section_structure:
            # num_measures = 2 ** random.randint(2, 4)
            num_measures = 16
            num_chords = num_measures / (2 ** random.randint(0, 2))
            section_attributes[section] = Section(section, num_measures, num_chords)
        return Song(key_signature, beats_per_measure, section_structure, section_attributes)


class Section:
    """
    Stores data for a "section" of a song, i.e. chorus or verse. Includes a melody
    Example fields:

    letter          A
    num_measures    8
    num_chords      4
    """
    letter = None
    num_measures = None
    num_chords = None
    melody = None

    rhythm_weight = 3  # 1-5

    chord_progression = None

    def __init__(self, letter, num_measures, num_chords, chord_progression=None, melody=None):
        if num_measures % num_chords != 0:
            raise ValueError("Invalid parameters!")
        self.letter = letter
        self.num_measures = num_measures
        self.num_chords = num_chords
        self.chord_progression = chord_progression
        self.melody = melody

    def set_melody(self, melody):
        self.melody = melody

    def get_melody(self):
        return self.melody

    def get_section_measures(self, beats_per_measure):

        current_beat = 0
        result = []

        current_measure_notes = []

        chord_index = -1
        # print self.num_measures,beats_per_measure
        #print " ".join([str(n.duration) for n in self.melody])
        #raw_input()
        for note in self.melody:
            #print "LOOP START"
            start_note = current_beat
            current_beat = current_beat + note.duration
            if start_note % beats_per_measure == 0:
                #print "Start of measure"
                if start_note > 0:
                    #print "(new measure)"
                    measure = Measure(beats_per_measure, current_measure_notes)
                    measure.assign_chords([self.chord_progression[chord_index]])
                    result.append(measure)
                current_measure_notes = []
                chord_index = (chord_index + 1) % len(self.chord_progression)
                #print "creating new, clear measure"
            #print note
            current_measure_notes.append(note)
        if self.num_measures != int(sum([n.duration for n in self.get_melody()]) / beats_per_measure):
            print "fack"
            raw_input()
        measure = Measure(beats_per_measure, current_measure_notes)
        measure.assign_chords([self.chord_progression[chord_index]])
        result.append(measure)
        #print self.letter+"-len result",len(result)
        return result

    @staticmethod
    def get_rand_sectioning(total_sections, unique_sections):
        if total_sections < 1 or unique_sections < 1:
            raise Exception("total_sections and unique_sections must both be at least 1!")
        elif total_sections == 1:
            return ['A']
        elif unique_sections == 1:
            raise Exception("Impossible to construct non-repeating section-list with given values: total(" + str(
                total_sections) + ") and unique(" + str(unique_sections) + ").")
        elif total_sections == 2:
            return ['A', 'B']
        else:
            if unique_sections > total_sections:
                raise Exception("unique_sections must be less than or equal to total_sections")
            result = ['A', 'B']
            possible = ['A', 'B']
            if unique_sections > 2:
                possible.append('C')
            for x in range(2, total_sections):
                working_with = [p for p in possible if p != result[-1]]
                chosen = working_with[random.randint(0, len(working_with) - 1)]
                if chosen == possible[-1] and len(possible) < unique_sections:
                    possible.append(chr(65 + len(possible)))
                result.append(chosen)
            return result


class Measure:
    """
    duration    int: number of beats in the measure
    notes       list of Note objects
    harmonies   list of tuple(int,Note) objects, where int is the beat that the Note object falls on

    Currently, harmonies only ever has one element.
    """

    duration = None
    _notes = None
    harmonies = None
    chords = []

    def __init__(self, duration, notes=[]):
        self.duration = duration
        self._notes = notes
        self.harmonies = []

    def assign_chords(self, chords):  # This is in HARDCORE beta.
        if type(chords) is list:
            self.chords = chords
        else:
            raise Exception("Invalid type for parameter chords: " + str(type(chords)))

    def append_note(self, note):
        self._notes.append(note)

    def get_note_at_beat(self, beat):
        if (beat < 0 or beat >= self.duration):
            return None
            # raise ValueError("Invalid beat parameter for getNoteAtBeat: "+str(beat))
        current_beat = 0
        for n in self._notes:
            current_beat += n.duration
            if beat < current_beat:
                return n
        raise Exception("Something went wrong.")

    def get_chord_at_beat(self, beat):
        """
        :param beat: This is currently zero index, but that might not be the best strategy.
        :return:
        """
        if (beat < 0 or beat >= self.duration):
            return None
        chord_duration = self.duration / len(self.chords)
        return self.chords[beat / chord_duration]


    def get_beat_of_note(self, note):
        current_beat = 0
        for n in self._notes:
            if n == note:
                return current_beat
            else:
                current_beat += n.duration