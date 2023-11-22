#modules
from collections import deque

#python libs
import re
import logging

#3rd party libs
import enchant



class Title:

    title: str
    corrected_title: str
    final_words: list[str]
    word: str
    dictionary: enchant.Dict = enchant.Dict('el_GR')
    requires_more_editing: bool = False
    cut_words = set()
    logs: str
    letter_dict =  \
                {"a":"α",
                "b":"β",
                "e":"ε",
                "h":"η",
                "I":"ι",
                "k":"κ",
                "m":"μ",
                "n":"ν",
                "o":"ο",
                "p":"ρ",
                "t":"τ",
                "x":"χ",
                }
    custom_corrections = {
        'πολυρεζιν': 'πολυρεζίν',
        'χρυση': 'χρυσή',
        'ριχταρι': 'ριχτάρι',
        'δωρο': 'δώρο'
    }

    def __init__(self, title: str):
        self.title = title
        self.final_words = []
        self.interrupt = False
        self.logs = ''
        self.log(f"Original title: {self.title}")
        self.run()
        self.log(f"Corrected title: {self.corrected_title}")

    def log(self, line):
        self.logs += line + '\n'

    def ignore(self):
        pass


    def alphanumerics(self):
        if self.interrupt == True: return
        word = self.word
        if word.isalpha():
            return
        else:
            self.log(f"Word {word} is probably dimensions and it will be fixed based on custom rules")
            word = re.sub(r'(\d)[ΧχXx](\d)', r'\1x\2', word)
            word = re.sub(r'(\d)[ΕεEeCc][KkΚκMm]\.?', r'\1 εκ.', word)
            word = re.sub(r'(\d)[MmΜμ][LlΛλ]\.?', r'\1 ml', word)
            self.final_words.append(word)
            self.interrupt = True

    def latin(self):
        if self.interrupt == True: return
        word = self.word
        is_ascii = False
        ascii_counter = 0
        for letter in word:
            if ord(letter) < 255 and letter not in "/\\.-":
                ascii_counter += 1
            
        if ascii_counter == len(word):
            is_ascii = True

        if is_ascii:
            self.log('Word is not greek, ignoring')
            self.final_words.append(word.title())
            self.interrupt = True
        
        else:
            if ascii_counter == 0:
                self.log('Word is probably greek, resuming')
            elif ascii_counter > 0:
                self.log('Word contains non greek characters, attempting to correct')
                self.word = self.correct(word)
                self.log(f'Word {word.lower()} was changed to {self.word.lower()}')

    def helperwords(self):
        if self.interrupt == True: return
        word = self.word

        if word == 'τεμ.':
            self.final_words.append(final_word)
            self.interrupt = True
        if len(word) < 3:
            self.log(f"Word {word} is helper and it will be ignored")
            final_word = word.lower()
            self.final_words.append(final_word)
            self.interrupt = True


    def cutwords(self):
        #Cut words
        if self.interrupt == True: return
        word = self.word
        if word.endswith('.'):
            self.log(f"Word {word} is cut and will be marked and ignored")
            Title.cut_words.add(word)
            final_word = '???' + word.upper()
            self.final_words.append(final_word)
            self.requires_more_editing = True
            self.interrupt = True

    def spellcheck(self):
        if self.interrupt == True: return
        word = self.word.lower()

        if word in self.custom_corrections:
            self.log(f"Word {word} was found in the custom list and was corrected accordingly")
            self.final_words.append(self.custom_corrections[word].title())
            return

        is_correct = self.dictionary.check(word)
        if is_correct:
            self.log(f"Word {word} is found to be correct.")
            self.final_words.append(word.title())
        else:
            self.log(f"Word {word} is found to be incorrect")
            suggestion = self.dictionary.suggest(word)
            self.log(f"Possible suggestions:\n{suggestion}")
            if len(suggestion) > 0:
                temp_suggestion = suggestion.pop(0)
                self.log(f"The correction selected is {temp_suggestion}")
                self.final_words.append(temp_suggestion.title())
            else:
                self.final_words.append(word.upper())
                self.log(f"No suggestion was found in the dictionary, ignoring")


    def run(self):
        self.preprocess_title()
        self.process_words()
        self.postprocess_title()


    def preprocess_title(self):

        self.preprocessed_title = self.title

        self.preprocessed_title = re.sub(r'(\w)-(\D)', r'\1 \2', self.preprocessed_title)
        self.preprocessed_title = re.sub(r'(\d)[TtΤτ][EeΕε][ΜμMm].?', r'\1 τεμ.', self.preprocessed_title)
        self.preprocessed_title = self.preprocessed_title.replace('"', '').replace("'", "")
        self.preprocessed_title = re.sub(r'(\w)\.(\w)', r'\1. \2', self.preprocessed_title)
        self.preprocessed_title = self.preprocessed_title.replace('/', ' / ').replace('\\', ' \ ')
        self.preprocessed_title = re.sub(r'(\w\.?),', r'\1 , ', self.preprocessed_title)
        self.words = self.preprocessed_title.split()
        self.alnum_words = [word for word in self.words if len(word) > 1 and not word.isalpha()]
        


    def process_words(self):

        for word in self.words:
            self.interrupt = False
            self.word = word

            #preprocess

            #interrupting
            self.ignore()
            self.alphanumerics()
            self.latin()
            self.helperwords()
            self.cutwords()

            #non-interrupting
            self.spellcheck()

            #postprocess
        
        self.corrected_title = " ".join(self.final_words)
    
    def postprocess_title(self):
        # remove double periods
        self.corrected_title = self.corrected_title.replace('..', '.')
        self.corrected_title = self.corrected_title.replace(' , ', ', ')
        self.corrected_title = self.corrected_title.replace('Ivory', 'Ιβουάρ')


    def __repr__(self) -> str:
        return f"{self.title = } | {self.corrected_title = }"
    
    def get_tuple(self) -> tuple[str, str]:
        return (self.title, self.corrected_title, self.logs, self.requires_more_editing)
    
    def correct(self, word: str):
        letters = list(word.lower())

        for i, letter in enumerate(letters):
            if letter in self.letter_dict.keys():
                letters[i] = self.letter_dict[letter]
        return ''.join(letters).upper()
