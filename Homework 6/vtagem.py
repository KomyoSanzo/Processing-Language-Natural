'''
Created on Apr 18, 2016

@author: Willis Wang and Hamster
'''

import sys
import math
import copy
from collections import namedtuple

def test(file_name):
    test_data = file(file_name, 'r')
    data = test_data.readlines()
    
    global words 
    words = [None]*len(data)
    tags = [None]*len(data)
    probabilities = dict()
    backpointers = dict()

    mus = dict()
    mus["###/0"] = 0.0
    
    words[0] = "###"


    #VITERBI'S SHIT
    for i in range(1, len(data)):
        line = data[i].rstrip("\n")
        line = line.split("/")
        words[i] = line[0]
        tags[i] = line[1]
        
        for t_i in tag_set.get(words[i], all_training_tags):
            for t_i_1 in tag_set.get(words[i-1], all_training_tags):
                p = prob_tt(t_i, t_i_1) + prob_wt(words[i], t_i)
                mu_temp = mus[t_i_1 + "/" + str(i-1)] + p
                
                if t_i + "/" + str(i) not in mus or mu_temp >= mus[t_i + "/" + str(i)]:
                    mus[t_i + "/" + str(i)] = mu_temp
                    probabilities[t_i + "/" + str(i)] = p
                    backpointers[t_i + "/" + str(i)] = t_i_1
    
    #FOLLOW BACKPOINTERS AND WHATNOT
    t = [None] * len(data)
    t[len(data) - 1] = "###"
    totalProb = 0.0
    
    for j in range(1, len(data)):
        i = len(data) - j;
        t[i-1] = backpointers[t[i] + "/" + str(i)]
        totalProb += probabilities[t[i] + "/" + str(i)]
    
    novelCorrect = 0.0
    novelTotal = 0.0
    knownCorrect = 0.0
    knownTotal = 0.0
    seenCorrect = 0.0
    seenTotal = 0.0
    for i in range(len(words)):
        if words[i] == "###":
            continue
        if tags[i] == t[i]:
            if vocab.get(words[i],0) > 0:
                knownCorrect += 1
            elif raw_vocab.get(words[i],0) > 0:
                seenCorrect += 1
            else:
                novelCorrect += 1
        if vocab.get(words[i], 0)> 0:
            knownTotal += 1
        elif raw_vocab.get(words[i], 0)> 0:
            seenTotal += 1
        else:
            novelTotal += 1
        
    # Print the results
    # If no novel words encountered, we are vacuously 100% accuracy
    print "Tagging accuracy (Viterbi decoding): %.2f%% (known: %.2f%% seen: %.2f%% novel: %.2f%%)" % \
          (100 * (novelCorrect + seenCorrect + knownCorrect) / (novelTotal + seenCorrect + knownTotal),
           100 * knownCorrect / knownTotal,
           0 if seenTotal == 0 else 100 * seenCorrect / seenTotal,
           0 if novelTotal == 0 else 100 * novelCorrect / novelTotal)
    print "Perplexity per Viterbi-tagged test word: %.3f" % math.exp(- totalProb / (len(words) - 1))
            
