'''
Created on Mar 23, 2016

@author: Willi Wang, Hamter
'''

import sys
  
#CLASS DEFINTIONS

class dottedRule:
    header = ""
    rule = [] # will be a Rule instance
    dot = -1 #int indicating index where dot is 
    startIndex = 0
    endIndex = -1
    weight = 0.0
    
    def __init__(self, nHeader = "", weight = 0.0, nRule  = [], nDot = -1, nStart = 0, nEnd = -1):
        self.header = nHeader
        self.rule = nRule
        self.dot = nDot
        self.startIndex = nStart
        self.endIndex = nEnd
        
    
    def isComplete(self):
        return (self.dot == len(self.rule))
    
    def toString(self):
        return str(self.header) + ' ' + str(self.dot) + ' ' + str(self.endIndex) + ' ' + str(self.startIndex)

    def symbolAfterDot(self):
        return self.rule[self.dot]


class columnEntry:
    rule = None
    index = 0

    def isComplete(self):
        return self.rule.isComplete()
    
    
class Chart:
    
    column_list = None
    hashed_columns = None
    
    
    def __init__ (self, grammar, sentence):
        
        self.column_list = [] 
        self.hashed_columns = []
        for i in range(len(sentence)+1):
            self.column_list.append([])
            self.hashed_columns.append({})
        
    def enqueue(self, rule, column):
        #if not c.hashed_columns.has_key(newRule.toString()):
        #    pass
        
        
        self.column_list[column].append(rule)
        indexedColumn = self.hashed_columns[column]
        indexedColumn[rule.toString()] = rule
        
        '''
        if (not rule.isComplete()):
            if (rule.symbolAfterDot() in indexedColumn):
                indexedColumn[rule.symbolAfterDot].append(rule)
            else:
                indexedColumn[rule.symbolAfterDot()] = [rule]
        '''    
    def getColSize(self):
        return len(self.column_list)

    def printC(self):
        for i in range(len(self.column_list)):
            toPrint = ""
            for j in self.column_list[i]:
                toPrint = toPrint + " " + j.toString()
            print toPrint + "\n"
    

        