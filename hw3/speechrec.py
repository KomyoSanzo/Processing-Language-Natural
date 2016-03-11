#!/usr/bin/python

# Sample program for hw-lm
# CS465 at Johns Hopkins University.

# Converted to python by Eric Perlman <eric@cs.jhu.edu>

# Updated by Jason Baldridge <jbaldrid@mail.utexas.edu> for use in NLP
# course at UT Austin. (9/9/2008)

# speechrec.py
# katie chang willis wang
# 8.b

import math
import sys

import Probs

# ======================================================================

def logProb(utter, priorLogProb, lm, lexicon, model):

    logprob = 0.0
    x = Probs.BOS
    y = Probs.BOS

    for z in utter.split():
        if model == "trigram":
            prob = lm.prob(x,y,z)
        elif model == "bigram":
            prob = lm.prob(Probs.OOV,y,z)
        elif model == "unigram":
            prob = lm.prob(Probs.OOV,Probs.OOV,z)
        else:
            sys.exit("Error with n-gram model name")

        logprob += math.log(prob) / math.log(2)
        x = y
        y = z

    logprob += math.log(lm.prob(x,y,Probs.BOS)) / math.log(2)
  
    return priorLogProb + logprob

def best(filename, lm, lexicon, model):
    input = open(filename, 'r')
    lines = input.readlines()

    length = int(lines[0].split("\t")[0]) #length of one line, delimited by tabs
        
    bestLogProb = -99999

    toPrint = lines[1]

    i = 1 # skip first line

    while i < len(lines):
        pieces = lines[i].split("\t") #delimited by tabs
    
        logP = logProb(pieces[3][4:-5], float(pieces[1]), lm, lexicon, model)
    
        if logP > bestLogProb:
            bestLogProb = logP
            
            
            toPrint = lines[i].split("\t")[0] #fix here
            toPrint += " " + filename
            
            
            errorRate = pieces[0]
            numberErrors = float(errorRate) * int(pieces[2])
        i += 1
        
    input.close()
    return errorRate, numberErrors, length, toPrint

def main():
    course_dir = '/usr/local/data/cs465/'
    argv = sys.argv[1:]

    if len(argv) < 5:
        print """
Prints the log-probability of each file under a smoothed n-gram model.

Usage:   %s smoother lexicon n-gramModel trainpath files...
Example: %s add0.01 words-10.txt trigram switchboard easy025 easy034

Possible values for smoother: uniform, add1, backoff_add1, backoff_wb, loglinear1
  (the \"1\" in add1/backoff_add1 can be replaced with any real lambda >= 0
   the \"1\" in loglinear1 can be replaced with any C >= 0 )
trainpath is the location of the training corpus
  (the search path for this includes "%s")
""" % (sys.argv[0], sys.argv[0], Probs.DEFAULT_TRAINING_DIR)
        sys.exit(1)
    smoother = argv.pop(0)
    lexicon = argv.pop(0)
    model = argv.pop(0)
    train_file = argv.pop(0)

    if not argv:
        print "warning: no input files specified"

    lm = Probs.LanguageModel()
    lm.set_smoother(smoother)
    lm.read_vectors(lexicon)
    lm.train(train_file)

    total_words = 0
    total_errors = 0.0

    for testfile in argv:
        errorRate, numberErrors, length, toPrint = best(testfile, lm, lexicon, model)
        total_words += length
        total_errors += numberErrors
        print toPrint

    print "%.3f\t Overall" % (total_errors/total_words)


if __name__ ==  "__main__":
    main()
