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
        sentence = sentence.split()
        
        c = Chart(gram, sentence)
        
#        for value in gram.ruleDict["ROOT"]:
#            print value.RHS

        for value in gram.ruleDict["ROOT"]:
            newRule = dottedRule("ROOT", value.prob, value.RHS, 0, 0, -1)
            c.enqueue(newRule, 0)
            print newRule.toString();
            
        for i in range(c.getColSize()):
            print "Processing Column: " + str(i)
            column = c.column_list[i]
            
            entry = 0
            
            while (entry < len(column)):
                if(column[entry].isComplete()):
                    print "IS COMPLETED"
                    #ATTACH
                    column[entry].endIndex = i
                    back_column = c.column_list[column[entry].startIndex]
                    for value in back_column:
                        if not value.isComplete() and value.symbolAfterDot() == column[entry].header:
                            newRule = dottedRule(value.header, value.weight,
                                                 value.rule, value.dot+1,
                                                 value.startIndex, value.endIndex)
                            
                            c.enqueue(newRule, i)
                            print newRule.toString()
                    
                elif gram.ruleDict.has_key(column[entry].symbolAfterDot()) and i + 1 < len(c.column_list):
                    #PREDICT
                    print "IS PREDICTED: " + str(column[entry].symbolAfterDot())
                    for value in gram.ruleDict[column[entry].symbolAfterDot()]:
                        newRule = dottedRule(column[entry].symbolAfterDot(),
                                             value.prob,
                                             value.RHS,
                                             0, 
                                             i,
                                             -1)
                        if not c.hashed_columns[i].has_key(newRule.toString()):
                            c.enqueue(newRule, i)
                            print newRule.toString()
                else:
                    print "IS SCANNED"
                    if i < len(sentence) and str(column[entry].symbolAfterDot()) == str(sentence[i]):
                        newRule = dottedRule(column[entry].header, 
                                             column[entry].weight,
                                             column[entry].rule,
                                             column[entry].dot+1,
                                             column[entry].startIndex,
                                             column[entry].endIndex)
                        c.enqueue(newRule, i+1)
                        print newRule.toString()
                
                entry += 1
        c.printC()
            
            









