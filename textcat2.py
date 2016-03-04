#!/usr/bin/python

# Sample program for hw-lm
# CS465 at Johns Hopkins University.

# Converted to python by Eric Perlman <eric@cs.jhu.edu>

# Updated by Jason Baldridge <jbaldrid@mail.utexas.edu> for use in NLP
# course at UT Austin. (9/9/2008)

# Modified by Mozhi Zhang <mzhang29@jhu.edu> to add the new log linear model
# with word embeddings.  (2/17/2016)

import math
import sys
import os

import Probs

# Computes the log probability of the sequence of tokens in file,
# according to a trigram model.  The training source is specified by
# the currently open corpus, and the smoothing method used by
# prob() is specified by the global variable "smoother". 

def main():
    course_dir = '/usr/local/data/cs465/'
    argv = sys.argv[1:]

    if len(argv) < 2:
        print """
Prints the log-probability of each file under a smoothed n-gram model.

Usage:   %s smoother lexicon trainpath files...
Example: %s add0.01 %shw-lm/lexicons/words-10.txt switchboard-small %shw-lm/speech/sample*

Possible values for smoother: uniform, add1, backoff_add1, backoff_wb, loglinear1
  (the \"1\" in add1/backoff_add1 can be replaced with any real lambda >= 0
   the \"1\" in loglinear1 can be replaced with any C >= 0 )
lexicon is the location of the word vector file, which is only used in the loglinear model
trainpath is the location of the training corpus
  (the search path for this includes "%s")
""" % (sys.argv[0], sys.argv[0], course_dir, course_dir, Probs.DEFAULT_TRAINING_DIR)
        sys.exit(1)

    smoother = argv.pop(0)
    lexicon = argv.pop(0)
    
    train_file = argv.pop(0)
    train_file2 = argv.pop(0)
    train1_probs = []
    train2_probs = []
    
    if not argv:
        print "warning: no input files specified"

    #Initialize language model data
    lm = Probs.LanguageModel()
    lm.set_vocab_size(train_file, train_file2)
    lm.set_smoother(smoother)
    lm.read_vectors(lexicon)
    
    
    #Create list of files to iterate through.
    files_list = []
    
    for arg in argv:
        if arg[len(arg)-1] == '*':
            for f in os.listdir(arg[0:len(arg)-1]):
                files_list.append(arg[0:len(arg)-1] + f)
        else:
            files_list.append(arg)
    
    
    #Attach log-2 probabilities for each training file
    argv = files_list
    lm.train(train_file)
    for testfile in argv:
        train1_probs.append(lm.filelogprob(testfile) / math.log(2))
    
    lm.train(train_file2)
    for testfile in argv:
        train2_probs.append(lm.filelogprob(testfile) / math.log(2))
    
    
    train1_count = 0.0
    train2_count = 0.0
    accuracy_num = []
    
    for i in range(len(train1_probs)):
        if (train1_probs[i] > train2_probs[i]):
            train1_count += 1
            if (os.path.split(train_file)[1][0:3] == os.path.split(argv[i])[1][0:3]):
                accuracy_num.append(True)
            else:
                accuracy_num.append(False)
                
            print "%s\t%s" % (train_file, argv[i])
        else:
            train2_count += 1
            if (os.path.split(train_file2)[1][0:3] == os.path.split(argv[i])[1][0:3]):
                accuracy_num.append(True)
            else:
                accuracy_num.append(False)
            print "%s\t%s" % (train_file2, argv[i])
            
    
    #GENERATE FILE START
    cmshit = open ("graph_output.txt", "w")
    
    ordered_file_list = []
    for individual_file in argv:
        ordered_file_list.append(int(os.path.split(individual_file)[1].split(".")[1]))
    #print argv
    
    accuracy_num = [x for (y, x) in sorted(zip(ordered_file_list, accuracy_num))]
    ordered_file_list = sorted(ordered_file_list)
    
    
    lowerBounds = ordered_file_list[0]
    currentBucket = []
    for i in range(len(ordered_file_list)):
        margin = (ordered_file_list[i] - lowerBounds)/((ordered_file_list[i] +lowerBounds)/2.0)
        if (margin < .2):
            currentBucket.append(accuracy_num[i])
        else:
            cmshit.write(str(lowerBounds) + "-" + str(ordered_file_list[i-1]) + "\t")
            accuracy = 0.0
            for num in currentBucket:
                if (num):
                    accuracy += 1
            cmshit.write (str(accuracy/len(currentBucket)) + "\n")
            
            lowerBounds = ordered_file_list[i]
            currentBucket = [lowerBounds]
    
    cmshit.write(str(lowerBounds) + "-" + str(ordered_file_list[i-1]) + "\t")
    accuracy = 0.0
    for num in currentBucket:
        if (num):
            accuracy += 1
    cmshit.write (str(accuracy/len(currentBucket)) + "\n")
    
    lowerBounds = ordered_file_list[i]
    currentBucket = [lowerBounds]
    
    cmshit.close()
    #GENERATE FILE END
    
            
            
    #Print results
    print str(train1_count) + " looked more like " + train_file + " (" + str(train1_count/(train1_count+train2_count)) + "%)"
    print str(train2_count) + " looked more like " + train_file2 + " (" + str(train2_count/(train1_count+train2_count)) + "%)"
    
    accuracy = 0.0
    for num in accuracy_num:
        if (num):
            accuracy +=1
        
    print "Accuracy: " + str(accuracy/len(argv))
    print "Error: " + str(1-accuracy/len(argv))

if __name__ ==  "__main__":
    main()
