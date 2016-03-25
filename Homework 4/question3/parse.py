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
from _ast import Param
import datetime

#PARSING FUNCTIONS

class Parser:
    grammar = None
    
    def __init__(self, gramm):
        grammar = gramm
        
    def parseSentenceFile(self, file, grammar):
        sentenceFile = open(file)

        for line in sentenceFile:
            startTime = datetime.datetime.now()
            if line == "\n":
                #skip empty line
                continue
            sys.stdout.write("Processing: " + line)
            self.parseSentence(line, grammar)
            print "Time Elapsed: " + str(datetime.datetime.now()-startTime)
            print "\n\n"
            
        
        
        
    
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
        
        for i in range(c.getColSize()):
            #print "Processing Column: " + str(i)
            column = c.column_list[i]
            
            entry = 0
            columnHistory = set([])
            while (entry < len(column)):
                
                if(column[entry].isComplete()):
                    #ATTACH
                    column[entry].endIndex = i
                    back_column = c.column_list[column[entry].startIndex]
                    for value in back_column:
                        if not value.isComplete() and value.symbolAfterDot() == column[entry].header:
                            newRule = dottedRule(value.header, value.weight + column[entry].weight,
                                                 value.rule, value.dot+1,
                                                 value.startIndex, value.endIndex)
                            newRule.upPointer = column[entry]
                            newRule.leftPointer = value
                            
                            if not c.hashed_columns[i].has_key(newRule.toString()):
                                c.enqueue(newRule, i)
                    
                elif gram.ruleDict.has_key(column[entry].symbolAfterDot()) and i  < len(c.column_list):
                    #PREDICT
                    if column[entry].symbolAfterDot() not in columnHistory:
                        columnHistory.add(column[entry].symbolAfterDot())
                        for value in gram.ruleDict[column[entry].symbolAfterDot()]:
                            newRule = dottedRule(column[entry].symbolAfterDot(),
                                                 value.prob,
                                                 value.RHS,
                                                 0, 
                                                 i,
                                                 -1)
                            
                            if not c.hashed_columns[i].has_key(newRule.toString()):
                                c.enqueue(newRule, i)
                else:
                    #Scan
                    if i < len(sentence) and str(column[entry].symbolAfterDot()) == str(sentence[i]):
                        newRule = dottedRule(column[entry].header, 
                                             column[entry].weight,
                                             column[entry].rule,
                                             column[entry].dot+1,
                                             column[entry].startIndex,
                                             column[entry].endIndex)
                        newRule.leftPointer = column[entry]
                        newRule.upPointer = dottedRule(column[entry].rule[column[entry].dot],
                                                    0,
                                                    [],
                                                    0,
                                                    column[entry].startIndex,
                                                    column[entry].endIndex)
                        c.enqueue(newRule, i+1)
                
                entry += 1
        #c.printC()
        
        #==========================
        #WE NOW DO THE BACKTRACKING
        #==========================
        #Begin by finding the lowest valued S
        lowestWeight= float("inf")
        sentenceEntry = None
        
        for value in c.column_list[len(c.column_list)-1]:
            if (value.header == "ROOT" and value.isComplete() and value.weight < lowestWeight):
                sentenceEntry = value
                lowestWeight = value.weight
        
        #Begin recursion with the lowest found entry point
        
        if (sentenceEntry is not None):
            self.formatPretty(self.printEntry(sentenceEntry))
            print "\n" + str(lowestWeight)
        return c
        
    def formatPretty(self, para):
        tab = 0
        i = 0
        while(i < len(para)):
            sys.stdout.write(para[i])
            if para[i] == "(":
                tab += 1
            elif para[i] == ")":
                tab -= 1
                if (i+1 < len(para) and para[i+1] != ')'):
                    if para[i+1] == '(':
                        sys.stdout.write('\n' + tab*'\t')
                    else:
                        sys.stdout.write('\n' + tab*'\t' + para[i+1] + '\n' + tab*'\t')
                        i += 1
            i += 1
    def printEntry(self, entry):
        if (entry is None):
            return ""
        ret = ""
        if (entry.isComplete()):
            if ((entry.leftPointer is None) and (entry.upPointer is None)):
                return entry.header

            ret += "(" + entry.header + "\t"            
            if (not entry.leftPointer is None):
                ret += self.printEntry(entry.leftPointer)
            if (not entry.upPointer is None):
                ret += self.printEntry(entry.upPointer)
            ret += ")"
            return ret
        else:             
            if (not entry.leftPointer is None):
                ret += self.printEntry(entry.leftPointer)
            if (not entry.upPointer is None):
                ret += self.printEntry(entry.upPointer)
            return ret
            







