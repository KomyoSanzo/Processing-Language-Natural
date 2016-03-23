'''
Created on Mar 21, 2016
The purpose of this module is to parse in grammar rules into the relevant dictionaries


@author: Willis Wang, Hamster
'''

        
        
#NECESSARY CLASSES FOR GRAMMAR PARSING
class grammarTree:
    ruleDict = dict()
    probDict = dict()

class Rule:
    prob = 0.0
    RHS = []
    
#Parser
def parseGrammar(file):
    f = open(file)
    tree = grammarTree()
    
    for line in f:
        splitLine = line.split()
        for i in range(len(splitLine)):
            if '#' in splitLine[i] :
                splitLine = splitLine[0:i]
                break

        if (len(splitLine) > 0):
            LHS = splitLine[1]
            prob = 0 - math.log(float(splitLine[0]), 2) #change from prob to weight
        
            #if this tree does not have this key already 
            if (not tree.ruleDict.has_key(LHS)):
                tree.ruleDict[LHS] = []
                tree.probDict[LHS] = 0.0
        
            

        
            ########
            #Will need to make changes HERE for dotted / non dotted rules yee...
            newRule = Rule()
            newRule.RHS = splitLine[2:len(splitLine)]
            newRule.prob = prob + tree.probDict[LHS]
        
            tree.probDict[LHS] = newRule.prob
            tree.ruleDict[LHS].append(newRule)

    print "doing something"
    #return grammar
    return 0



##Printing Pretty stuffs

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

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print "Error"
    else:
        file = sys.argv[1]
        sentenceFile = sys.argv[2]
        gram = parseGrammar(file)
        parseSentenceFile(sentenceFile, gram)
        
        if ("-t" in sys.argv):
            output = prettyPrint('ROOT', "")
            formatPretty(output)

        #prettyprint here



