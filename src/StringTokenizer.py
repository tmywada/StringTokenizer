# =================================================================================
#                             String Tokenizer
# =================================================================================
#
import re
import copy
from itertools import product
import bz2
import pickle
import math
from urllib import request

# --- version
version = '0.0.1'

class Utilities:

    def save_pickled_bz2_file(self, object, file_path:str):
        """
        """
        if file_path.lower().endswith('.pbz2') == False:
            file_path = f'{file_path}.pbz2'
        with bz2.BZ2File(file_path, 'wb') as f:
            pickle.dump(object, f)
        return file_path

    def load_pickled_bz2_file(self, file_path:str):
        """
        """
        if file_path.lower().endswith('.pbz2') == False:
            file_path = f'{file_path}.pbz2'
        return pickle.load( bz2.BZ2File(file_path, 'rb') )

class GenerateBaseRegexPatterns:
    """
    Generate Regex Pattern. Define base element and configure incrementally.
    """
    def __init__(self):
        """
        """
        self.base = {
            'lower': 'a-z',
            'upper': 'A-Z',
            'digit': '0-9',
            'special': '-_*%'
        }

        self.patterns = dict()

        # --- generate patterns
        self.generate_patterns_sequence_one()
        self.generate_patterns_sequence_two()
        self.generate_patterns_sequence_three()
        self.generate_patterns_prefixed()

    def generate_patterns_sequence_one(self):
        """
        """
        for key,pattern in self.base.items():
            self.patterns[key.title()] = f'[{pattern}]+'
            
    def generate_patterns_sequence_two(self):
        """
        """
        for k0,k1 in product(self.base, self.base):
            if k0 == k1:
                continue

            key = f'{k0.title()}{k1.title()}'
            p0 = f'[{self.base[k0]}]+'
            p1 = f'[{self.base[k1]}]+'

            self.patterns[key] = f'{p0}{p1}'

    def generate_patterns_sequence_three(self):
        """
        """
        for k0,k1,k2 in product(self.base, self.base, self.base):
            if k0 == k1 or k1 == k2:
                continue

            key = f'{k0.title()}{k1.title()}{k2.title()}'
            p0 = f'[{self.base[k0]}]+'
            p1 = f'[{self.base[k1]}]+'
            p2 = f'[{self.base[k2]}]+'

            self.patterns[key] = f'{p0}{p1}{p2}'

    def generate_patterns_prefixed(self):
        """
        Alphabet includes both upper and lower cases
        """
        # --- 
        tmp_alphabet = f'{self.base["lower"]}{self.base["upper"]}'
        tmp_alphabet_digit = f'{tmp_alphabet}{self.base["digit"]}'

        # ---
        self.Alphabet      = f'[{tmp_alphabet}]+'
        self.AlphabetDigit = f'[{tmp_alphabet_digit}]+' 

class GenerateRegexPatterns(Utilities):

    def __init__(self):
        self.patterns_considered = [
            'Lower',
            'Digit',
            'LowerDigit',
            'UpperLower',
            'UpperLowerDigit'
        ]
        self.base_patterns = GenerateBaseRegexPatterns().patterns

    def count_square_bracketed_segments(self, input_regex:str):
        """
        ref: https://stackoverflow.com/a/2403159
        """
        pattern = '\[(.*?)\]'
        return len( re.findall(pattern, input_regex) )

    def generate_pattern_or(self):
        """
        """
        # --- initialization
        res = []
        counts = set()
        patterns = []

        # --- loop through patterns
        for pattern_name in self.patterns_considered:

            # --- wrong input
            if pattern_name not in self.base_patterns:
                print(f'error: {pattern_name} is not defined')
                continue

            # --- get pattern and number of []
            pattern = self.base_patterns[pattern_name]
            count   = self.count_square_bracketed_segments(pattern)

            patterns.append(
                {
                    'pattern': pattern,
                    'name': pattern_name,
                    'count': count
                }
            )

            # --- get distinct number of []
            counts.add( count )

        # --- loop throught number of [] (shold be desending order)
        for cnt in sorted(list(counts), reverse = True):

            # --- get patterns 
            _patterns = [v['pattern'] for v in patterns if v['count'] == cnt]

            # --- concatenate with '|'  (i.e., or)
            _patterns = '|'.join(_patterns)

            res.append(_patterns)

        # --- concantenate all with '|'
        pattern = '|'.join(res)

        return f'({pattern})'

