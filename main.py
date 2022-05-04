from random import randint

from music21 import *

SIZE_OF_POPULATION = 1024
RESULT_OF_POPULATION = 32
NUM_OF_MUTATIONS = 128
POPULATIONS = 100


class Chords:
    """This class contains only static methods witch related with chords"""

    @staticmethod
    def get_major_triads(noteID):
        """This method returns a list of notes that form a major triad
        :param noteID - ID of the note in midi format
        """
        return [noteID, noteID + 4, noteID + 7]

    @staticmethod
    def get_minor_triads(noteID):
        """This method returns a list of notes that form a minor triad
        :param noteID - ID of the note in midi format
        """
        return [noteID, noteID + 3, noteID + 7]

    @staticmethod
    def get_dim(noteID):
        """This method returns a list of notes that form a diminished chords
        :param noteID - ID of the note in midi format
        """
        return [noteID, noteID + 3, noteID + 6]

    @staticmethod
    def get_sus2(noteID):
        """This method returns a list of notes that form a suspended second chords
        :param noteID - ID of the note in midi format
        """
        return [noteID, noteID + 2, noteID + 7]

    @staticmethod
    def get_sus4(noteID):
        """This method returns a list of notes that form a suspended fourth chords
        :param noteID - ID of the note in midi format
        """
        return [noteID, noteID + 5, noteID + 7]

    @staticmethod
    def getChord(_chord):
        """This method returns a list of notes that form a minor triad
        :param _chord - is format of chord represented as tuple of two elements where first is initial id of note and
        second is represent type of musical triad
        1 - major triad
        2 - minor triad
        3 - diminished chords
        4 - suspended second chords
        5 - suspended fourth chords
        """
        if _chord[1] == 1:
            return Chords.get_major_triads(_chord[0])
        elif _chord[1] == 2:
            return Chords.get_minor_triads(_chord[0])
        elif _chord[1] == 3:
            return Chords.get_dim(_chord[0])
        elif _chord[1] == 4:
            return Chords.get_sus2(_chord[0])
        elif _chord[1] == 5:
            return Chords.get_sus4(_chord[0])
        return []


