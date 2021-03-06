'''
fcheck.py 
@author: Claire

Parses facts against the vocabulary, 
should include in arguments the .v file and .f file 

'''

import predpar
import sys 
from string import *
import string 
import re
import factotum_lex
import factotum_globals

lex = factotum_lex.LexFacts()
g = factotum_globals.GlobalClass()

grammar_dict = {}
TypeHier = {}
PhraseList  = []
depth = 0
depthLim = 100 
AliasestoSubj = {}
MultiAl = []
Labels = {}
entrypoint = 0 
PossibleRootsToAdd = []

 

########################################################

def check_vocab():
    ''' Parses vocab using predpar over the .v passed into fcheck 
        so that we may use the output dictionary grammar to parse our facts 
    '''
    res_parseV = []
    res_parseV = predpar.parse_vocab()
    return res_parseV  

################################################

def add_predef_rules():
    
    grammar_dict['Start'] = [[':','Predefined'],
                             ['Phrase']
                             ]

    grammar_dict['Predefined'] = [['Primary Term', '<-', 'Single Alias'],
                                  ['Primary Term', '<-', 'Multi Alias '], 
                                  ['Single Alias', '->', 'Primary Term'],
                                  ['Primary Term', '[', 'Type', ']']
                                  ]
    return 

#############################################################

def go_thru_factFile():
    '''
    Opens up the given file,  reads in line by line, and
    uses factotum lexer to go thru and find the subject and predicates
    (nearly identical to go_thru_file used in predpar.py) 
    '''
    if len(sys.argv) < 3: 
        sys.stderr.write("must include fact (.f) file \n")
        raise SystemExit(1)
    
    factfile = open(sys.argv[2], 'r')
    
#    factfile = open('_wikidata_.f', 'r')
    
    facts = []
    line = ''
    line = factfile.readline()
    m = s = p =  r = c = ''
    px = []
    
    #sampled from factotum_entities 
    #READ IN LINES 
    
    while(len(line) > 0):
        my_fact = line[:-1]
        line = ''
        line = factfile.readline()
        
        while(len(line) > 0) and (line[0] == '-'):
            my_fact += '\n' + line[1:-1]
            line = ''
            line = factfile.readline()
            continue
        
        if my_fact != '':
            (m,s,p,px,r,c) = lex.breakup_fact(my_fact)
        
            p = p.strip() # get rid of whitespace
            if '<-' in my_fact and not '<-' in p:
                p = '<' + p
                
            marker = my_fact[0]
            if marker == ':':
                fstr = s + ' ' + p 
                facts.append([marker, fstr])
            
            else: 
                facts.append([s,p])
            
    
    return facts 
###################################################

def isDescendant(item, tmatch):
    ''' note: remember that the TypeHier maps subtype to the parent, 
    want to check if item is a descendant of tmatch 
    '''
    tmatch.strip()
    if tmatch == 'ANY': 
        if TypeHier.get(item):
            return True 
        else: 
            return False 
        return True 
    
    elif not item in TypeHier.keys(): #means you've parsed thru and made it to the root without finding a match 
        if item in AliasestoSubj.keys(): #means is an Alias
            ent = AliasestoSubj[item]
            return isDescendant(ent, tmatch)
        else: 
            return False 
    
    elif tmatch == item : 
        return True 
    
    else: 
        parent = TypeHier[item][1]
        return isDescendant(parent, tmatch)

#####################################################

def checkLabel(rule, fact, n):
    ''' Checks if there is a token type specification along with the 
        label, checks it, or just provides a label for fact[n]
    '''
     
    if rule.__class__ == list: 
        label = rule[0]
        
        if len(rule) > 1: 
            ttype = rule[1]
        
            x = checkTtype(ttype, fact, n)
        
            if x.__class__ == string: 
                if not label in Labels: 
                    i = x[1]
                    x = x[0]
                    #Labels[x] = label
                    fact = fact[i+1:]
                    return (fact, i)
                elif x: 
                    #label = label[len('Label:'):]
                    #label.strip()
                    if not fact[n] in Labels:
                    #Labels[fact[n]] = labelr
                        return True 
                
        else: return False 
            
        
    else: 
        #label = rule[len('Label:')+1:]
        #label.strip()
        if not fact[n] in Labels: 
            #Labels[fact] = label 
            return True 
            
        
    return True 

##############################################

