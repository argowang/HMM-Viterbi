#! /usr/bin/python

from collections import defaultdict
import sys
import math


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
        trigram[key] = math.log(trigram[key] * 1.0 / bigram[(key[0], key[1])], 2)
    return trigram


# the input file contains trigram only, print out the trigram followed by log prob
def cal_trigram(rawTrigram, trigramDict, output):
    for l in rawTrigram:
        line = l.strip()
        if line:
            fields = line.split(" ")
            # input has the format u v w\n
            if trigramDict[(fields[0], fields[1], fields[2])] == 0:
                output.write("%s %s %s %f\n" %(fields[0], fields[1], fields[2], float("-inf")))
            else:
                output.write("%s %s %s %f\n" %(fields[0], fields[1], fields[2], trigramDict[(fields[0], fields[1], fields[2])]))
    return


countFile = open('./4_1.txt', 'r')
rawTrigram = open('./trigrams.txt', 'r')
output = open('./5_1.txt', 'r+')
d = trigram_prob(countFile)
cal_trigram(rawTrigram, d, output)
