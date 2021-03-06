'''
Problem 4, 5
@author: Willis Wang and Hamster
'''

import sys
import math
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
    
    for i in range(len(data)-1, 0, -1):
        t[i-1] = backpointers[t[i] + "/" + str(i)]
        totalProb += probabilities[t[i] + "/" + str(i)]      

    knownCorrect = 0.0
    knownTotal = 0.0
    
    newCorrect = 0.0
    newTotal = 0.0
    for i in range(len(words)):
        if words[i] == "###":
            continue
        if words[i] in vocab:
            knownTotal +=1
        else:
            newTotal += 1
        
        if tags[i] == t[i]:
            if words[i] in vocab:
                knownCorrect +=1
            else:
                newCorrect += 1
        
    print "Tagging accuracy (Viterbi decoding): %.2f%% (known: %.2f%% novel: %.2f%%)" % (100 * (newCorrect + knownCorrect) / (newTotal + knownTotal),
                                                                                         100 * knownCorrect / knownTotal, 0 if newTotal == 0 else 100 * newCorrect / newTotal)
    print "Perplexity per Viterbi-tagged test word: %.3f" % math.exp(-totalProb/(len(words)-1))
                 
        
def forward_backward(file_name):
    test_data = file(file_name, 'r')
    data = test_data.readlines()
    
    global words 
    words = [None]*len(data)
    tags = [None]*len(data)
    
    
    words[0] = "###"
    
    alpha = dict()
    alpha["###/0"] = 0
    for i in range(1, len(data)):
        line = data[i].rstrip("\n")
        line = line.split("/")
        words[i] = line[0]
        tags[i] = line[1]
        
        for t_i in tag_set.get(words[i], all_training_tags):
            for t_i_1 in tag_set.get(words[i-1], all_training_tags):
                p = prob_tt(t_i, t_i_1) + prob_wt(words[i], t_i)
                alpha[t_i+"/"+str(i)] = logsumexp(alpha.get(t_i+"/"+str(i), float('-inf')),
                                                  alpha.get(t_i_1+"/"+str(i-1), float('-inf'))+p)
    S = alpha["###"+"/"+str(len(words)-1)]
    
    BestTag = namedtuple("BestTag", "tag probability")
    probabilities = [BestTag(None, float('-inf'))]*len(words)
    
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
    
    knownCorrect = 0.0
    knownTotal = 0.0
                
    newCorrect = 0.0
    newTotal = 0.0
    for i in range(len(words)):
        if words[i] == "###":
            continue
        if tags[i] == probabilities[i].tag:
            if words[i] in vocab:
                knownCorrect += 1
            else:
                newCorrect += 1
        if words[i] in vocab:
            knownTotal += 1
        else:   
            newTotal += 1
    print "Tagging accuracy (posterior decoding): %.2f%% (known: %.2f%% novel: %.2f%%)" % (100 * (newCorrect + knownCorrect) / (newTotal + knownTotal),
                                                                                         100 * knownCorrect / knownTotal, 0 if newTotal == 0 else 100 * newCorrect / newTotal)


def logsumexp(x, y):
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
    return (vocab.get(w,0) + 1.0)/(len(vocab) + len(words) + 1.0)


def train(file_name):
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
    



all_training_tags = set([])

tw_singleton = dict()
tt_singleton = dict()

tt_count = dict()
tw_count = dict()


vocab = dict()
tag_count = dict()
tag_set = dict()

if len(sys.argv) < 2:
    print "PUT YO FILES IN HERE YO"
    exit()
training_file = sys.argv[1]
test_file = sys.argv[2]


train(training_file)
test(test_file)
forward_backward(test_file)





    
    
    