def checkTtype(rule, fact, n):
    ''' Checks if item fact[n] follows the 
        token type specification
    '''
    
    z = len('Ttype:')
    ttype = rule[z:]
    ttype.strip()
    
    if ttype == 'n': #number 
        period = False 
        if fact[n][0] == '-':
            #negative number 
            test = fact[n][1:]
        else: 
            test = fact 
        
        for e in test: 
            if e == '.' and not period: 
                period = True 
            elif not e in string.digits: 
                return False 
            else: 
                continue 
        
        return True  
  
    elif ttype == 's':  #string
        
        if fact[n] == '\"': 
            str = '\"'
            n += 1
            while fact[n] != '\"':
                str += fact[n]
                str += ' '
                if n == len(fact): 
                    return False 
                else: 
                    n += 1
            str += '\"'
            
            return (str, n)
            
        else: 
            return False #not a string 
        
        
    elif ttype == 'w':  #word
        
        for e in fact[n]:
            if e in string.letters: 
                continue 
            elif e == '\'': 
                continue 
            else: 
                return False 
        return True 
        
    elif ttype == 'o':  #object
        
        if fact[n] in TypeHier.keys():
            return True 
        else: 
            return False 
            
    else: 
        return False
    
###################################################
def isTerminalSymbol(item):
    '''
    checks if item is  terminal symbol 
    (eg not in the grammar dictionary)
    '''
    if item in grammar_dict.keys():
        return False 
    else: 
        return True 

######################################################

def matchTerminalSymbol(symbol, fact, next_index, tree, rule, count):
    ''' Matches fact[next_index] with symbol
    '''
    
    if 'Type:' in symbol:
        typename = symbol.replace('Type: ', '')
        if isDescendant(fact[next_index], typename):
            next_index += 1
            
            return(tree, next_index)
            
    elif symbol.__class__ == list:
        x = checkLabel(symbol, fact, next_index)
        if x.__class__ == tuple:
            next_index = x[1] + 1
            tree.append([symbol, x[0]])
        elif x == True:
            tree.append([symbol, fact[next_index]])
            next_index+= 1
        else:
            return False 
        
        return(tree, next_index)
                
    elif 'Label:' in symbol:
        if checkLabel(symbol, fact, next_index):
            tree.append([symbol, [fact[next_index]]])
            next_index += 1
            
            return(tree, next_index)
                
    elif 'Ttype:' in symbol:
        x = checkTtype(symbol, fact, next_index)
        if x.__class__ == tuple:
            next_index = x[1] + 1
            tree.append([symbol, x[0]])
        elif x == True:
            next_index += 1
        else:
            return False
        
        return (tree, next_index)
        
    elif 'NUM' in symbol:
        for i in fact[next_index]:
            if i == '-':
                continue
            elif not i in string.digits:
                break
            elif i in string.digits:
                if i == fact[next_index][-1]: #the last digit in the string of digits 
                    tree.append([symbol, fact[next_index]])
                    next_index += 1
                    return(tree, next_index)
                  
    else:
        try: 
            if re.match(symbol, fact[next_index]):
                next_index+=1
                return(tree, next_index)
            else:
                return False 
        except: 
            if symbol == fact[next_index]:
                next_index += 1
                return (tree, next_index)
            else:
                return False
    
    
    return False  

######################################################

def parseRD_Facts(fact, start_sym, next, factFinished):
    ''' Recursive parsing function checking fact against vocabulary
    '''
    
    next_index = next
    
    if start_sym in grammar_dict.keys():
        rules = grammar_dict[start_sym]
        
        for r in rules:

            next_index = next
            tree = []
            tree.append([start_sym, r])
            
            if r.__class__ == list and len(r) > 1:
                count = 0  
                
                for token in r: 
                    count += 1
                    
                    #TERMINAL SYMBOLS 
                    if isTerminalSymbol(token):
                        termMatch = matchTerminalSymbol(token, fact, next_index, tree, r, count)
                        if not termMatch: #token didn't match, go to next rule 
                            break 
                        else:  #token matched 
                            tree, next_index = termMatch  #works because append to tree in the function, not just single entry
                            
                            if next_index == len(fact):  #have reached end of fact stream 
                                if count == len(r):   #end of rule tokens 
                                    factFinished = True
                                    return (tree, next_index, factFinished)
                                else:  #end of fact, not end of rule
                                    break #have reached end of input stream, but not end of rule -- BAD
                            
                            elif count == len(r): #end of rule, not end of fact 
                                factFinished = False
                                if entrypoint - 1 != 0: 
                                    return (tree, next_index, factFinished)
                                else: 
                                    break 
                                
                            else:   #continue through tokens in rule (not end fact, not end of rule) 
                                continue 
                                
                                
                    #NOT A TERMINAL SYMBOL--- will have to deal with 
                    else:
                        if token in grammar_dict.keys():
