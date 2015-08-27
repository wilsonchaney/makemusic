import random

from music_theory import *
from rhythm import *
from song_data import Measure

PITCH_CHANGE = [-2, -1, 1, 2]


class MelodyEngine:
    """
    Contains logic used to create the melody for a song.

    Fields:
        song (Song)
        scale_values (list of int)
    """

    song = None
    scale_values = None

    def __init__(self, song):
        self.song = song
        self.scale_values = song.key.get_all_note_values_in_key()

    def get_next_note(self, last_pitch_index, duration, chords):
        """Gets the next note in a melody line.
        Args:
            last_pitch_index (int): index in self.scale_values of the last pitch
            duration: rhythm of the note that is being decided on
            chords: chords behind the note in question
        :return: index (in self.scale_values) of new note
        """
        possible_values = [last_pitch_index + pc for pc in
                           PITCH_CHANGE]  # Get all possible next notes, by index in scale_values
        possible_values = [p for p in possible_values if
                           self.scale_values[p] <= TREBLE_CLEF_RANGE[1] and self.scale_values[p] >= TREBLE_CLEF_RANGE[
                               0]]  # Filter to valid range in treble clef
        if len(possible_values) == 0:
            raise Exception("There are no possible values for the next note!!!")

        if duration >= 0.5:
            filtered_to_chord = [pI for pI in possible_values if
                                 all([chord.note_fits(Pitch(self.scale_values[pI], self.song.key)) for chord in chords])]
            if len(filtered_to_chord) > 0:
                possible_values = filtered_to_chord
            else:
                brk = 0

        return possible_values[random.randint(0, len(possible_values) - 1)]

    def get_final_measure(self, num_beats, chord, last_pitch):
        """
        Currently the final measure of a song is just one note, that fits into the chord triad.
        :param num_beats: number of beats in the measure
        :param chord: chord for the measure
        :param last_pitch: Last pitch of the preceding measure - used to make sure melody doesn't "jump around" from measure to measure.
        :return: Measure object
        """
        triad_steps = [chord.step, (chord.step - 1 + 2) % 7 + 1, (chord.step - 1 + 4) % 7 + 1]
        all_triad_pitches = [x for x in self.scale_values if Pitch(x, self.song.key).scale_step in triad_steps]
        closest_pitch = all_triad_pitches[0]
        distance = abs(closest_pitch - last_pitch.value)
        for x in range(1, len(all_triad_pitches)):
            current_distance = abs(all_triad_pitches[x] - last_pitch.value)
            if current_distance < distance:
                closest_pitch = all_triad_pitches[x]
                distance = current_distance
        final_note = Note(Pitch(closest_pitch, self.song.key), num_beats)
        result = Measure(num_beats, [final_note])
        result.assign_chords([chord])
        return result

    def basic_harmonize(self, measure):
        max_note_occurences = max([n.duration for n in measure.notes])
        all_max_length_notes = [n for n in measure.notes if n.duration == max_note_occurences]
        note_to_work_with = all_max_length_notes[random.randint(0, len(all_max_length_notes) - 1)]
        note_index = self.scale_values.index(note_to_work_with.pitch.value)
        lower_harmony_index = note_index - 2
        higher_harmony_index = note_index + 2

        lower_pitch = Pitch(self.scale_values[lower_harmony_index], self.song.key)
        higher_pitch = Pitch(self.scale_values[higher_harmony_index], self.song.key)

        interval_low = scale_steps.index(lower_pitch.get_interval(self.song.key.get_root_pitch())) + 1
        interval_hi = scale_steps.index(higher_pitch.get_interval(self.song.key.get_root_pitch())) + 1

        allowed = MELODIC_ALLOWANCES[measure.chords[0].step]
        possible = [step for step in allowed if step == interval_low or step == interval_hi]

        if (len(possible) > 0 and random.random() > 0.7):
            interval = possible[random.randint(0, len(possible) - 1)]
            pitch = lower_pitch if interval == interval_low else higher_pitch
            harmony_note = Note(pitch, note_to_work_with.duration)
            return (measure.get_beat_of_note(note_to_work_with), harmony_note)
        else:
            return None
    def create_melody_beta(self,section):
        """
        Creates a melody for a section of a song.

        Melodies span many measures, but will account for things like downbeats and beginnings of measures,
        so that the melodic line somewhat adheres rhythmically.
        """
        chord_progression = self.song.get_chord_progression(section)
        rhythm = gen_rhythm(self.song.num_measures_in_section(section),self.song.beats_per_measure,self.song.get_rhythm_weight(section))

        pitch_index = random.randint(0, 2) * 2 + (4 * 7)  #Start on a triad pitch, in octave 4
        current_pitch = self.scale_values[pitch_index]
        melody = [Note(Pitch(current_pitch, self.song.key), rhythm[0])]
        current_beat = 0
        for x in range(1,len(rhythm)):
            end_note = current_beat+rhythm[x]
            #current_beat => end_note
            result = []
            while current_beat < end_note:
                #Do stuff
                chord_index = int(current_beat/4) % self.song.num_chords_in_section(section)
                """

                """
                result.append(chord_progression[chord_index])
                current_beat += 0.5
            pitch_index = self.get_next_note(pitch_index, rhythm[x], result)
            pitch = Pitch(self.scale_values[pitch_index], self.song.key)
            melody.append(Note(pitch, rhythm[x]))
            current_beat=end_note
        return melody

    def divide_cross_measure_notes(self,melody):
        result = []

        current_beat = 0
        for note in melody:
            starting_beat = current_beat
            starting_measure = int(starting_beat / self.song.beats_per_measure)

            ending_beat = (starting_beat+note.duration)
            ending_measure = int(ending_beat/self.song.beats_per_measure)


            if ending_measure > starting_measure and ending_beat % self.song.beats_per_measure != 0:
                first_duration = self.song.beats_per_measure-(starting_beat % self.song.beats_per_measure)
                split_notes = note.split_into_tied_notes(first_duration)
                result.append(split_notes[0])
                result.append(split_notes[1])
                #OHHHHH SHITTTTTT
            else:
                result.append(note)
            current_beat = current_beat + note.duration
        return result




def get_percent_valid_notes(song, measure, chord):
    """
    :return: Percent by duration of notes in measure that fit into the chord
    """
    valid_duration = 0
    for note in measure._notes:
        if (chord.note_fits(note.pitch)):
            valid_duration += note.duration
    return valid_duration / float(measure.duration)