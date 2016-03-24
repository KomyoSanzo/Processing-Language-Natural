'''
Created on Mar 21, 2016

@author: Willis Wang & Katie Chang
HW4
'''

#change probabilities to weights
#want MINIMUM total weighted parse tree


import sys
import random
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
            self.parseSentence(line, grammar)
    
    def parseSentence(self, sentence, gram):
        print "ACTUALLY parse sentence here"
        for i in range(100):
            print "I is code monkey"
        
        #INITIALIZE EVERYTHING (and burn all the babies)
        listOfWords = sentence.split()
        print listOfWords
        chart = []
        for i in listOfWords:
            chart.append([])
        
        print gram
        
        for value in gram["ROOT"]:
            chart[0].append(value)
            
        #predict
        




