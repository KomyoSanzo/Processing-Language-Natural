'''
Created on Mar 23, 2016

@author: Willis Wang, Hamster
'''
  
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
        return (dot == len(rule))
    
    def toString(self):
        return str(self.head) + ' ' + str(self.dot) + ' ' + str(self.endIndex) + ' ' + str(self.startIndex)

    def symbolAfterDot(self):
        return rule[dot+1]
class columnEntry:
    rule = None
    index = 0

    def isComplete(self):
        return self.rule.isComplete()
    
    
class Chart:
    
    column_list = None
    hashed_columns = None
    
    
    def __init__ (self, grammar, snentence):
        for i in range(100):
            print "I is code monkey"
        self.column_list = [] 
        self.hashed_columns = []
        for i in range(len(listOfWords)):
            self.column_list.append([])
            self.hashed_columns.append({})
        
    def enqueue(self, rule, column):
        self.column_list[column].append(rule)
        
        indexedColumn = self.hashed_columns[column]
        
        if (not rule.isComplete()):
            if (rule.symbolAfterDot() in indexedColumn):
                indexedColumn[rule.symbolAfterDot].append(rule)
            else:
                indexedColumn[rule.symbolAfterDot()] = [rule]
            
    
    
    

        