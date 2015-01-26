#http://stackoverflow.com/posts/11158224/revisions
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from pprint import pprint

import lexicon

if __name__ == "__main__":

    with open("vulgarlatin.lex","r") as raw_lexicon:
        read_words = [x for x in raw_lexicon.read().splitlines() if x[0] != "#"]
        split_words = [x.split() for x in read_words]

    latin_lexicon = lexicon.Lexicon()

    latin_lexicon.language = "Vulgar Latin"
    latin_lexicon.set_date(200,"AD")
    
    #make Lexicons
    for line in split_words:
        latin_lexicon.add_entry(lexicon.LexiconEntry(*line))

    latin_lexicon.init_phonology()

for word in latin_lexicon.entries:
    print(word.lexicon_entry())

latin_phonology = latin_lexicon.phonology
print(latin_phonology.get_vowels())

syllable_types = set()

for entry in latin_lexicon.entries:
    for syllable in entry.phonetic.syllables:
        vs = []
        vs = "".join(["V" if x.is_vowel() else "C" for x in syllable.phonemes])
        syllable_types.add(vs)
        print(list(zip(syllable.phonemes,vs)))
        print(syllable.get_structure())
        if syllable.has_clusters():
            print(syllable.get_clusters())
         
print(syllable_types)
