__author__ = 'Wilson'
from elementtree.SimpleXMLWriter import XMLWriter
from Core.chords import Chord,makeChordMeasure
from Core.music_theory import *

class XMLNote(Note):
    def __init__(self,note,tie):
        Note.__init__(self,note.pitch,note.duration)
        self.tie = tie

class MusicXMLWriter:
    song = None #Core.MusicData.Song
    writer = None #elementtree.SimpleXMLWriter.XMLWriter
    currentBeat = 0
    divisions = 2 #Hmm
    currentMeasureIndex = -1
    def __init__(self,song):
        self.song = song
    def write(self,fileName):
        file = open(fileName,"w")
        file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        self.writer = XMLWriter(file)

        structure = self.writer.start("score-partwise",{"version":"3.0"})

        self.writer.start("part-list")
        self.writer.start("score-part",{"id":"P1"})
        self.writer.element("part-name","Music")
        self.writer.end("score-part")
        self.writer.end("part-list")
        self.writer.start("part",{"id":"P1"})


        for index,measure in enumerate(self.song.get_measures()):
            #raw_input()
            self.currentMeasureIndex = index
            self.currentBeat = 0

            self.writer.start("measure",{"number": str(index+1)})
            self.writer.start("attributes")
            self.writer.element("divisions",str(self.divisions))



            if(index == 0):
                self.writer.start("key")
                self.writer.element("fifths",str(KeySignature.key_sig_values[self.song.key.value]))
                self.writer.element("mode","major")
                self.writer.end("key")
                self.writer.start("time")
                self.writer.element("beats",str(measure.duration))
                self.writer.element("beat-type","4")
                self.writer.end("time")
                self.writer.element("staves","2")
                self.writer.start("clef",{"number":"1"})
                self.writer.element("sign","G")
                self.writer.element("line","2")
                self.writer.end("clef")
                self.writer.start("clef",{"number":"2"})
                self.writer.element("sign","F")
                self.writer.element("line","4")
                self.writer.end("clef")


            self.writer.end("attributes")

            self.writeChordSymbol(measure.chords[0])

            for note in measure._notes:
                if note.duration == 1.5 and self.currentBeat % 1 == 0.5:
                    splitNotes = self.splitDottedHalf(note)
                    #for x in splitNotes:
                        #print str(x.pitch)+", "+str(x.duration)
                    self.writeNoteXML(splitNotes[0],1,"start")
                    self.writeNoteXML(splitNotes[1],1,"stop")
                else:
                    if len(measure.harmonies) == 1:
                        if self.currentBeat == measure.harmonies[0][0]:
                            #print "harmony found: "+str(index+1)
                            self.writeNoteXML([note,measure.harmonies[0][1]],1)
                        else:
                            self.writeNoteXML(note,1)
                    else:
                        self.writeNoteXML(note,1)


            self.writer.start("backup")
            self.writer.element("duration",str(measure.duration*self.divisions))
            self.writer.end("backup")
            ### OLD
            #c = measure.chords[0].get_random_voicing(measure.duration)
            #self.writeNoteXML(c,2)
            ### NEW
            newThing = makeChordMeasure(measure.chords[0],measure.duration)
            for note_tuple in newThing:
                self.writeNoteXML(note_tuple,2)
            ####

            self.writer.end("measure")
        self.writer.end("part")
        self.writer.end(structure)
    def writeNoteXML(self,note_s,staffNumber,tied = None):
        """
        This can output XML for either a note or a chord.
        """
        if isinstance(note_s,Note):
            note_s = [note_s]
        elif not isinstance(note_s,list):
            raise ValueError("WTF IS GOING ON")



        for i,n in enumerate(note_s):
            self.writer.start("note")
            self.writer.start("pitch")
            self.writer.element("step",n.pitch.letter[:1])
            if(n.pitch.sharp_or_flat != 0):
                self.writer.element("alter",str(n.pitch.sharp_or_flat))
            if n.pitch.letter == 'Cb':
                self.writer.element("octave",str(n.pitch.octave+1))
            else:
                self.writer.element("octave",str(n.pitch.octave))
            self.writer.end("pitch")
            self.writer.element("duration",str(n.duration*self.divisions))

            if(tied == "start" or n.tie == "start"):
                self.writer.start("notations")
                self.writer.element("tied",None,{"type":"start"})
                self.writer.end("notations")
            elif(tied == "stop" or n.tie == "stop"):
                self.writer.start("notations")
                self.writer.element("tied",None,{"type":"stop"})
                self.writer.end("notations")
            nextNote = self.song.get_measure_at_index(self.currentMeasureIndex).get_note_at_beat(self.currentBeat+n.duration)
            last_note_measure_change = int(math.floor((self.currentBeat-0.25)/4))
            last_beat = (self.song.beats_per_measure+self.currentBeat-0.25) % self.song.beats_per_measure
            lastNote = self.song.get_measure_at_index(last_note_measure_change).get_note_at_beat(last_beat)#I think this works...
            #The conditionals below are only self detecting for eighth notes, if parameter "beam" is None
            if n is None:
                brk = 0
            """
            if n.type == "eighth" and self.currentBeat % 1 == 0 and nextNote is not None and tied is None:
                if nextNote.type == "eighth":
                    self.writer.element("beam","begin")
            elif n.type == "eighth" and self.currentBeat % 1 == 0.5 and lastNote.type == "eighth"  and tied is None: #lastNote NULL???
                self.writer.element("beam","end")
            """
            self.writer.element("type",n.type)
            if(n.dot):
                self.writer.element("dot")

            self.writer.element("staff",str(staffNumber))
            if(i > 0):
                self.writer.element("chord")
            self.writer.end("note")
        self.currentBeat += note_s[0].duration


    def writeChordSymbol(self,chord):
        self.writer.start("harmony")
        self.writer.start("root")
        root = self.song.key.scale[chord.step-1]
        self.writer.element("root-step",root[0])
        if(len(root) > 1):
            alter = 1 if root[1] == '#' else -1
            self.writer.element("root-alter",str(alter))
        self.writer.end("root")
        typeText = "" if chord.chord_type == "maj" else "m"
        self.writer.element("kind","none",{"text":typeText})
        self.writer.end("harmony")
    def splitDottedHalf(self,note):
        firstEighth = Note(Pitch(note.pitch.value,self.song.key),0.5)
        secondQuarter = Note(Pitch(note.pitch.value,self.song.key),note.duration-0.5)
        return [firstEighth,secondQuarter]
        


#equation?

'''
<note>
        <pitch>
          <step>C</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <type>whole</type>
      </note>
'''