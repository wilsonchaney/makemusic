from Core import *
from xml import MusicXMLWriter
import time

start_time = time.time()

song = Song.create_random_attributes(beats_per_measure=4,unique_sections=3,total_sections=6,key_signature="C")
melody_engine = MelodyEngine(song)

total_repeat_count = 0
while True:
    repeat_needed = False

    # For each section, create the chord progression. (i.e. the chords for a verse, for a chorus, and so on.)
    for section in song.get_unique_sections():
        redo_count = 0
        chords = get_chord_progression(song.key, song.num_chords_in_section(section))

        # TODO: rework this. It's EXTREMELY inefficient.
        # Currently, I'm re-doing the chord progression generation if I make two chord progressions that are too similar
        # In chords.py, I need to add logic to ALWAYS generate a chord progression that is more "unique"
        while len([prog for prog in song.get_all_chord_progressions() if not different_enough(chords, prog)]) > 0 and total_repeat_count < 50:
            redo_count += 1
            chords = get_chord_progression(song.key, song.num_chords_in_section(section))
            if redo_count == 15:
                repeat_needed = True
                break # Restart all chord progresions
        if repeat_needed:
            break
        song.set_chord_progression(section,chords)
    if repeat_needed:
        total_repeat_count += 1
        continue
    else:
        break

# For each section, generate a melody (both pitches and rhythms)
for section in song.get_unique_sections():
    chords = song.get_chord_progression(section)
    section_data = []
    # See rhythm.py to understand this weight - it basically biases rhythm generation in favor of
    # shorter notes or longer ones, depending on the value.
    rhythmic_weight = random.randint(1,5)
    song.set_rhythm_weight(section,rhythmic_weight)
    melody = melody_engine.create_melody_beta(section)
    num_beats_expected = song.num_measures_in_section(section)*song.beats_per_measure
    num_beats_actual = sum([n.duration for n in melody])
    song.set_section_melody(section,melody_engine.divide_cross_measure_notes(melody))

# TODO: document this.
song.populate_measures()

last_pitch_before_final_measure = song.get_measures()[-1]._notes[-1].pitch
final_chord = Chord(1,"maj",song.key)
makeChordMeasure(final_chord,4)
song.append_final_measure(melody_engine.get_final_measure(song.beats_per_measure,final_chord,last_pitch_before_final_measure))

writer = MusicXMLWriter(song)
writer.write("output.xml")

end_time = time.time()

print "Done generating song."
print "Time Elapsed:",str(1000*(end_time-start_time))+"ms"