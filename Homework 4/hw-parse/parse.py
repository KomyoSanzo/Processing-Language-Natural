'''
Created on Mar 21, 2016

@author: Willis Wang & Katie Chang
HW4
'''

#change probabilities to weights
#want MINIMUM total weighted parse tree


import sys
import random
import math
import GrammarParsers
import ParseClasses  
  
        
        
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
            parseSentence(line, grammar)
    
    def parseSentence(self, sentence, gram):
        print "ACTUALLY parse sentence here"
        for i in range(100):
            print "I is code monkey"
        
        #INITIALIZE EVERYTHING (and burn all the babies)
        listOfWords = sentence.split()
        chart = []
        for i in len(listOfWords):
            chart.append([])
        
        for value in grammar["ROOT"]:
            chart[0].append(value)
            
        #predict
        
        
        








