'''
Created on Mar 21, 2016

@author: Willis Wang & Katie Chang
HW4
'''

#change probabilities to weights
#want MINIMUM total weighted parse tree


import sys
import random
from ParseClasses import *
        
#PARSING FUNCTIONS

class Parser:
    grammar = None
    
    def __init__(self, gramm):
        grammar = gramm
        
    def parseSentenceFile(self, file, grammar):
        sentenceFile = open(file)

        for line in sentenceFile:
            if line == "\n":
                #skip empty line
                continue
            print line
            self.parseSentence(line, grammar)
    
    def parseSentence(self, sentence, gram):
#        print "ACTUALLY parse sentence here"
#        for i in range(5):
#            print "I is code monkey"

        #INITIALIZE EVERYTHING (and burn all the babies)
        listOfWords = sentence.split()
        print listOfWords
        
        c = Chart(gram, sentence)
        
#        for value in gram.ruleDict["ROOT"]:
#            print value.RHS

        for value in gram.ruleDict["ROOT"]:
            newRule = dottedRule("ROOT", 0, value.RHS, 0, 0, -1)
            c.enqueue(newRule, 0)