def forward_backward(file_name):
    test_data = file(file_name, 'r')
    data = test_data.readlines()
    
    global words 
    words = [None]*len(data)
    
    words[0] = "###"
    
    global tt_count_new
    global tw_count_new
    global tag_count_new
    tt_count_new = copy.deepcopy(tt_count_orig)
    tw_count_new = copy.deepcopy(tw_count_orig)
    tag_count_new = copy.deepcopy(tag_count_orig)
    
    
    
    alpha = dict()
    alpha["###/0"] = 0
    for i in range(1, len(data)):
        line = data[i].rstrip("\n")
        line = line.split("/")
        words[i] = line[0]
        
        for t_i in tag_set.get(words[i], all_training_tags):
            for t_i_1 in tag_set.get(words[i-1], all_training_tags):
                p = prob_tt(t_i, t_i_1) + prob_wt(words[i], t_i)
                alpha[t_i+"/"+str(i)] = logsumexp(alpha.get(t_i+"/"+str(i), float('-inf')),
                                                  alpha.get(t_i_1+"/"+str(i-1), float('-inf'))+p)
    S = alpha["###"+"/"+str(len(words)-1)]
    
    BestTag = namedtuple("BestTag", "tag probability")
    probabilities = [BestTag("###", float('-inf'))]*len(words)
    bi_probabilities = dict()
    
    
    beta = dict()
    beta["###"+"/"+str(len(words)-1)] = 0
    for i in range(len(data)-1, -1, -1):
        for t_i in tag_set.get(words[i], all_training_tags):
            if probabilities[i].probability < alpha.get(t_i+"/"+str(i),float('-inf')) + beta.get(t_i+"/"+str(i),float('-inf')) - S:
                probabilities[i] = BestTag(t_i, alpha.get(t_i+"/"+str(i),float('-inf')) + beta.get(t_i+"/"+str(i),float('-inf')) - S)
            for t_i_1 in tag_set.get(words[i-1], all_training_tags):
                p = prob_tt(t_i, t_i_1) + prob_wt(words[i], t_i)
                beta[t_i_1+"/"+str(i-1)] = logsumexp(beta.get(t_i_1+"/"+str(i-1),float('-inf')),
                                                     beta.get(t_i+"/"+str(i), float('-inf'))+p)
                if (bi_probabilities.get(t_i+"/"+str(i), BestTag("###",float('-inf'))).probability < 
                    alpha.get(t_i_1+"/"+str(i-1),float('-inf')) + p + beta.get(t_i+"/"+str(i), float('-inf')) - S):
                    bi_probabilities[t_i+"/"+str(i)] = BestTag(t_i_1, alpha.get(t_i_1+"/"+str(i-1),float('-inf')) + p + beta.get(t_i+"/"+str(i), float('-inf')) - S)
            
        if probabilities[i].tag+"/"+bi_probabilities.get(t_i+"/"+str(i),BestTag("###", float('-inf'))).tag not in tt_count_new:
            tt_count_new[probabilities[i].tag+"/"+bi_probabilities.get(t_i+"/"+str(i),BestTag("###", float('-inf'))).tag] = 1
        else:
            tt_count_new[probabilities[i].tag+"/"+bi_probabilities.get(t_i+"/"+str(i), BestTag("###",float('-inf'))).tag] += 1
    
        if words[i]+"/"+probabilities[i].tag not in tw_count_new:
            tw_count_new[words[i]+"/"+probabilities[i].tag] = 1
        else:
            tw_count_new[words[i]+"/"+probabilities[i].tag] += 1
            
        if probabilities[i].tag not in tag_count_new:
            tag_count_new[probabilities[i].tag] = 1
        else:
            tag_count_new[probabilities[i].tag] += 1
        
    runningP = 0.0
    for tag in all_training_tags:
        runningP = logsumexp(runningP, alpha.get(tag+"/1", 0) + beta.get(tag+"/1", 0))
    perplexity = math.exp(-runningP/(len(words)-1.0))
    print "Iteration : Perplexity per untagged raw word: %.2f" % (perplexity)
    
    
    global tt_count
    global tw_count
    global tag_count
    
    tt_count = copy.deepcopy(tt_count_new)
    tw_count = copy.deepcopy(tw_count_new)
    tag_count = copy.deepcopy(tag_count_new)

def logsumexp(x, y):
    if y == 0:
        return x
    if x == 0:
        return y
    if y <= x:
        return x + math.log(1 + math.exp(y-x))
    else:
        return y + math.log(1 + math.exp(x-y))
    
def prob_tt(t_1, t_2):
    lbda = 1.0 + tt_singleton[t_2]
    numerator = tt_count.get(t_1+"/"+t_2,0) + lbda*prob_tt_backoff(t_1)
    denominator = tag_count.get(t_2, 0) + lbda
    return math.log(float(numerator)/float(denominator))

def prob_tt_backoff(t):
    return tag_count[t]/(len(words)-1.0)


