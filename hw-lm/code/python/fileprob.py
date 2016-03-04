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

  if not argv:
    print "warning: no input files specified"

  lm = Probs.LanguageModel()
  lm.set_smoother(smoother)
  lm.read_vectors(lexicon)
  lm.train(train_file)
  
  # We use natural log for our internal computations and that's
  # the kind of log-probability that fileLogProb returns.  
  # But we'd like to print a value in bits: so we convert
  # log base e to log base 2 at print time, by dividing by log(2).

  for testfile in argv:
    print "%g\t%s" % (lm.filelogprob(testfile) / math.log(2), testfile)


if __name__ ==  "__main__":
  main()
