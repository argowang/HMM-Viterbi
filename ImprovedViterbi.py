#! /usr/bin/python

from collections import defaultdict
import sys
import math
import os
from subprocess import call

# emission_parameter and trigram_prob all take 4_1.txt as input
# emission_parameter will return a dictionary of e, (word, label) -> float
# trigram_prob will return a dictionary of p(y_n|y_n-1, y_n-2), (y_n-2, y_n-1, y_n) -> float


# a dictionary record the entry
def word_count(file):
    d = defaultdict(int)
    for l in file:
        line = l.strip()
        if line:  #Nonempty line
            fields = line.split(" ")
            if fields[1] == "WORDTAG":
                word = fields[-1]
                d[word] = fields[0]
            else:
                break
    return d

# import a file, output a dictionary, which has (word, label) as its key and e as its value
def emission_parameter(file):
    # create a dict with label as its key and count as its value
    label_count = defaultdict(int)
    # first traversal, record Count(y) into label_count
#    while l: # until reach file end
    for l in file:
        line = l.strip() # remove unnecessary space
        if line: # Nonempty line
            fields = line.split(" ")
            if fields[1] != "1-GRAM":
                continue
            else:
                # the line has format count 1-GRAM label
                label_count[fields[2]] = int(fields[0])
    d = defaultdict(float)

    # go back to the top of file
    file.seek(0)
    # second traversal, create a dict whose value is emission parameter
    for l in file:
        line = l.strip()
        if line: # Nonempty line
            fields = line.split(" ")
            # finish reading the WORDTAG part, don't care the remaining
            if fields[1] != "WORDTAG":
                break
            else:# have the format: count WORDTAG label word
                word = fields[3]
                label = fields[2]
                # find count(y) and calculate emission parameter
                e = (int(fields[0])) * 1.0 / label_count[label]
                d[(word, label)] = e

    return d


# take a countFile such as 4_1.txt as input, return a dict of q(y_n | y_n-2, y_n-1)
def trigram_prob(countFile):
    bigram = defaultdict(int)
    trigram = defaultdict(int)
    # first traversal, reform entries into dictionary
    for l in countFile:
        line = l.strip()
        if line: # nonempty
            fields = line.split(" ")
            # add into bigram dict
            if fields[1] == "2-GRAM":
                    bigram[(fields[2], fields[3])] = int(fields[0])
            # add into trigram dict
            elif fields[1] == "3-GRAM":
                trigram[(fields[2], fields[3], fields[4])] = int(fields[0])
    for key in trigram:
        trigram[key] = trigram[key] * 1.0 / bigram[(key[0], key[1])]
    return trigram

# return the possible labels one position could have
def K(index, length):
    # K_-1 = K_-2 = {*}
    if index == -1 or index == -2:
        return ["*"]
    # K_k = K for k = 1...n
    if index <= length:
        return ["O", "I-ORG", "B-LOC", "I-LOC", "I-PER", "I-MISC", "B-MISC", "B-ORG"]


# implement the viterbi algorithm
def viterbi(sentence, tri_d, e_d, word_d):
    n = len(sentence)
    for index in range(n):
        word = sentence[index]
        # the word does not appeared before, change the word according to the category
        if word_d[sentence[index]] == 0:
            if str.isupper(word):
                sentence[index] = "_ALLCAPS_"
            # All lowercase rare words:
            elif str.islower(word):
                sentence[index]= "_ALLLOWER_"
            # numbers
            elif word.isdigit():
                sentence[index] = "_ALLNUMS_"
            # small number with . e.g. 0.42
            elif ("." in word) and str.isdigit(word.replace(".", "")):
                sentence[index] = "_SMALLNUMS_"
            # large number with , e.g. 10,000
            elif ("," in word) and str.isdigit(word.replace(",", "")):
                sentence[index] = "_LARGENUMS_"
            # number with dashes(date) e.g. 1995-08-01
            elif ("-" in word) and str.isdigit(word.replace("-", "")):
                sentence[index] = "_DATE_"
            # capital words with period(s)
            elif ("." in word) and str.isupper(word.replace(".", "")):
                sentence[index] = "_CAPPERIOD_"
            # Initial capital
            elif str.isupper(word[0]) and str.islower(word[1:]):
                sentence[index] = "_INITCAP_"
            else:
                sentence[index] = '_RARE_'
    pi_dict = defaultdict(float)
    bp_dict = defaultdict()
    # Set pi(-1, *, *) = 0
    pi_dict[(-1, "*", "*")] = 0.0
    # For k = 0...n-1
    for k in range(n):
        for u in K(k - 1, n):
            for v in K(k, n):
                largest = float("-inf")
                for w in K(k-2, n):
                    # there should be no log0 case, since all words do not existed are replaced with _RARE_, if the word
                    # does exist, then we should use that emission parameter
                    if e_d[(sentence[k], v)]== 0:
                        sumPi = float("-inf")
                    # in case log0
                    # if (w, u, v) not in tri_d:
                    elif tri_d[(w, u, v)] == 0:
                        sumPi = float("-inf")
                    else:
                        sumPi = pi_dict[(k-1, w, u)]+math.log(tri_d[(w, u, v)], 2) + math.log(e_d[(sentence[k], v)],2)
                        # print sumPi, k, w, u, v, pi_dict[(k-1, w, u)], math.log(tri_d[(w, u, v)], 2) ,math.log(e_d[(sentence[k], v)],2)
                    if sumPi >= largest:
                        largest = sumPi
                        pi_dict[(k, u, v)] = largest
                        bp_dict[(k, u, v)] = w
    # calculate yn-1 yn
    maxProb = float("-inf")
    maxLLast = ""
    maxL2ndLast = ""
    for u in K(n - 2, n):
        for v in K(n-1, n):
            if (u, v, "STOP") not in tri_d:
                sumPi = float("-inf")
            else:
                sumPi = pi_dict[(n-1, u, v)] + tri_d[(u, v, "STOP")]
            if sumPi >= maxProb:
                maxProb = sumPi
                maxLLast = v
                maxL2ndLast = u
    y = defaultdict()
    y[n-1] = maxLLast
    y[n-2] = maxL2ndLast
    for k in reversed(range(n - 2)):
        y[k] = bp_dict[(k + 2, y[k + 1], y[k + 2])]
    res = []
    # return labels
    for k in range(n):
        res.append(y[k])
    prob = []
    y[-2] = "*"
    y[-1] = "*"
    # return accumulated possibility
    for k in range(1,n+1):
        prob.append(pi_dict[(k-1, y[k-2], y[k-1])])
    return res, prob


