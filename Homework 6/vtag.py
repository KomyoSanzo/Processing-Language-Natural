'''
Created on Apr 18, 2016

@author: Willis Wang and Hamster
'''

import sys
import math
from numpy.core.test_rational import denominator


def test(file_name):
    test_data = file(file_name, 'r')
    data = test_data.readlines()
    
    global words 
    words = [None]*len(data)
    tags = [None]*len(data)
    probabilities = dict()
    
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
    for i in range(len(words)):
        if words[i] == "###":
            continue
        if tags[i] == t[i]:
            if words[i] not in vocab:
                novelCorrect += 1
            else:
                knownCorrect += 1
        if words[i] not in vocab:
            novelTotal += 1
        else:
            knownTotal+= 1
        
    # Print the results
    # If no novel words encountered, we are vacuously 100% accuracy
    print "Tagging accuracy (Viterbi decoding): %.2f%% (known: %.2f%% novel: %.2f%%)" % \
          (100 * (novelCorrect + knownCorrect) / (novelTotal + knownTotal),
           100 * knownCorrect / knownTotal, 0 if novelTotal == 0 else 100 * novelCorrect / novelTotal)
    print "Perplexity per Viterbi-tagged test word: %.3f" % math.exp(- totalProb / (len(words) - 1))
                 
        

def prob_tt(t_1, t_2):
    if t_1 + "/" + t_2 in tt_count:
        numerator = tt_count[t_1+ "/" + t_2]
    else:
        numerator = 0
    denominator = tag_count[t_1]
    
    return math.log(float(numerator)/float(denominator))

def prob_wt(w, t):
    if w + "/" + t in tw_count:
        numerator = tw_count[w + "/" + t]
    else:
        numerator = 0
    denominator = tag_count[t]
    return math.log(float(numerator)/float(denominator))


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
        
        
        #CHECK IF EXISTS IN TT_COUNT AND INCREMENT
        if last_line != None:
           hashed_tt = last_line + "/" + line[1]
           if hashed_tt not in tt_count:
               tt_count[hashed_tt] = 1
           else:
               tt_count[hashed_tt] += 1
        
        if line[1] != "###":
            all_training_tags.add(line[1])
        
        last_line = line[1] 
    



all_training_tags = set([])

tt_count = dict()
tw_count = dict()
vocab = dict()
tag_count = dict()
tag_set = dict()
backpointers = dict()
mus = dict()
mus["###/0"] = math.log(1)


if len(sys.argv) < 2:
    print "PUT YO FILES IN HERE YO"
    exit()
training_file = sys.argv[1]
test_file = sys.argv[2]


train(training_file)
test(test_file)







    
    
    