#                           
                            diveIn = parseRD_Facts(fact, token, next_index, factFinished)
                            
                            if diveIn: 
                                tree.extend(diveIn[0])
                                next_index = diveIn[1]
                                factFinished = diveIn[2]
                                
                                if factFinished: 
                                    return (tree, next_index, factFinished)
                                else:  #continue through remainder of rule, which may contain more tokens
                                    continue 
                            else: #didn't parse this nonterminal, need to go to next rule 
                                break 
                                
                        else: #not terminal, but also not in grammar dict... typo most likely 
                            break
                        
            else:  #ONLY 1 ITEM IN DEFINITON LIST-- SINGLE RULE TOKEN 
                ruleLen1 = r[0] 
                if isTerminalSymbol(ruleLen1): 
                    termMatch = matchTerminalSymbol(ruleLen1, fact, next_index, tree, r, count)
                    
                    if not termMatch:
                        break 
                    else: 
                        tree, next_index = termMatch 
                        if next_index == len(fact): #reached end of fact (obvi reached end of rule)
                            factFinished = True
                            return (tree, next_index, factFinished)
                        else: #only 1 token in rule, but also not end of fact... 
                            factFinished = False 
                            if entrypoint - 1 != 0:
                                return (tree, next_index, factFinished)
                            else: #so need to continue to the next rule 
                                continue 
                    
                    
                else:  #SINGLE RULE TOKEN, NONTERMINAL  (e.g. ['Phrase'])
                    
                    if ruleLen1 in grammar_dict.keys(): 
                        global entrypoint
                        entrypoint += 1
                        diveIn = parseRD_Facts(fact, ruleLen1, next_index, factFinished)
             
                        if diveIn: 
                            tree.extend(diveIn[0])
                            next_index = diveIn[1]
                            factFinished = diveIn[2] 
                        
                            if factFinished:
                                return(tree, next_index, factFinished)
                            else: #fact not finished, but this one single item is, go to next rule
                                continue 
                        else:  #didn't parse this nonterminal, need to go to next rule
                            continue  
                        
                    else: 
                        break 
                    
    return False


##########################################################


def input_typedef(fact):
    ''' Adds predefined rules with type definitions to type tree 
    '''
    
    paren1 = fact.index('[')
    paren2 = fact.index(']')
    if paren1 == -1 or paren2 == -1: 
        return 
    
    subj = string.join(fact[:paren1])

        
    if subj in TypeHier.keys():
        
        if TypeHier[subj][1] == 'ROOT':
            head = string.join(fact[paren1 + 1: paren2])    
            if head == '': #already a root 
                return
            elif head == subj: 
                return 
            else:  #DONT ADD TO TYPETREE/CHECK
                if head.find('disputed') != -1:
                    return 
                elif head.find('Disputed') != -1:
                    return
                elif head.find('debated') != -1: 
                    return
                elif head.find('Debated') != -1: 
                    return
                else: 
                    TypeHier[subj] = [False, head]
                    PossibleRootsToAdd.append(head)
                    return 
        else: 
            print >> sys.stderr, " \nMulti-Inheritance detected, Type \"%s\" is not included in the type tree.\n" % (subj, )
            return
    else: 
        
        head = string.join(fact[paren1 + 1: paren2])
        TypeHier[subj] = [False, head]
        PossibleRootsToAdd.append(head)
        return  subj
        
#############################################
def f_tracePath(subtype, mini):
    '''
    Traces the path of a given subtype to a root, 
    thus confirming if it is indeed linked to a properly defined root, 
    also has an internal check for LOOPS, using the mini dictionary d, to keep 
    track of items already detected in the path and returns false (blank path []) indicating so 
    '''
    path = []
    sub = subtype
    head = TypeHier[sub][1]
    d = mini
    
    if sub in d.keys():
        print >> sys.stderr, "Loop detected" + sub
        return [] #loop 
    
    elif head == 'ROOT':
        path = [sub]
        return path 
    
    elif head in TypeHier.keys():
        d[sub] = ''
        path = f_tracePath(head, d)
        
        if path == []:
            return []
        else: 
            path.append(sub)
            return path
            
    else: 
        return []
    

#################################################

def fcheck_types():
    ''' Checks types for loops and reachability to root 
    '''
    