# parse the file into sentences according to empty line
def into_sentence(file, tri_d, e_d, word_d, output):
    sentence = []
    for l in file:
        line = l.strip()
        if line:  #nonempty
            sentence.append(line.split(" ")[0])
        else:  #empty line, end of one sentence
            original_sentence = sentence[:]
            res, prob = viterbi(sentence, tri_d, e_d, word_d)
            for index in range(len(sentence)):
                output.write("%s %s %f\n" % (original_sentence[index], res[index], prob[index]))
            sentence = []
            output.write("\n")


#take ner_train.dat as input, change infrequent words into categorizes
def into_categories(file, output):
    d = defaultdict(int)
    # first traverse, create a dict, whose key is word and value is count
    for l in file:
        line = l.strip()
        if line:  #Nonempty line
            fields = line.split(" ")
            # the word is recorded already
            word = fields[0]
            if word in d:
                d[word] += 1
            else: # the word is not recorded yet
                d[word] = 1

    file.seek(0)
    # second traverse, change rare word's label to _RARE_
    for l in file:
        line = l.strip()
        if line: # Nonempty line
            fields = line.split(" ")
            word = fields[0]
            label = fields[1]
            # count < 5, change word to corresponding categories
            if d[word] < 5:
                #  All capital words
                if str.isupper(word):
                    output.write("_ALLCAPS_ %s\n" % label)
                # All lowercase rare words:
                elif str.islower(word):
                    output.write("_ALLLOWER_ %s\n" % label)
                #  numbers
                elif word.isdigit():
                    output.write("_ALLNUMS_ %s\n" % label)
                #  small number with . e.g. 0.42
                elif ("." in word) and str.isdigit(word.replace(".", "")):
                    output.write("_SMALLNUMS_ %s\n" % label)
                #  large number with , e.g. 10,000
                elif ("," in word) and str.isdigit(word.replace(",", "")):
                    output.write("_LARGENUMS_ %s\n" % label)
                #  number with dashes(date) e.g. 1995-08-01
                elif ("-" in word) and str.isdigit(word.replace("-", "")):
                    output.write("_DATE_ %s\n" % label)
                #  capital words with period(s)
                elif ("." in word) and str.isupper(word.replace(".", "")):
                    output.write("_CAPPERIOD_ %s\n" % label)
                #  Initial capital
                elif str.isupper(word[0]) and str.islower(word[1:]):
                    output.write("_INITCAP_ %s\n" % label)
                else:
                    output.write("_RARE_ %s\n" % label)

            else:
                output.write(l)
        else:
            output.write(l)
    return


raw = open('./ner_train.dat', 'r+')
output = open('./ner_train.dat.categorized', 'r+')
into_categories(raw, output)
output.seek(0)
os.system("python count_freqs.py ner_train.dat.categorized > 6_input")

output2 = open('./6.txt', 'r+')
input = open('./ner_dev.dat', 'r')
train = open('./6_input', 'r')
tri_d = trigram_prob(train)
train.seek(0)
e_d = emission_parameter(train)
train.seek(0)
word_d = word_count(train)
into_sentence(input, tri_d, e_d, word_d, output2)
