# CS465 at Johns Hopkins University.
# Module to estimate n-gram probabilities.

# Updated by Jason Baldridge <jbaldrid@mail.utexas.edu> for use in NLP
# course at UT Austin. (9/9/2008)

# Modified by Mozhi Zhang <mzhang29@jhu.edu> to add the new log linear model
# with word embeddings.  (2/17/2016)


import math
import random
import re
import sys
import numpy
from pip._vendor.requests.packages.urllib3.packages.six import itervalues

# TODO for TA: Currently, we use the same token for BOS and EOS as we only have
# one sentence boundary symbol in the word embedding file.  Maybe we should
# change them to two separate symbols?
BOS = 'EOS'   # special word type for context at Beginning Of Sequence
EOS = 'EOS'   # special word type for observed token at End Of Sequence
OOV = 'OOV'    # special word type for all Out-Of-Vocabulary words
OOL = 'OOL'    # special word type for all Out-Of-Lexicon words
DEFAULT_TRAINING_DIR = "/usr/local/data/cs465/hw-lm/All_Training/"
OOV_THRESHOLD = 3  # minimum number of occurrence for a word to be considered in-vocabulary


# TODO for TA: Maybe we should use inheritance instead of condition on the
# smoother (similar to the Java code).
class LanguageModel:
  def __init__(self):
    # The variables below all correspond to quantities discussed in the assignment.
    # For log-linear or Witten-Bell smoothing, you will need to define some 
    # additional global variables.
    self.smoother = None       # type of smoother we're using
    self.lambdap = None        # lambda or C parameter used by some smoothers

    # The word vector for w can be found at self.vectors[w].
    # You can check if a word is contained in the lexicon using
    #    if w in self.vectors:
    self.vectors = None    # loaded using read_vectors()

    self.vocab = None    # set of words included in the vocabulary
    self.vocab_size = None  # V: the total vocab size including OOV.

    self.tokens = None      # the c(...) function
    self.types_after = None # the T(...) function

    self.progress = 0        # for the progress bar

    self.bigrams = None
    self.trigrams = None
    
    # the two weight matrices U and V used in log linear model
    # They are initialized in train() function and represented as two
    # dimensional lists.
    self.U, self.V = None, None  
    
    # self.tokens[(x, y, z)] = # of times that xyz was observed during training.
    # self.tokens[(y, z)]    = # of times that yz was observed during training.
    # self.tokens[z]         = # of times that z was observed during training.
    # self.tokens[""]        = # of tokens observed during training.
    #
    # self.types_after[(x, y)]  = # of distinct word types that were
    #                             observed to follow xy during training.
    # self.types_after[y]       = # of distinct word types that were
    #                             observed to follow y during training.
    # self.types_after[""]      = # of distinct word types observed during training.

  def prob(self, x, y, z):
    """Computes a smoothed estimate of the trigram probability p(z | x,y)
    according to the language model.
    """

    if self.smoother == "UNIFORM":
      return float(1) / self.vocab_size
    elif self.smoother == "ADDL":
      if x not in self.vocab:
        x = OOV
      if y not in self.vocab:
        y = OOV
      if z not in self.vocab:
        z = OOV
      return ((self.tokens.get((x, y, z), 0) + self.lambdap) /
        (self.tokens.get((x, y), 0) + self.lambdap * self.vocab_size))

      # Notice that summing the numerator over all values of typeZ
      # will give the denominator.  Therefore, summing up the quotient
      # over all values of typeZ will give 1, so sum_z p(z | ...) = 1
      # as is required for any probability function.

    elif self.smoother == "BACKOFF_ADDL":
        
        
      if x not in self.vocab:
        x = OOV
      if y not in self.vocab:
        y = OOV
      if z not in self.vocab:
        z = OOV
      ayy = (self.tokens.get(z, 0) + self.lambdap)/(self.tokens.get("",0) + self.lambdap * self.vocab_size)
      lmao = ((self.tokens.get((y, z), 0) + self.lambdap * self.vocab_size * ayy)/(self.tokens.get(y, 0) + self.lambdap * self.vocab_size))
      return ((self.tokens.get((x, y, z), 0) + self.lambdap * self.vocab_size * lmao)/(self.tokens.get((x, y), 0) + self.lambdap * self.vocab_size))
            
    elif self.smoother == "BACKOFF_WB":
      sys.exit("BACKOFF_WB is not implemented yet (that's your job!)")
    elif self.smoother == "LOGLINEAR":
      
      if x not in self.vectors:
          x = OOL
      if y not in self.vectors:
          y = OOL
      if z not in self.vectors:
          z = OOL
      vector_x = numpy.matrix(self.vectors[x])
      vector_y = numpy.matrix(self.vectors[y])
      vector_z = numpy.matrix(self.vectors[z])
      
      vector_u = numpy.matrix(self.U)
      vector_v = numpy.matrix(self.V)
      num = math.exp(float(vector_x*vector_u*vector_z.transpose() + vector_y*vector_v*vector_z.transpose()))

      den = 0.0
      for value in self.vectors.itervalues():
          vector_z = numpy.matrix(value)
          den += math.exp(float(vector_x*vector_u*vector_z.transpose() + vector_y*vector_v*vector_z.transpose()))
      return num/den
    else:
      sys.exit("%s has some weird value" % self.smoother)

  def filelogprob(self, filename):
    """Compute the log probability of the sequence of tokens in file.
    NOTE: we use natural log for our internal computation.  You will want to
    divide this number by log(2) when reporting log probabilities.
    """
    logprob = 0.0
    x, y = BOS, BOS
    corpus = self.open_corpus(filename)
    for line in corpus:
      for z in line.split():
        prob = self.prob(x, y, z)
        logprob += math.log(prob)
        x = y
        y = z
    logprob += math.log(self.prob(x, y, EOS))
    corpus.close()
    return logprob

  def read_vectors(self, filename):
    """Read word vectors from an external file.  The vectors are saved as
    arrays in a dictionary self.vectors.
    """
    with open(filename) as infile:
      header = infile.readline()
      self.dim = int(header.split()[-1])
      self.vectors = {}
      for line in infile:
        arr = line.split()
        word = arr.pop(0)
        self.vectors[word] = [float(x) for x in arr]

  def train (self, filename):
    """Read the training corpus and collect any information that will be needed
    by the prob function later on.  Tokens are whitespace-delimited.

    Note: In a real system, you wouldn't do this work every time you ran the
    testing program. You'd do it only once and save the trained model to disk
    in some format.
    """
    sys.stderr.write("Training from corpus %s\n" % filename)

    # Clear out any previous training
    self.tokens = { }
    self.types_after = { }
    self.bigrams = []
    self.trigrams = [];

    # While training, we'll keep track of all the trigram and bigram types
    # we observe.  You'll need these lists only for Witten-Bell backoff.
    # The real work:
    # accumulate the type and token counts into the global hash tables.

    # If vocab size has not been set, build the vocabulary from training corpus
    if self.vocab_size is None:
      self.set_vocab_size(filename)

    # We save the corpus in memory to a list tokens_list.  Notice that we
    # appended two BOS at the front of the list and a EOS at the end.  You
    # will need to add more BOS tokens if you want to use a longer context than
    # trigram.
    x, y = BOS, BOS  # Previous two words.  Initialized as "beginning of sequence"
    # count the BOS context
    self.tokens[(x, y)] = 1
    self.tokens[y] = 1

    tokens_list = [x, y]  # the corpus saved as a list
    corpus = self.open_corpus(filename)
    for line in corpus:
      for z in line.split():
        # substitute out-of-vocabulary words with OOV symbol
        if z not in self.vocab:
          z = OOV
        # substitute out-of-lexicon words with OOL symbol (only for log-linear models)
        if self.smoother == 'LOGLINEAR' and z not in self.vectors:
          z = OOL
        self.count(x, y, z)
        self.show_progress()
        x=y; y=z
        tokens_list.append(z)
    tokens_list.append(EOS)   # append a end-of-sequence symbol 
    sys.stderr.write('\n')    # done printing progress dots "...."
    self.count(x, y, EOS)     # count EOS "end of sequence" token after the final context
    corpus.close()

    if self.smoother == 'LOGLINEAR': 
      # Train the log-linear model using SGD.

      # Initialize parameters
      self.U = [[0.0 for _ in range(self.dim)] for _ in range(self.dim)]
      self.V = [[0.0 for _ in range(self.dim)] for _ in range(self.dim)]

      # Optimization parameters
      gamma0 = 0.01  # initial learning rate, used to compute actual learning rate
      epochs = 10  # number of passes

      self.N = len(tokens_list) - 2  # number of training instances

      # ******** COMMENT *********
      # In log-linear model, you will have to do some additional computation at
      # this point.  You can enumerate over all training trigrams as following.
      #
      # for i in range(2, len(tokens_list)):
      #   x, y, z = tokens_list[i - 2], tokens_list[i - 1], tokens_list[i]
      #
      # Note1: self.lambdap is the regularizer constant C
      # Note2: You can use self.show_progress() to log progress.
      #
      # **************************

      sys.stderr.write("Start optimizing.\n")

      #####################
      # TODO: Implement your SGD here
      #####################

      currentU = numpy.matrix(self.U)
      currentV = numpy.matrix(self.V)
      gamma = gamma0
      t = 0
      
      #For 1..E
      for e in range(epochs):
          F = 0.0
          prob_log = 0.0
          
          #For 1..N
          for i in range(2, len(tokens_list)):
              #UPDATE GAMMA
              gamma = gamma0/(1+gamma0*t*self.lambdap/self.N)
              
              #READ IN NEW X Y Z
              x, y, z = tokens_list[i-2], tokens_list[i - 1], tokens_list[i]
              if x not in self.vectors:
                  x = OOL
              if y not in self.vectors:
                  y = OOL
              if z not in self.vectors:
                  z = OOL
              x = numpy.matrix(self.vectors[x])
              y = numpy.matrix(self.vectors[y])
              z = numpy.matrix(self.vectors[z])
              
              Z = 0.0
              for value in self.vectors.itervalues():
                  z_prime = numpy.matrix(value)
                  Z += math.exp(float(x*currentU*z_prime.transpose() + y*currentV*z_prime.transpose()))
              
              #FOR each value in the matrices...
              F_summ_part = 0.0
              
              for j in range(self.dim):
                  for m in range(self.dim):
                      deltaF_U_summ_part = 0
                      deltaF_V_summ_part = 0
                      
                      for value in self.vectors.itervalues():
                          z_prime = numpy.matrix(value)
                          
                          num = math.exp(float(x*currentU*z_prime.transpose() + y*currentV*z_prime.transpose()))
                          deltaF_U_summ_part += (num/Z)*x[0,j]*z_prime[0,m]
                          deltaF_V_summ_part += (num/Z)*y[0,j]*z_prime[0,m]
                          if (numpy.array_equal(z_prime,z)):
                              prob_log = math.log(num/Z)
                      deltaF_U = x[0, j]*z[0,m] - deltaF_U_summ_part - 2*self.lambdap*currentU[j, m]/self.N
                      deltaF_V = y[0, j]*z[0,m] - deltaF_V_summ_part - 2*self.lambdap*currentV[j, m]/self.N
                      
                      currentU[j, m] = currentU[j, m] + gamma*deltaF_U
                      currentV[j, m] = currentV[j, m] + gamma*deltaF_V
                      F_summ_part += currentU[j, m] * currentU[j,m] + currentV[j, m] * currentV[j, m]
                      
              F += prob_log - (self.lambdap/self.N)*F_summ_part
              t += 1
          print "finished one epoch: " + str(F)
        
      self.U = currentU
      self.V = currentV        
      
    sys.stderr.write("Finished training on %d tokens\n" % self.tokens[""])

  def count(self, x, y, z):
    """Count the n-grams.  In the perl version, this was an inner function.
    For now, I am just using a class variable to store the found tri-
    and bi- grams.
    """
    self.tokens[(x, y, z)] = self.tokens.get((x, y, z), 0) + 1
    if self.tokens[(x, y, z)] == 1:       # first time we've seen trigram xyz
      self.trigrams.append((x, y, z))
      self.types_after[(x, y)] = self.types_after.get((x, y), 0) + 1

    self.tokens[(y, z)] = self.tokens.get((y, z), 0) + 1
    if self.tokens[(y, z)] == 1:        # first time we've seen bigram yz
      self.bigrams.append((y, z))
      self.types_after[y] = self.types_after.get(y, 0) + 1

    self.tokens[z] = self.tokens.get(z, 0) + 1
    if self.tokens[z] == 1:         # first time we've seen unigram z
      self.types_after[''] = self.types_after.get('', 0) + 1 

    self.tokens[''] = self.tokens.get('', 0) + 1  # the zero-gram


  def set_vocab_size(self, *files):
    """When you do text categorization, call this function on the two
    corpora in order to set the global vocab_size to the size
    of the single common vocabulary.

    NOTE: This function is not useful for the loglinear model, since we have
    a given lexicon.
     """
    count = {} # count of each word

    for filename in files:
      corpus = self.open_corpus(filename)
      for line in corpus:
        for z in line.split():
          count[z] = count.get(z, 0) + 1
          self.show_progress();
      corpus.close()

    self.vocab = set(w for w in count if count[w] >= OOV_THRESHOLD)

    self.vocab.add(OOV)  # add OOV to vocab
    self.vocab.add(EOS)  # add EOS to vocab (but not BOS, which is never a possible outcome but only a context)

    sys.stderr.write('\n')    # done printing progress dots "...."

    if self.vocab_size is not None:
      sys.stderr.write("Warning: vocab_size already set; set_vocab_size changing it\n")
    self.vocab_size = len(self.vocab)
    sys.stderr.write("Vocabulary size is %d types including OOV and EOS\n"
                      % self.vocab_size)

  def set_smoother(self, arg):
    """Sets smoother type and lambda from a string passed in by the user on the
    command line.
    """
    r = re.compile('^(.*?)-?([0-9.]*)$')
    m = r.match(arg)
    
    if not m.lastindex:
      sys.exit("Smoother regular expression failed for %s" % arg)
    else:
      smoother_name = m.group(1)
      if m.lastindex >= 2 and len(m.group(2)):
        lambda_arg = m.group(2)
        self.lambdap = float(lambda_arg)
      else:
        self.lambdap = None

    if smoother_name.lower() == 'uniform':
      self.smoother = "UNIFORM"
    elif smoother_name.lower() == 'add':
      self.smoother = "ADDL"
    elif smoother_name.lower() == 'backoff_add':
      self.smoother = "BACKOFF_ADDL"
    elif smoother_name.lower() == 'backoff_wb':
      self.smoother = "BACKOFF_WB"
    elif smoother_name.lower() == 'loglinear':
      self.smoother = "LOGLINEAR"
    else:
      sys.exit("Don't recognize smoother name '%s'" % smoother_name)
    
    if self.lambdap is None and self.smoother.find('ADDL') != -1:
      sys.exit('You must include a non-negative lambda value in smoother name "%s"' % arg)

  def open_corpus(self, filename):
    """Associates handle CORPUS with the training corpus named by filename."""
    try:
      corpus = file(filename, "r")
    except IOError, err:
      try:
        corpus = file(DEFAULT_TRAINING_DIR + filename, "r")
      except IOError, err:
        sys.exit("Couldn't open corpus at %s or %s" % (filename,
                 DEFAULT_TRAINING_DIR + filename))
    return corpus

  def show_progress(self, freq=5000):
    """Print a dot to stderr every 5000 calls (frequency can be changed)."""
    self.progress += 1
    if self.progress % freq == 1:
      sys.stderr.write('.')