#    print 'TYPEHIER BEFORE FCEHCK TYPES'
#    for ty in TypeHier.keys():
#        print ty + ':'
#        print TypeHier[ty]
        
    for poss in PossibleRootsToAdd: 
        if poss in TypeHier.keys(): 
            continue 
        else: 
            TypeHier[poss] = [True, 'ROOT']

    delList = []
    types = TypeHier.keys()
    
    for t1 in types:
        looptest = {}
        if not TypeHier[t1][0]:
            path = f_tracePath(t1, looptest)
            if path != []:
                for link in path: 
                    if TypeHier[link][0]:
                        continue 
                    else:
                        TypeHier[link][0] = True 
            else: 
                continue 
        else:
            continue 
        
    
    #if any type still has "False" entry, it means no proper
    # path was discovered to the root, thus meaning the type
    # was in some way improperly defined, and so we remove it 
    # from the tree
#    print 'TYPES THAT FAILED FCHECK'
    for t2 in types: 
        if not TypeHier[t2][0]:
            
#            print t2 + ':'
#            print TypeHier[t2]
            
            del TypeHier[t2]
            delList.append(t2)
        else:
            continue 

        
    return delList

#####################################################

def isPredef(fact):
    ''' Checks if fact is a predefined fact by the presence of ':' or 
        [, ], <-, or ->
    '''
    
    if fact[0] == ':':
        if '->' in fact:
             return True 
        elif '<-' in fact:
             return True 
        elif ('[' in fact) and (']' in fact):
             return True 
        else: 
            fact.remove(':')
            return False 
            
       
    elif '->' in fact:
         print >> sys.stderr, '\'->\' present in fact but no predefined marker \':\',\n user is advised to add it' 
         return True 
    elif '<-' in fact: 
        print >> sys.stderr, '\'<-\' present in fact but no predefined marker \':\', user is advised to add it' 
        return True 
    elif ('[' in fact) and (']' in fact): 
        print >> sys.stderr, '\'[]\' present in fact but no predefined marker \':\', user is advised to add it' 
        return True     
    else: 
        return False 

###################################################

def check_predef(f):
    '''
    grammar_dict['Predefined'] = [['Primary Term', '<-', 'Single Alias'],
                                  ['Primary Term', '<-', 'Multi Alias '], 
                                  ['Single Alias', '->', 'Primary Term'],
                                  ['Primary Term', '[', 'Type', ']']
                                  ]
    Type definitions are added to the type hierarchy and then checked for completeness.  
    Aliases are added to the two dictionaries, Aliases to Subj (mapping the alias to it's primary term) 
    and Subj to Aliases where the Subject/Primary term is mapped to all it's aliases.  It is important to note
    that while one entitiy (primaryterm) may have multiple aliases, a single alias may refer to only one entity. 
    '''
    
    predefs = grammar_dict['Predefined']
    
    for rule in predefs: 
        symb = rule[1]
        
        if symb in f: 
            i = f.index(symb)
            
            if symb == '[':
                subj = input_typedef(f)
                try:
                    s = subj.split()
                    if len(s) > 1: #MULTI WORDED SUBJECTTTT
                        l = f[0]
                        r = subj 
                        r = r.replace('.', '')
                        r = r.strip()
                        MultiAl.append(r)
                        AliasestoSubj[r] = l
                        break
                except:
                    break 
            
            elif 'Alias' in rule[0]:
                l  = f[:i][0]
                r = f[i+1:][0]
                AliasestoSubj[l] = r
                break
             
            elif 'Alias' in rule[2]:
                
                l  = f[:i][0]
                r = f[i+1:]
                if len(r) > 1 and  not 'Multi' in rule[2]:
                    continue
                elif len(r) > 1: 
                    r = ' '.join(r)
                    r = r.replace('.', '')
                    r = r.strip()
                    MultiAl.append(r)
                else: 
                    if r == []: break
                    r = r[0]
                    r = r.replace('.', '')
                    r = r.strip()
                    
                AliasestoSubj[r] = l     
               
                break
        else: 
            continue 
    
    return

