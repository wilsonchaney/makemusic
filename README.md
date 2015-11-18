## makemusic - an algorithmic music composition engine
### Basic Idea
This is an algorithmic music composer/generator that I created. It composes using basic music theory, much like a human might - but without a "creative" element; Everything is systematic.

For the time being, songs consist of a single piano part - the left hand plays chords and the right hand plays melody.

#### Core Music Theory
The file [here](https://github.com/wilsonchaney/makemusic/blob/master/src/Core/music_theory.py) contains the "core" music theory. This includes pitches, notes, key signatures, and a few other things. It's really just the "tools" used for melody generation and more.

#### Melodies
Melodies are randomly generated in here, based on the chords being played. This is a bit more complex, and I'll update it soon.

#### Chords
All the functionality for chords and chord progressions is [here](https://github.com/wilsonchaney/makemusic/blob/master/src/Core/chords.py). Progressions are basically made with a simple state machine, where each state is a chord, with some edges/transitions taking you to the next chord in the progression (The chosen edge is random). There are some other nuances to this as well.

#### Key Signatures
Each song that is generated has a [key signature](https://github.com/wilsonchaney/makemusic/blob/master/src/Core/music_theory.py#L330-L472). This makes it easy to consider a pitch in two different ways - the absolute location on the piano in terms of half steps, and the position in the scale of that key signature. (This makes harmonies WAY easier)