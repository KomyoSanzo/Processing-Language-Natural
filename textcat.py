#!/usr/bin/python

#Modified from fileprob for HW3.2
#Katie Chang
#Feb 25th 2016

import math
import sys

import Probs

# Computes the log probability of the sequence of tokens in file,
# according to a trigram model.  The training source is specified by
# the currently open corpus, and the smoothing method used by
# prob() is specified by the global variable "smoother". 

def filelogprob(filename, langmod):
    infile = file(filename, "r")

    logprob = 0.0
    x = Probs.BOS
    y = Probs.BOS

    for line in infile:
        for z in line.split():
            prob = langmod.prob(x, y, z)
            logprob += math.log(prob)
            x = y
            y = z
    logprob += math.log(langmod.prob(x, y, Probs.EOS))
    infile.close()
    return logprob

def textcat(filename, langmod):
    print 'lol'

def main():
    course_dir = '/usr/local/data/cs465/'
    argv = sys.argv[1:]

    if len(argv) < 3:
        print """
Prints the log-probability of each file under a smoothed n-gram model.

Usage:   %s smoother lexicon trainpath1 trainpath2 files...
Example: %s add1 words-10.txt gen spam foo.txt bar.txt baz.txt

Possible values for smoother: uniform, add1, backoff_add1, backoff_wb, loglinear1
""" % (sys.argv[0], sys.argv[0])
    sys.exit(1)

    smoother = argv.pop(0)
    lexicon = argv.pop(0)
    train_file1 = argv.pop(0)
    train_file2 = argv.pop(0)

    print argv
  
    #dynamically get files afterwards...? NAH MAN they're the only things left in argv so we can just loop through them later yasss

    if not argv:
        print "warning: no input files specified"

    lm = Probs.LanguageModel()
    lm.set_smoother(smoother)

#Will have to train the two files separately
#call Probs.set_vocab_size() on the pair of training corpora
#    
#    train model from corpus 1
#    for each file,
#        compute its probability under model 1; save this in an array
#    
#    re-train model from corpus 2
#    for each file,
#        compute its probability under model 2; save this in an array
#    
#    finally, loop over the arrays to print the results

    train_array1 = []
    train_array2 = []

    lm.train(train_file1)

    for testfile in argv:
        train_array1.append(filelogprob(testfile, lm)/math.log(2))

    lm.train(train_file2)

    for testfile in argv:
        train_array2.append(filelogprob(testfile, lm)/math.log(2))

    for i in range(len(train_array1)):
        print "train_array1 at index " + str(i) + ": " + str(train_array1[i])
        print "train_array2 at index " + str(i) + ": " + str(train_array2[i])


    # We use natural log for our internal computations and that's
    # the kind of log-probability that fileLogProb returns.  
    # But we'd like to print a value in bits: so we convert
    # log base e to log base 2 at print time, by dividing by log(2).

    for testfile in argv:
        print "%g\t%s" % (filelogprob(testfile, lm)/math.log(2), testfile)

if __name__ ==  "__main__":
    main()
