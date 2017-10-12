#! /usr/bin/python

import sys
import math
from collections import defaultdict

# import a ner.counts file, output a dictionary, which has (word, label) as its key and e as its value
def emission_parameter(file):
    # create a dict with label as its key and count as its value
    label_count = defaultdict(int)
    # first traversal, record Count(y) into label_count
    #    while l: # until reach file end
    for l in file:
        line = l.strip()  # remove unnecessary space
        if line:  # Nonempty line
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
        if line:  # Nonempty line
            fields = line.split(" ")
            # finish reading the WORDTAG part, don't care the remaining
            if fields[1] != "WORDTAG":
                break
            else:  # have the format: count WORDTAG label word
                word = fields[3]
                label = fields[2]
                # find count(y) and calculate emission parameter
                e = (int(fields[0])) * 1.0 / label_count[label]
                d[(word, label)] = e

    return d


# calculate the label that maximize the emission parameter of _RARE_
def rare_emission(d):
    maxE = 0.0
    maxLabel = ""
    if ("_RARE_", "I-ORG") in d:
        if d[("_RARE_", "I-ORG")] > maxE:
            maxE = d[("_RARE_", "I-ORG")]
            maxLabel = "I-ORG"
    if ("_RARE_", "B-LOC") in d:
        if d[("_RARE_", "B-LOC")] > maxE:
            maxE = d[("_RARE_", "B-LOC")]
            maxLabel = "B-LOC"
    if ("_RARE_", "I-LOC") in d:
        if d[("_RARE_", "I-LOC")] > maxE:
            maxE = d[("_RARE_", "I-LOC")]
            maxLabel = "I-LOC"
    if ("_RARE_", "I-PER") in d:
        if d[("_RARE_", "I-PER")] > maxE:
            maxE = d[("_RARE_", "I-PER")]
            maxLabel = "I-PER"
    if ("_RARE_", "B-ORG") in d:
        if d[("_RARE_", "B-ORG")] > maxE:
            maxE = d[("_RARE_", "B-ORG")]
            maxLabel = "B-ORG"
    if ("_RARE_", "I-MISC") in d:
        if d[("_RARE_", "I-MISC")] > maxE:
            maxE = d[("_RARE_", "I-MISC")]
            maxLabel = "I-MISC"
    if ("_RARE_", "O") in d:
        if d[("_RARE_", "O")] > maxE:
            maxE = d[("_RARE_", "O")]
            maxLabel = "O"
    if ("_RARE_", "B-MISC") in d:
        if d[("_RARE_", "B-MISC")] > maxE:
            maxE = d[("_RARE_", "B-MISC")]
            maxLabel = "B-MISC"
    return maxE, maxLabel


# input a untagged word, a dict with all emission parameters, pick out the label maximize e
# pull out the emission parameter for the word, find the label that maximize the parameter
# if the word does not exist, give it label _RARE_
def naive_tagger(word, d, rareE, rareL):
    # if the word does not exist, we will assign it _RARE_ label and use the _RARE_ prob
    maxE = 0.0
    maxLabel = ""
    if (word, "I-ORG") in d:
        if d[(word, "I-ORG")] > maxE:
            maxE = d[(word, "I-ORG")]
            maxLabel = "I-ORG"
    if (word, "B-LOC") in d:
        if d[(word, "B-LOC")] > maxE:
            maxE = d[(word, "B-LOC")]
            maxLabel = "B-LOC"
    if (word, "I-LOC") in d:
        if d[(word, "I-LOC")] > maxE:
            maxE = d[(word, "I-LOC")]
            maxLabel = "I-LOC"
    if (word, "I-PER") in d:
        if d[(word, "I-PER")] > maxE:
            maxE = d[(word, "I-PER")]
            maxLabel = "I-PER"
    if (word, "B-ORG") in d:
        if d[(word, "B-ORG")] > maxE:
            maxE = d[(word, "B-ORG")]
            maxLabel = "B-ORG"
    if (word, "I-MISC") in d:
        if d[(word, "I-MISC")] > maxE:
            maxE = d[(word, "I-MISC")]
            maxLabel = "I-MISC"
    if (word, "O") in d:
        if d[(word, "O")] > maxE:
            maxE = d[(word, "O")]
            maxLabel = "O"
    if (word, "B-MISC") in d:
        if d[(word, "B-MISC")] > maxE:
            maxE = d[(word, "B-MISC")]
            maxLabel = "B-MISC"

    # none of the above case, the word does not exist before
    if maxE == 0.0 and maxLabel == "":
        maxE = rareE
        maxLabel = rareL
    return maxE, maxLabel


# take a file whose input is untagged, return a file with input with the format: word label logProb
def predict_label(train_file, untagged_input, tagged_output):
    # use train_file to calculate all emission parameter
    d = emission_parameter(train_file)
    # find the emission parameter and corresponding label for unseen word
    rareE, rareLabel = rare_emission(d)
    # tag all the entries
    for l in untagged_input:
        line = l.strip()
        if line:  # Nonempty line
            fields = line.split(" ")
            word = fields[0]
            e, label = naive_tagger(word, d, rareE, rareLabel)
            e = math.log(e, 2)
            tagged_output.write("%s %s %f\n" % (word, label, e))
        else:  # empty line just print
            tagged_output.write(l)
    return


train_file = open('./4_1.txt', 'r')
untagged_input = open('./ner_dev.dat', 'r')
tagged_output = open('./4_2.txt', 'r+')
predict_label(train_file, untagged_input, tagged_output)