def prob_wt(w, t):
    
    if w == "###" and t == "###":
        return 0
    lbda = 1 + tw_singleton[t]
    numerator = tw_count.get(w+"/"+t,0) + lbda*prob_wt_backoff(w)
    denominator = tag_count.get(t,0) + lbda
    
    return math.log(float(numerator)/float(denominator))

def prob_wt_backoff(w):
    return (vocab.get(w,0) + raw_vocab.get(w,0) + 1.0)/(len(vocab) + len(raw_vocab) + len(words))


def train(file_name, raw_file_name):
    last_line = None
    training_data = file(file_name, 'r')
    
    #FOR REACH LINE IN THE TRAINING DATA
    for line in training_data:
        #SEPARATE IT INTO A LIST WITH TWO ELEMENTS
        line = line.rstrip("\n")
        line = line.split("/")
        
        
        #CHECK IF IT EXISTS IN VOCAB AND INCREMENT 
        if line[0] not in vocab:
            vocab[line[0]] = 1
            tag_set[line[0]] = []
        else:
            vocab[line[0]] += 1        
        
        #CHECK IF EXISTS IN TAG AND INCREMENT
        if line[1] not in tag_count:
            tag_count[line[1]] = 1
        else:
            tag_count[line[1]] +=1 
        
        
        #CHECK IF EXISTS IN TW_COUNT AND INCREMENT
        hashed_tw = line[0] + "/" + line[1]
        if hashed_tw not in tw_count:
            tw_count[hashed_tw] = 1
            tag_set[line[0]].append(line[1])
        else:
            tw_count[hashed_tw] += 1
        
        #CHECK SINGLETONS FOR TW
        if line[1] not in tw_singleton:
            tw_singleton[line[1]] = 0
            
        if tw_count[hashed_tw] == 1:
            tw_singleton[line[1]] += 1
        elif tw_count[hashed_tw] == 2:
            tw_singleton[line[1]] -= 1
        
        #CHECK IF EXISTS IN TT_COUNT AND INCREMENT
        if last_line != None:
            hashed_tt = line[1] + "/" + last_line
            if hashed_tt not in tt_count:
                tt_count[hashed_tt] = 1
            else:
                tt_count[hashed_tt] += 1
                
            #CHECK SINGLETONS FOR TT
            if last_line not in tt_singleton:
                tt_singleton[last_line] = 0
            if tt_count[hashed_tt] == 1:
                tt_singleton[last_line] += 1
            elif tt_count[hashed_tt] == 2:
                tt_singleton[last_line] -= 1
        
        if line[1] != "###":
            all_training_tags.add(line[1])
        
        last_line = line[1] 
    global tt_count_orig 
    tt_count_orig = copy.deepcopy(tt_count)
    global tw_count_orig
    tw_count_orig = copy.deepcopy(tw_count)
    global tag_count_orig
    tag_count_orig = copy.deepcopy(tag_count)
    
    raw_data = file(raw_file_name, 'r')
    for line in raw_data:
        line = line.rstrip("\n")
        line = line.split("/")
        
        if line[0] not in raw_vocab:
            raw_vocab[line[0]] = 1
        else:
            raw_vocab[line[0]] += 1      


all_training_tags = set([])

tw_singleton = dict()
tt_singleton = dict()

#current counts
tt_count = dict()
tw_count = dict()
tag_count = dict()

#new counts
tt_count_new = dict()
tw_count_new = dict()
tag_count_new = dict()

#original counts
tt_count_orig = dict()
tw_count_orig = dict()
tag_count_orig = dict()

vocab = dict()
raw_vocab = dict()
tag_set = dict()

if len(sys.argv) < 2:
    print "PUT YO FILES IN HERE YO"
    exit()
training_file = sys.argv[1]
test_file = sys.argv[2]
raw_file = sys.argv[3]

train(training_file, raw_file)

for i in range(4):    
    test(test_file)
    print "iteration: " + str(i)
    forward_backward(raw_file)





    
    
    