###################################################### 
def first_pass(facts):
    '''
    The first pass pulls out predefined rules which contain information that will
    be needed before compleely going thru all facts.  Predefined rules include type definitions,
    as well as aliases, and so if a rule is of the predefined form, isPredef(fact) will return true, 
    and then the fact is  analyzed using the function CHECK_PREDEF(fact)    
    '''
    remFacts = []
    failed = []
    tokens = re.compile('(<-|->|:=|-=|\?<|:|;|\?:|>\?|.|\?|,|"|~>|=>>|<|>|[-_0-9a-zA-Z\']+|[+]|-|[*]|/|%|=|!=|<=|>=|=[[]|[\\\\][[]|[[]|[]]|[(]|[)]|!|&|[|]|[||]|&&|[\\\\$]|[\\\\]&|[\\\\\]@|[\\\\*]|[\\\\]|#)$')
    
    for f in facts: 
        
        f[1] = f[1].strip()
        f[1] = f[1].strip('.')
        f[1] = f[1].strip()
        
        subject = f[0]
        f, cit =  predpar.tokenize_pred_string(f[1], tokens)
        f.insert(0, subject)   
            
        if f == []:                              #failed to tokenize 
            failed.append(f)
                            
        #check if type def, check if predef --> only deal with those in first pass
        if isPredef(f):
            if ':' in f: 
                f.remove(':')
            check_predef(f)    
        else: 
            remFacts.append(f)
            continue 
    

        
    no_path = fcheck_types() 
    
        
    for n in no_path: 
        if n in TypeHier:
            del TypeHier[n]
    
    remFacts1 = []
    
    for r in remFacts: 
        factstr = string.join(r)
        for a in MultiAl:
            if factstr.find(a) != -1:
                a2 = a.split()
                try:
                    i = r.index(a2[0])
                    start = i
                    count = 1
                    end = -1 
                    while i != -1 and count < len(a2): 
                        try:
                            i = r.index(a2[count])
                            count += 1
                            if count == len(a2):
                                end = i
                        except: 
                            break
                    
                    if end == -1: 
                        continue 
                    else: 
                        
                        before = r[:start]
                        if end + 1 < len(r)-1:
                            after = r[end+1:]
                        else: 
                            after = r[end:]
                        newfacttoken = before + [a] + end 
                        r = newfacttoken 
                except: 
                    break  
                    
            else: 
                continue 
        remFacts1.append(r)

    
        
    print >> sys.stderr, 'DONE MULTIAL CHECK'   
#    return  remFacts1, failed #so when parsing thru rules, don't go thru the type definition again 
    return remFacts, failed
     
################################################
#def print_grammardict():
#      ##########PRINTING VOCAB DICTIONARY PRODUCED 
#    for x in grammar_dict:
#        print x + ":"
#        print x.__class__
#        for y in grammar_dict[x]:
#            print  y + ":"
#            for z in grammar_dict[x][y]:
#                print  z 
#        print '\n' 
    
########################################################################

#def print_endFacts(parsed, failed):
#    ##########PRINT STATMENTS 
#
#    print '\nPARSED FACTS'
#    print len(parsed)
#    for n in parsed:
#        print '\n'
#        for i in n:
#           print i
#    
#    print '\n FAILED FACTS: '
#    print len(failed)
#    for f in failed: 
#        print failed
#        print '\n'
     

####################################
    
def fact_checker():
    ''' 'main' function of this module. 
    '''
    vrules = []
    vfail = []
    global grammar_dict 
    grammar_dict = {}
    vdict = {}
    global TypeHier
    TypeHier = {}
    
    parsed_facts = []
    failed_facts = []
    facts2 = []
    
    
    vrules, vfail, vdict, TypeHier, grammar_dict  = check_vocab()
    
    if vrules == [] or grammar_dict == {}:
        sys.stderr.write("vocabulary failed to parse")
        return

    #print_grammardict()
    
    add_predef_rules()
    facts = go_thru_factFile()   
    
    facts2, failed_facts = first_pass(facts) #goes thru and analyzes predefined rules 
    print >> sys.stderr, 'END FIRST PASS FCHECK'
    
#    print 'TYPE TREE'        
#    for x in TypeHier.keys(): 
#        print x + ":"
#        print TypeHier[x]
    
    successfn = '_fcheck_succparsed2_'
    failedfn = '_fcheck_failparsed2_'
    
    successf = open(successfn, 'w')
    failedf = open(failedfn, 'w')
    
    for f2 in facts2:
        global depth
        depth = 0 
        global entrypoint
        entrypoint = 0 

#        factParse = parse_Facts(f2, 'Start', grammar_dict)
        factParse = parseRD_Facts(f2, 'Start', 0, False)
        if factParse: 
            parsed_facts.append([f2, factParse])
            writestr = str(f2) + ':\n' + str(factParse)
            successf.write(writestr)
            successf.write('\n\n')
        else: 
            failed_facts.append(f2)
            writestr = str(f2)
            failedf.write(writestr)
            failedf.write('\n')
    
    successf.close()
    failedf.close() 
#    print_endFacts(parsed_facts, failed_facts)
    
    return [parsed_facts, failed_facts] 
     



if __name__ == '__main__':
    fact_checker()


