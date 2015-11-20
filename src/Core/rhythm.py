import random

"""
rhythm.py

This module is responsible for generating rhythms, represented as lists of floats.

Currently, rhythms are generated for an entire section at a time (i.e. many measures).
"""

global_notes = [3,2,1.5,1,0.5] #Notes to use. More will be included in future versions!

def gen_rhythm(num_measures,beats_per_measure,note_length_weight=3,notes=global_notes):
    """
    
    :param num_measures:
    :param beats_per_measure:
    :param note_length_weight: 1 - 5 inclusive!
    :return:
    """
    total_beats = beats_per_measure*num_measures
    if notes == global_notes:
        notes = get_weighted_list(note_length_weight)
    result = []
    while(sum(result) < total_beats):
        current_beat = sum(result)
        total_remaining = total_beats-current_beat
        remaining_in_measure = total_remaining % 4
        available_notes = [note for note in notes if note <= total_remaining]

        if total_remaining % 1 == 0: #Downbeat
            if random.random() > 0.5:
                available_notes = [x for x in available_notes if x != 0.5]
        if random.random() < 0.6:
            notes_that_fit_measure = [x for x in available_notes if x <= remaining_in_measure]
            if len(notes_that_fit_measure) > 0:
                available_notes = notes_that_fit_measure

        note = available_notes[random.randint(0,len(available_notes)-1)]
        result.append(note)
        if total_remaining % 1 == 0 and total_remaining > 0 and note == 0.5:
            if random.random() > 0.5:
                result.append(0.5)
    return result

def get_weighted_list(weight):
    shifted_weight = weight-3
    result = []
    for i,note in enumerate(global_notes):
        num_copies = 10+(2-i)*2*shifted_weight
        result.extend(num_copies*[note])
    return result

def count_over_measure_ties(rhythm,beats_per_measure):
    result = 0
    current_beat = 0
    for note in rhythm:
        current_measure = current_beat / beats_per_measure
        current_beat = current_beat + note
        if int(current_beat / beats_per_measure) > current_measure and current_beat % beats_per_measure != 0:
            result += 1
    return result