#! /usr/bin/python

import sys
from collections import defaultdict

# import a ner.counts file, output a dictionary, which has (word, label) as its key and e as its value
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


#take ner_train.dat as input, change infrequent words into _RARE_
def into_rare(file, output):
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
            # count < 5, change word to rare
            if d[word] < 5:
                output.write("_RARE_ %s\n" % label)
            else:
                output.write(l)
        else:
            output.write(l)
    return

ner_count = open('./ner.counts', 'r')
train = open('./ner_train.dat', 'r+')
output = open('./ner_train.dat.rare_processed', 'r+')
e_dict = emission_parameter(ner_count)
into_rare(train, output)
# print e_dict[('will', 'O')]
# print e_dict[('Atlanta', 'I-LOC')]
