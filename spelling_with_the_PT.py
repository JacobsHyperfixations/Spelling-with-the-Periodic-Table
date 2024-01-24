# which words can be spelled with the atomic symbols
import copy
import math
import sys
import numpy as np

def load_words(word_list):
    with open(word_list, 'r') as word_file:
        eng_words = tuple(word_file.read().split())
    return eng_words
    
def load_symbols():
    with open('atomic_symbols.txt', 'r') as word_file:
        tmp = (word_file.read().split())
    return tmp
    
def sort_atomic_symbols(atomic_symbols):
    # creates 2D list, 1st dimension separates symbols that can't both be valid
    # 2nd dimension contains symbols that both can be valid
    choice_possible = []
    singles = []
    choice_impossible = copy.deepcopy(atomic_symbols)
    # remove singles
    for i in atomic_symbols:
        if len(i) == 1:
            singles.append(i)
            choice_impossible.remove(i)
    # remove doubles if they start with a single
    atomic_symbols = copy.deepcopy(choice_impossible)
    for i in singles:
        start_with_same_letter = [i]
        for j in atomic_symbols:
            if i == j[0]:
                start_with_same_letter.append(j)
                choice_impossible.remove(j)
        choice_possible.append(start_with_same_letter)
    # remove singles with no friends
    i = 0
    while i < len(choice_possible):
        if len(choice_possible[i]) == 1:
            choice_impossible.append(choice_possible[i][0])
            choice_possible.pop(i)
        else:
            i += 1
    return choice_possible, choice_impossible
    
def clean(arr):
    # remove empty items from list
    i = 0
    while i < len(arr):
        if arr[i] == '':
            arr.pop(i)
        else:
            i += 1
    return arr

class valid_word:

    def __init__(self, word):
        # create class to store information about each valid word
        self.word = word
        self.spelling = [''] * 200
        self.count = 0
        self.num_choices = 0
    
    def count_sym_num(self, arr):
        for i in self.used:
            if i == arr:
                return
        self.used.append(arr)
    
def determine_if_vaild(subword, word, choice_possible, choice_impossible):
    # recursively determine if a given string is valid. If it is, return integer > 0
    # If not, return 0
    if len(subword) == 0:
        word.count += 1
        return 1
    else:
        loop = 0
        tmp = 0
        level = 0
        for i in choice_possible:
            if subword[:len(i[0])] == i[0]:
                for j in i:
                    if subword[:len(j)] == j:
                        tmp = determine_if_vaild(subword[len(j):], word, choice_possible, choice_impossible)
                        if tmp > 0:
                            for k in range(word.count - tmp, word.count):
                                word.spelling[k] = j + ' ' + word.spelling[k]
                            level += tmp
                            loop += 1
                if loop == 2:
                    return level
                if loop == 1:
                    return level
                if loop == 0:
                    return 0
        for i in choice_impossible:
            if subword[:len(i)] == i:
                tmp = determine_if_vaild(subword[len(i):], word, choice_possible, choice_impossible)
                if tmp > 0:
                    for k in range(word.count - tmp, word.count):
                        word.spelling[k] = i + ' ' + word.spelling[k]
                    return tmp
        return tmp
    
def total_num_choices(spellings_str):
    # return the number of choices for a spelling tree
    spellings_arr = ['']*len(spellings_str)
    for i in range(len(spellings_str)):
        spellings_arr[i] = spellings_str[i].split()
    return rec_num_choices(spellings_arr)
    
def rec_num_choices(spellings_arr):
    if len(spellings_arr) == 1:
        return 0
    else:
        choice_count = 0
        choice1 = []
        choice2 = []
        for i in range(len(spellings_arr[0])):
            for j in range(1,len(spellings_arr)):
                if spellings_arr[0][i] != spellings_arr[j][i]:
                    for k in range(len(spellings_arr)):
                        if k < j:
                            choice1.append(spellings_arr[k][i+1:])
                        else:
                            choice2.append(spellings_arr[k][i+1:])
                    break
            if len(choice2) != 0:
                break
        left_choice_count = rec_num_choices(choice1)
        right_choice_count = rec_num_choices(choice2)
        if left_choice_count >= right_choice_count:
            return left_choice_count + 1
        else:
            return right_choice_count + 1
            
def get_valid_words(words_file, atomic_symbols):
    english_words = load_words(words_file)
    choice_possible, choice_impossible = sort_atomic_symbols(atomic_symbols)
    #valid_words = [''] * len(english_words)
    count = 0
    for i in english_words:
        current_word = valid_word(i)
        if determine_if_vaild(current_word.word, current_word, choice_possible, choice_impossible) > 0:
            #valid_words[count] = current_word
            count += 1
    return count
    
def add_atomic_count(spellings):
    atomic_count_return = np.zeros(118, dtype=int)
    for i in spellings:
        spelling = i.split()
        for j in spelling:
            atomic_count_return[atomic_symbols.index(j)] += 1
    return atomic_count_return/len(spellings)
                
if __name__ == '__main__':
    # sys.argv[1] is the path to the txt file that contains the word list through which to search
    # sys.argv[2] is the path to the txt file to which the valid words will be written
    # sys.argv[3] is the path to the txt file to which the valid words and extra information,
    # including all valid spellings, the total number of choices in the spelling tree,
    # the fraction of words spelled, and the symbol counts will be written
    
    # load in word list to check. Expects a text file with each word separated by a new line
    english_words = load_words(sys.argv[1])
    atomic_symbols = load_symbols()
    atomic_count = np.zeros(len(atomic_symbols), dtype=int)
    # sort atomic symbols to speed up code. By checking a single 'b' and finding it is invalid,
    # we don't also have to check doubles that begin with the 'b'
    choice_possible, choice_impossible = sort_atomic_symbols(atomic_symbols)
    valid_words = [''] * len(english_words)
    count = 0
    # look through each word and check if it is valid
    for i in english_words:
        current_word = valid_word(i)
        # if the word is valid ...
        if determine_if_vaild(current_word.word, current_word, choice_possible, choice_impossible) > 0:
            # store it
            valid_words[count] = current_word
            # increase valid word count by one
            count += 1
            # remove empty strings from spelling array
            clean(current_word.spelling)
            # find and store the number of choices for that word's spellings
            current_word.num_choices = total_num_choices(current_word.spelling)
            # add normalized atomic symbols counts
            atomic_count = atomic_count + add_atomic_count(current_word.spelling)
    
    # remove empty entries in array
    clean(valid_words)
    
    # write out results
    with open(sys.argv[2], 'w') as f:
        for i in valid_words:
            f.write(i.word + '\n')
    
    with open(sys.argv[3], 'w') as f:
        for i in valid_words:
            f.write('word: ' + i.word + '\n')
            f.write('number of valid spellings: ' + str(i.count) + '\n' + 'spellings:' + '\n')
            for k in i.spelling:
                f.write(k + '\n')
            f.write('number of choices: '+str(i.num_choices)+'\n')
            f.write('\n')
        f.write('\n' + 'fraction of valid_words: ' + str(len(valid_words)/len(english_words)) + '\n')
        f.write('number of symbol uses:' + '\n')
        for i in range(len(atomic_count)):
            f.write(atomic_symbols[i] + ': ' + str(atomic_count[i]) + '\n')
    print('Finished!')