#!/usr/bin/env python

import sys
import random



class grammarRule:
    prob = 0.0
    RHS = []

class grammarTree:
    ruleDict = dict()
    probDict = dict()
    
pretty = False

tree = grammarTree()
if (len(sys.argv) > 1 and sys.argv[1] != '-t'):
    numberOfSentences = int(sys.argv[1])
else:
    numberOfSentences = 1

if ("-t" in sys.argv):
    pretty = True
f = open('grammar4.txt')

#Parse Grammar rules
for line in f:
    splitLine = line.split()
    for i in range(len(splitLine)):
        if '#' in splitLine[i] :
            splitLine = splitLine[0:i]
            break

    if (len(splitLine) > 0):
        LHS = splitLine[1]
        prob = float(splitLine[0])
        
        if (not tree.ruleDict.has_key(LHS)):
            tree.ruleDict[LHS] = []
            tree.probDict[LHS] = 0.0
            
        
        newRule = grammarRule()
        newRule.RHS = splitLine[2:len(splitLine)]
        newRule.prob = prob + tree.probDict[LHS]
        
        tree.probDict[LHS] = newRule.prob
        tree.ruleDict[LHS].append(newRule)


def generateNext(LHS):
    if (tree.ruleDict.has_key(LHS)):
        ret = ""
        rng = random.random()
        for node in tree.ruleDict[LHS]:
            if ((node.prob/tree.probDict[LHS])>= rng):
                for RHS in node.RHS:
                    ret += " " + generateNext(RHS)
                return ret.strip()
                
    else:
        return LHS

def prettyPrint(LHS, ret):
    if (tree.ruleDict.has_key(LHS)):
        ret += ("(" + LHS + "\t")
        
        rng = random.random()
        for node in tree.ruleDict[LHS]:
            if ((node.prob/tree.probDict[LHS]) >= rng):
                for i in range(len(node.RHS)):
                    ret = prettyPrint(node.RHS[i], ret)
                ret += (")")
                return ret
    else:
        ret += (" " + LHS)
        return ret

def formatPretty(para):
    tab = 0
    for i in range(len(para)):
        sys.stdout.write(para[i])
        if para[i] == "(":
            tab += 1
        elif para[i] == ")":
            tab -= 1
            if (i+1 < len(para) and para[i+1] != ')'):
                sys.stdout.write('\n' + tab*'\t')
        
            
    
    
for i in range (numberOfSentences):
    if (pretty):
        output = prettyPrint('ROOT', "")
        formatPretty(output)
        print "\n\n"
    else:        
        output = generateNext('ROOT')    
        sys.stdout.write(  output + '\n\n')

        
    