class ElementPart:
    """
    This class made object that contains 4 chords and make some operations with it.
    This object can be represented as measure stream.
    """

    def __init__(self):
        """This method init object of class ElementPart"""
        self.chords = []
        self._score = None

    def getScore(self):
        """This method returns score of this object
        :return self score
        """
        return self._score

    def mutate(self):
        """This method change one of the chords to randomly defined"""
        chord_pos = randint(0, len(self.chords) - 1)

        chord_type = randint(0, 5)
        note_id = randint(0, 120)
        self.chords[chord_pos] = (note_id, chord_type,)

    def generate(self):
        """This method generate data of this object of class. For this object we create 4 randomly defined chords."""
        self.chords.clear()
        for i in range(4):
            chord_type = randint(0, 5)
            note_id = randint(0, 120)
            self.chords.append((note_id, chord_type,))

    def score(self, measures):
        """
        This method calculate score and save it in self attribute.
        the score defined as sum of scores of each note in chords and divided by number of Octaves and Names.
        if the note is equal to the note on the measure by name it gives 10 points of score.
        if the note is equal to the note on the measure by octaves it gives 20 points of score.
        if it is not chord and where we just rest it gives 1 points of score.

        :param measures - is list of measures. Each measure is tuple of the sets of Names and Octaves in original
        composition.
        """
        score = 0
        setOctaves = set()
        setNames = set()
        for measure in measures:
            for _chord in self.chords:
                _list = Chords.getChord(_chord)
                if len(_list) == 0:
                    score += 1
                for _note in _list:
                    if _note // 12 in measure[1]:
                        score += 20
                    if _note % 12 in measure[0]:
                        score += 10
                    setOctaves.add(_note // 12)
                    setNames.add(_note % 12)

        self._score = score / (len(setNames) + 1) / (len(setOctaves) + 1)

    def makeNewElementPart(self, el1, el2):
        """
        This method generate data for this object of class by two other object given as parent objects.
        Here get all odd chords from first parent object and all other from second parent objects.

        :param el1 - first parent object
        :param el2 - second parent object
        """
        isFirst = True
        self.chords.clear()
        for i in range(len(el1.chords)):
            if isFirst:
                isFirst = False
                self.chords.append(el1.chords[i])
            else:
                isFirst = True
                self.chords.append(el2.chords[i])

    def getMeasure(self):
        """
        This method make measure stream by the self chords. Here we combine some same chords and make their duration
        longer.

        :return measure stream
        """
        m = stream.Measure()
        array = []
        i = 0
        while i < len(self.chords):
            dur = 1
            while i + 1 < len(self.chords) and self.chords[i][0] == self.chords[i + 1][0] and self.chords[i][1] == \
                    self.chords[i + 1][1]:
                dur += 1
                i += 1
            array.append((self.chords[i][0], self.chords[i][1], dur,))
            i += 1

        for _chord in array:
            if len(Chords.getChord(_chord)) != 0:
                c = chord.Chord(Chords.getChord(_chord), duration=duration.Duration(_chord[2]))
                m.append(c)
            else:
                c = note.Rest(duration=duration.Duration(_chord[2]))
                m.append(c)
        return m


class Population:
    """
    This class made object that contains list of objects of the class ElementPart.
    This object can be represented as Part stream.
    This class created to make simulations of EA and get best chords for the composition.
    """

    def __init__(self, filename):
        """This method init object of class ElementPart, init attribute as object of class MainStream and calculate
        number of parts in initial composition."""
        self.elements = []
        self.results = []
        self.main_stream = MainStream(filename)
        self.numberOfParts = self.main_stream.getLength()

    def mutate(self):
        """This method change some of the elements of population by their mutate algo"""
        for i in range(NUM_OF_MUTATIONS):
            pos = randint(0, SIZE_OF_POPULATION - 1)
            self.elements[pos].mutate()

    def generate(self):
        """This method generate data of this object of class. Creating number of elements in equals to
        SIZE_OF_POPULATION """
        self.elements.clear()
        for i in range(SIZE_OF_POPULATION):
            el = ElementPart()
            el.generate()
            self.elements.append(el)

    def getBest(self, index):
        """This method calculate  scores for all elements and sort by decreasing order
        :param index - index of the part in in original composition
        """
        pos = 0
        self.elements = self.elements[:SIZE_OF_POPULATION]
        for el in self.elements:
            el.score(self.main_stream.measures()[index])
            pos += 1

        def _orderByScore(_element):
            """This method return score of the given element
            :param _element - given element is object of class ElementPart
            :return score
            """
            return _element.getScore()

        self.elements.sort(key=_orderByScore, reverse=True)
        self.elements = self.elements[:RESULT_OF_POPULATION]

    def makeNewPopulation(self):
        self.elements = self.elements[:RESULT_OF_POPULATION]
        for i in range(RESULT_OF_POPULATION):
            for j in range(RESULT_OF_POPULATION):
                if i == j:
                    continue
                el = ElementPart()
                el.makeNewElementPart(self.elements[i], self.elements[j])
                self.elements.append(el)
        self.mutate()

    def getPart(self):
        """This method return part stream of all elements in results list.
        We add all measure stream from all elements in results list to the resulting part stream.
        :return part stream
        """
        p = stream.Part()
        for el in self.results:
            p.append(el.getMeasure())
        return p

    def simulate(self, save=True, number=1):
        """Here we simulate evolutionary algo and get best of the each population and generate new population.
        :param save - do we need to save best result of the population in the midi file
        :param number - is number of simulations
        """
        mx_score = 0
        self.results.clear()
        for _ in range(number):
            res = []
            score = 0
            for i in range(self.numberOfParts):
                self.generate()
                for j in range(POPULATIONS):
                    self.getBest(i)
                    if j + 1 < POPULATIONS:
                        self.makeNewPopulation()
                res.append(self.elements[0])
                score += self.elements[0].getScore()
                print("Part no", i, " - ", score)
            print("Simulation no", _, " - ", score)
            if mx_score < score:
                self.results = res
                mx_score = score

        if save:
            self.main_stream.save(self.getPart())
        else:
            self.main_stream.show(self.getPart())


class MainStream:
    """
    This class made contains stream from the midi file and can make some operations with it.
    _measures is the list of list of tuple of the sets where contains information from the original composition
    divided by parts and measures and collected all octave and name for each measure.
    """
    stream = None
    _measures = None

    def __init__(self, filename):
        """This method init object of class MainStream.
        Here we reading file by given filename and save it stream in attribute of this object and calculate measures to
        the list of parts as list of measures where measure is tuple of sets of the Octaves and Names
        """
        self._filename = 'SanzharZhanalin.mid'
        mf = midi.MidiFile()
        mf.open(filename)
        mf.read()
        mf.close()
        self.stream = midi.translate.midiFileToStream(mf)
        self.makeMeasures(self.stream.measureOffsetMap().items())

    @staticmethod
    def makeMeasure(measure):
        """This method calculate measure as tuple of sets of the Octaves and Names.
        :param measure - is object of initial composition
        :return tuple as sets of the Octaves and Names.
        """
        arrayOctaves = set()
        arrayNames = set()
        for el1 in measure:
            if hasattr(el1, "isNote") and el1.isNote:
                arrayOctaves.add(el1.octave)
                arrayNames.add(el1.pitch.midi % 12)
            elif hasattr(el1, "isChord") and el1.isChord:
                for _note in el1.notes:
                    arrayOctaves.add(_note.octave)
                    arrayNames.add(_note.pitch.midi % 12)
        return tuple([arrayNames, arrayOctaves])

    def makeMeasures(self, measures):
        """This method calculate measures as the list of parts as list of measures
        where measure is tuple of sets of the Octaves and Names
        :param measures - is list of parts of initial composition
        :return - list of list of tuple
        """
        self._measures = []
        for el in measures:
            array = []
            for measure in el[1]:
                array.append(self.makeMeasure(measure))
            self._measures.append(array)

    def measures(self):
        """This method return calculate measures and if this is not calculated calculate it.
        :return measures - list of list of tuple
        """
        if self._measures is None:
            self.makeMeasures(self.stream.measureOffsetMap().items())
        return self._measures

    def getLength(self):
        items = self.stream.measureOffsetMap().items()
        return len(items)

    def save(self, part):
        """This method add given part of composition witch got from simulations of EA to stream and save it as midi file
        """
        s = self.stream
        s.insert(0, part)
        mf = midi.translate.streamToMidiFile(s)
        mf.open(self._filename, 'wb')
        mf.write()
        mf.close()

    def show(self, part):
        """This method add given part of composition witch got from simulations of EA to stream and show it
        """
        s = self.stream
        s.insert(0, part)
        s.show()


if __name__ == '__main__':
    """يا ربنا العظيم! قم بحماية هذا الرمز من الأخطاء السيئة ودع هذا الحل يحصل على علامة جيدة."""
    population = Population("input1.mid")
    POPULATIONS = 1000
    population.simulate(save=True, number=1)