class TokenizeString(GenerateRegexPatterns):

    def __init__(self):
        """
        replaced_stirng should be unusual as much as possible.
        """
        self.replaced_string = '|*R*|*E*|*P*|*L*|*A|*C*|*E*|*D*|'
        self.pattern_enclosing = '[0-9a-zA-Z]'
        self.file_path_word_source = './data/word_source.pbz2'
        self.file_path_words_counts = './data/words_counts.pbz2'

        # --- load pickled bz2 file
        tmp = self.load_pickled_bz2_file(self.file_path_word_source)
        self.word_cost = tmp['word_cost']
        self.max_word_length = tmp['max_word_length']

    def refresh_source_data(self, url:str=None, file_path_word_source:str=None, file_path_words_counts:str=None):
        """
        ref: https://stackoverflow.com/a/11642687
        """
        # --- set parameters
        if url == None:
            url = 'http://norvig.com/google-books-common-words.txt'

        if file_path_word_source == None:
            file_path_word_source = self.file_path_word_source

        if file_path_words_counts == None:
            file_path_words_counts = self.file_path_words_counts

        # --- initilization
        dictionary_word_counts = {}
        words = []

        for line in request.urlopen(url):
            _line = line.decode().lower()
            tmp = [v.strip() for v in _line.split()]
            dictionary_word_counts[tmp[0]] = int(tmp[1])
            words.append(tmp[0])

        # --- 
        total_counts = float(sum(dictionary_word_counts.values()))
        word_cost = dict((k, math.log((i+1)*math.log(total_counts))) for i,k in enumerate(words))
        max_word_length = max(map(len, dictionary_word_counts))

        # --- 
        res_source = {
            'word_cost': word_cost,
            'max_word_length': max_word_length
        }

        # --- save 
        self.save_pickled_bz2_file(res_source, file_path_word_source)
        self.save_pickled_bz2_file(dictionary_word_counts, file_path_words_counts)

        # --- save in state
        self.word_cost = word_cost
        self.max_word_length = max_word_length

        print('wrod sources are saved')

    def infer_delimiters(self, input_string:str, pattern:str):
        """
        
        """
        # --- initialization
        _input_string = copy.deepcopy(input_string)

        # --- retrieve tokens
        tokens = re.findall(pattern, input_string)

        if len(tokens) == 0:
            res = {}

        # --- replace retrieved tokens with default string
        for token in tokens:
            _input_string = _input_string.replace(token, self.replaced_string)
        
        delimiter_candidates = [v for v in _input_string.split(self.replaced_string) if len(v) != 0]

        # --- exclude case at top and end
        if len(delimiter_candidates) == 0:
            res = {}
        else:
            res = {
                'delimiter_candidates': delimiter_candidates,
                'tokens_retrieved': tokens
            }
        return res

    def tokenize_with_delimiters(self, input_string:str, delimiters:list, pattern_enclosing:str=None):
        """
        """
        # --- delimiter segment
        _seg_delimiter = '|'.join(delimiters)
        seg_delimiter = f'({_seg_delimiter})'

        # --- enclosing string
        if pattern_enclosing == None:
            pattern_enclosing = self.pattern_enclosing

        # --- pattern
        pattern = f'{pattern_enclosing}{seg_delimiter}{pattern_enclosing}'

        # --- tokenize
        tokens = re.findall(pattern, input_string)

        # ---
        res = {
            'pattern': pattern,
            'tokens_retrieved': tokens
        }

        return res

    def infer_space(self, input_string:str):
        """
        ref: https://stackoverflow.com/a/11642687
        """
        def best_match(i):
            candidates = enumerate(reversed(cost[max(0, i-self.max_word_length):i]))
            return min((c + self.word_cost.get(s[i-k-1:i], 9e999), k+1) for k,c in candidates)

        # Build the cost array.
        cost = [0]
        for i in range(1,len(s)+1):
            c,k = best_match(i)
            cost.append(c)

        # Backtrack to recover the minimal-cost string.
        out = []
        i = len(s)
        while i>0:
            c,k = best_match(i)
            assert c == cost[i]
            out.append(s[i-k:i])
            i -= k

        return " ".join(reversed(out))

