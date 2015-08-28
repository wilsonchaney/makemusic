from Core import *
from xml import MusicXMLWriter

import time
import numpy


totalFactor = 0
totalTime = 0
numRuns = 1
outputToXML = True

totalTime = 0

for run in range(0,numRuns):
    start = time.time()

    song = Song.create_random_attributes(beats_per_measure=4,unique_sections=3,total_sections=6)
    melody_engine = MelodyEngine(song)

    total_repeat_count = 0
    while True:
        repeat_needed = False
        for section in song.get_unique_sections():
            redo_count = 0
            chords = get_chord_progression(song.key, song.num_chords_in_section(section))

            while len([prog for prog in song.get_all_chord_progressions() if not different_enough(chords, prog)]) > 0 and total_repeat_count < 50:
                redo_count += 1
                chords = get_chord_progression(song.key, song.num_chords_in_section(section))
                if redo_count == 15:
                    repeat_needed = True
                    #print "Broke infinite loop."
                    break # Restart all chord progresions
            if repeat_needed:
                break

            song.set_chord_progression(section,chords)
        if repeat_needed:
            total_repeat_count += 1
            continue
        else:
            break
    for section in song.get_unique_sections():

        chords = song.get_chord_progression(section)
        section_data = []
        rhythmic_weight = random.randint(1,5)
        song.set_rhythm_weight(section,rhythmic_weight)
        #print section,rhythmic_weight
        #raw_input()
        melody = melody_engine.create_melody_beta(section)
        num_beats_expected = song.num_measures_in_section(section)*song.beats_per_measure
        num_beats_actual = sum([n.duration for n in melody])
        song.set_section_melody(section,melody_engine.divide_cross_measure_notes(melody))

    song.populate_measures()

    last_pitch_before_final_measure = song.get_measures()[-1]._notes[-1].pitch
    final_chord = Chord(1,"maj",song.key)
    makeChordMeasure(final_chord,4)
    song.append_final_measure(melody_engine.get_final_measure(song.beats_per_measure,final_chord,last_pitch_before_final_measure))

    mid = time.time()
    writer = MusicXMLWriter(song)
    writer.write("output.xml")

    end = time.time()

    totalTime += 1000*(end-start)
    for section in song.get_unique_sections():
        pass
        #print section,("measures:"+str(song.num_measures_in_section(section))),("chords:"+str(song.num_chords_in_section(section)))
        #print song.get_rhythm_weight(section),"\n"
    #print song.section_structure
print "Execution time: ",totalTime/numRuns,"ms per song"
print "Done"