#!/usr/bin/python
# vi: ts=4 sw=4 et ai sm
# mkvocab Program for reading Factotum 90 data and creating a vocabulary.
# Written by Buz on 2010-11-18
# partially finished on 2010-11-24

# This is working as far as it goes.
# It needs to be split up and modularized.

import os, sys, time, md5, glob
import cPickle as pickle
from getopt import *
from string import *

true    = 1
false   = 0
debug   = false


factd  = 'X:/Factotum/Factotum 3G/'
factv  = 'photo.v'
factf  = 'photo.f'
factfx = 'photo.fx'

markers = ( ':"', ':[', ':', '*', ':*', '#*', '#"', ':<', '"', '#', ' ')
unique_num = 0
current_subject = ''

entities = {}     # Dict of entitites where each is a list of 7-tuples:
                  #  ( info-type, subject, predicate, head, remarks, cits )
                  #  The info types are:
                  #      T: Type
                  #      A: Alias
                  #      a: Reverse Alias
                  #      R: Remark
                  #      C: Citation information about Entities
                  #      F: A Fact about the other entities
                  
types = {}        # Dict info about organization and uses of types
                  # ent: list of entities of this type
                  # rel: list of relations used for this type
                  # res: list of restrictions to apply to this type
                  # par: father type of this type
                  # sib: list of child types of this type
                  # div: list of type-parts that go to make up this type
                  # rem: remarks about the type (e.g. informal definition)
                  
relations = {}    # info about predicate relations syntax and semantics
                  # Dict of relations where each is a list of tuples"
                  # The key is always an unique_name and the contents
                  # are always a unique parse pattern.
                  # The common_name may not be unique if several parse
                  # patterns represent the same relation.
                  # ( common_name, [( repr, type )...]
                  # The list always starts with the tuple ( '<>', 'E' )
                  # which represents the subject entity.
                  # The type info is currently limited to:
                  #      E: An entity
                  #      V: A value
                  #      R: A relation literal token
                  # Additional ones need to be added:
                  #      S: A subject
                  #      P: A sub-rule predicate part

# Two dictionarys that 'organize' the relations dictionary in different ways

rel_keys = {}     # The key is a summary of the keywords in the relaion
                  # The value is a list of relation names that might parse
                  # the relation. This is used to check input to find a
                  # matching relation.  Partial keys could be used as well.

rel_tags = {}     # The relation patterns that impliment this relation
                  # So the key 'died' could point a several relations that
                  #        specify that.
                  # Likewise the key 'dead' could point to the same relations.
#
#
#                          Dictionary: relations
# Dictionary
#  rel_keys                           name     syntax pattern
# 'death :' +------> $$0027:( 'dead', [ (,), (,) ... ] )
#           |
#           +------> $$0032:( 'dead', [ (,), (,) ... ] )
#           |
#           +------> $$0007:( 'dead', [ (,), (,) ... ] )
#           |
#           +------> $$0095:( 'dead', [ (,), (,) ... ] )
#
# 'birth :' +------> $$0023:( 'alive',[ (,), (,) ... ] )
#           |
#           +------> $$0065:( 'c1',   [ (,), (,) ... ] )
#
# In addition there also might be an entry that looked like this:
#
# 'birth'   +------> $$0023:( 'alive',[ (,), (,) ... ] )
#           |
#           +------> $$0065:( 'c1',   [ (,), (,) ... ] )
#
#=================================================================
#
# Dictionary
#  rel_tags                          name      syntax pattern
# 'death'   +------> $$0108:( 'death', [ (,), (,) ... ] )
#           |
#           +------> $$0055:( 'x1',    [ (,), (,) ... ] )
#           |
#           +------> $$0007:( 'death', [ (,), (,) ... ] )  # not a mistake
#           |
#           +------> $$0195:( 'death', [ (,), (,) ... ] )
#
# 'birth:'  +------> $$0023:( 'alive', [ (,), (,) ... ] )  # This is not a
#           |                                              # mistake either
#           +------> $$0065:( 'c1',    [ (,), (,) ... ] )  # in fact all
#                                                          # rel_tags look
#           like their corresponding rel_keys when mkvocab finishes its work.
#           However when a user starts editing his vocabulary he can group
#           diverse syntax patterns under the same name.  At that point all
#           bets are off.  In fact the rel_tag dictionary may well get more
#           complicated.

# Sorry about all the comments but this is pretty complicated and I just want to# be able to understand it when I get back to it in a couple of years.

#-------------------------------------------

def lex_string( p ):

    # Returns a list of tuples: (token, ttype).
    # ttype   indicates
    #  W      word only: letters/numbers/dash/underbar
    #  N      number only: numbers/plus/minus/period
    #  P      punctuation: single char or backslash + char
    #  "      string: can include \" characters
    #  <      an angle bracket phrase \< ... >
    #  {      a brace phrase          \{ ... }
    #  [      a square bracket phrase (these should never occur in predicates)
    #         but they do occur in citations, so they are a part of this.
    #                                 \[ ... ]
    #  (      a parenthesized phrase  \( ... )

    # whitespace between tokens is discarded.

    # grouping token control to allow \{ ... } within brace groups
    depth  = 0
   
    # tokens and token types
    tokens = []       # contains tuples (token,token-type)
    ttype  = ' '      # blank indcates we are between tokens in white space
    token  = ''
    words   = 'a9_-'
    numbers = '9-.'

    cp = 0
    p = strip(p)
    plen = len(p)
    token_done = false
    # print 'lexing: >' + p + '< plen:', plen
    
    esym = ''
    
    while cp < plen:
        
        c = p[cp]
        try:
            n = p[cp+1]
        except:
            n = ' '
        # print 'cp =', `cp`, c + n
        dc = false
        ctype = 'x'        
        
        # Note only one token grouping is active at any one time.
        # So strings can have \<...> groupings inside them with no effect
        # likewise \<...> can have strings inside with no tokenization.

        # handle token groups: strings, angle brackets, etc.
        # depth depends on not have more than one grouping active.
        if   c == '"'  and not depth:
            depth += 1; ttype = '"'; esym = '"'        
        elif c == '\\' and n == '<' and not depth:
            depth += 1; ttype = '<'; esym = '>'; dc = true
        elif c == '\\' and n == '[' and not depth:
            depth += 1; ttype = '['; esym = ']'; dc = true
        elif c == '\\' and n == '{' and not depth:
            depth += 1; ttype = '{'; esym = '}'; dc = true
        elif c == '\\' and n == '(' and not depth:
            depth += 1; ttype = '('; esym = ')'; dc = true
        elif c == esym and depth:
            depth -= 1;
            if not depth:
                token_done = true
                token += c
                cp += 1
                ctype = 'x'
        # handle special chars: \" in strings
        elif c == '\\' and n == '"' and ttype == '"': dc = true
        # handle special chars: \c in any other context
        elif c == '\\' and not depth: token_done = true; dc = true

        # charcterize this character
        elif c in digits:     ctype = '9'
        elif c in letters:    ctype = 'a'
        elif c in whitespace: ctype = 'w'
        elif c == '+':        ctype = '+'
        elif c == '_':        ctype = '_'
        elif c == '-':        ctype = '-'
        elif c == '.':        ctype = '.'
        else: ctype = 'p'

        # print 'ctype is ', ctype, 'token:', token, 'ttype = >' + ttype + '<'

        # now decide on token type based on first char of token
        if ttype == ' ': # group tokens are started above
                         # this only handles single tokens
            if   ctype == 'w': cp += 1; token_done = true
            elif ctype == 'a': ttype = 'W'
            elif ctype == '9' or \
                 ctype == '-': ttype = 'N'
            else: # What's left should be single character tokens
                token += c
                cp += 1
                if dc:
                    token += m
                    cp += 1
                ttype = 'P'
                ctype = 'w'
                token_done = true

        # now decide if token has finished with a non-permissible char
        if   ttype == 'N' and ctype not in numbers: token_done = true
        elif ttype == 'W' and ctype not in words:   token_done = true
                
        # print 'at', cp, 'ctype/ttype is >' + ctype + ttype + '<', \
        #       token_done, 'token:', token
        
        # here is where all the action is
        if token_done:
            if token:
                tokens.append( (token,ttype) )
            token_done = false
            ttype = ' '
            token = ''
            ctype = 'x'
        else:
            # Gather characters into the token
            token += c;
            cp += 1
            if dc: 
                token += n;
                cp += 1
            
    tokens.append( (token,ttype) )
    return tokens


#-------------------------------------------

def unlex( lex ):
    #print 'unlex of', `lex`,
    str = ''
    if len(lex) <= 1: str += lex[0][0]
    else:   
        for i in lex[:-1]:
            # i[0] is the token; i[1] is the type
            str += i[0] + ' '
        str += lex[-1][0]
    #print 'is', str
    return str

#-------------------------------------------
    

def lex_fact( f ):
    # breaks up fact into marker, subject, predicate, remarks, and citations.
    # Returns 5-tuple (m,s,p,r,c)
    global current_subject
    # print "fact is ", f
    m = s = p = r = c = ''
    cp = 0
    # Look for markers if none then marker will be blank
    for pm in markers:
        cp = len(pm)
        # print 'test >' + f[:cp] + '< against >' + pm +'<'
        if f[:cp] == pm:
            m = pm
            f = f[cp:]
            break
    
    # print 'marker is', m
        
    # if marker implies subject then fill in subject field
    mlen = len(m)
    if m == "*" or m == ':*' or m == '#*':
        s = unique_name()
        f = f[mlen:]
        # print "set subject to ", s
    elif m == '"' or m == ':"' or m == '#' or m == '#"' or m == ':[':
        s = current_subject
        f = f[mlen:]
        # print "set subject to ", s
    elif m == ':<':
        s = '\\include'
        f = f[mlen:]
        # print "set subject to ", s
    else: 
        #print 'subject left unchanged.'
        pass

    # print "fact is ", f
    # if s != '': print "subject is ", s
    f = expandtabs(f,4)

    # get citations
    # find \[ marking start of citations
    cb = rfind( f, '\\[' )
    if cb >= 0:
        c = strip(f[cb:])
        f = f[:cb]
        # print "citations are ", c

    if m == '#' or m == '#"':        
        # print 'return remark'
        return(m, current_subject, '', [], strip(f), c )

    # get remarks
    # find \# marking start of remarks
    rb = rfind( f, '\\#' )
    if rb >= 0:
        r = strip(f[rb+2:])   # Remove \# from the fact.
        f = strip(f[:rb])
        # print "remark is ", r

    # Get plausible subject from fact
    if s == '':
        # print "pick up subject from >" + f + "<"
        sf = split( f )
        # print `len(sf)`, `sf`
        if len(sf):
            se = len(sf[0])
            if se > 0:
                s = f[:se]
                f = f[se:]
                # print "set subject to", s
        else:
            # print "Whitespace not found."
            pass
                            
    # Get plausible predicate from fact
    p = f;
    px = lex_string(f) # set predicate

    if s != '':
        current_subject = s
    else:
        s = current_subject = unique_name()

    # print 'subject is', s
    # print 'predicate is', unlex(px)
    return ( m, s, p, px, r, c )

#-------------------------------------------

def usage():
    print ""
    print "mkvocab [options] file"
    print "will open file.f in the same directory as file."
    print "If file.v is newer than file.f and then the program"
    print "issues a warning and does nothing."
    print ""
    print "Options:"
    print "--help  Help -- provides this summary."
    print "-h      Help -- provides this summary."
    print "-v      Make vocabulary, default is to list vocabulary as output"
    print "-q      No std-output produced."
    return

#----------------------------------------------------------

def create_fx( ):

    return
#----------------------------------------------------------

def unique_name():
    global unique_num
    unique_num += 1
    return( '$$' + ( '%08d' % unique_num ) )

#----------------------------------------------------------
#   Create Entity facts
#----------------------------------------------------------

def enter_alias( m, s, a, px, r, c):
    global entities
    if not s: s = current_subject
    if not a: print "error in " + s + ": alias empty."
    if a not in entities:
        entities[a] = []
        entities[a].append(['A', m,  a, s, [], r, c])
    if s not in entities:
        entities[s] = []
        entities[s].append(['a', '', s, a, [], r, c])
    return

#----------------------------------------------------------

def enter_cits( m, s, p, px, r, c):
    global entities
    if not s: s = current_subject
    if s not in entities:
        entities[s] = [] 
    entities[s].append(["C", m, s, '', [], r, c])
    return

#----------------------------------------------------------

def enter_remarks( m, s, p, px, r, c):
    global entities
    if not s: s = current_subject
    if s not in entities:
        entities[s] = [] 
    entities[s].append(["R", m, s, p, [], r, c])
    return
#----------------------------------------------------------

def enter_fact( m, s, p, px, r, c):
    global entities
    if not s: s = current_subject
    if s not in entities:
        entities[s] = [] 
    entities[s].append(["F", m, s, p, px, r, c])
    return

#----------------------------------------------------------

def enter_type( m, s, t, px, r, c):
    global entities
    if not s: s = current_subject
    if s not in entities:
        entities[s] = []
    entities[s].append(["T", m, s, t, [], r, c])
    return

#----------------------------------------------------------

def enter_syntax( vtag, vlist ):
    global relations, rel_keys, rel_tags
    # print "Enter Syntax:", k, `v`
    
    # Loop to find an exact matching relation
    n = 0
    found = false

    if vtag in rel_keys:
        for r in rel_keys[vtag]: # We are looking for an exact relation match
            if vlist == relations[r][1]:
                found = true
                return
        
    # if found, r is the basic relation name it will be a unique name
    # and we can forget it since it is already a recorded relation.
    # So at this point we have a new vtag, vlist pattern

    cname = replace( vtag, ' ', '')

    # create the low-level relation vocabulary
    
    s = unique_name()
    relations[s] = ( cname, vlist )

    # Enter the key in rel_keys as a pattern or alternative pattern:
    # ... exact matches disappered in the search loop.

    if vtag not in rel_keys:
        rel_keys[vtag] = []
    rel_keys[vtag].append(s)
        
    # Enter the cname in rel_tags as a relation:
    # this will alias together patterns with the same key words
    # and different patterns of entities and values.
    
    if cname not in rel_tags:
        rel_tags[cname] = []
    rel_tags[cname].append(s)

    return

#----------------------------------------------------------

def set_type_info( t, field, val):
    global types
    lists = ( 'ent', 're', 'res', 'par', 'sib', 'rem' )
    if t not in types:
        types[t] = {}          # create a named type dict in the types dict
        types[t]['ent'] = []   # entities that belong to this type
        types[t]['rel'] = []   # relations used in entities of this type
        types[t]['res'] = []   # restriction applied to this type
        types[t]['par'] = ''   # It's a tree only one father
        types[t]['sib'] = []   # It's a tree multiple sons
        types[t]['div'] = []   # It's an object divided into independent parts
        types[t]['rem'] = []   # Remarks about this type (informal def.)
    if field in lists:
        types[t][field].append( val )
    elif field == 'par':
        if   types[t]['par'] == val: return
        elif types[t]['par'] == []:  types[t]['par'] = val
        else: 
            print 'replacing previous parent of type %s ( %s ) by %s' %\
                ( t, types[t]['par'], val )
            types[t]['par'] = val        
    return

#----------------------------------------------------------

def set_relations( px ):

    # set relations takes a parsed predicate
    # It attempts to separate elements of the predicate into
    # relation-words, entity-references, and values.
    # Without clues as to what strings are values this is highly error prone
    # The user can clue in the program as to what is a value by using \( ... )
    # The program will try to fix up results later.
        
    vlist = []
    iw = 0
    tlist = len(px)
    # print 'starting with:', `px`
    vlist.append( ('<>','E') )  # put in subject Entity
    while iw < tlist:
        w, t = px[iw]
        wt = w
        found = false
        if  t == 'W':
            nwds = 1
            while true:
                # print 'is %s an entity name?' % wt,                                
                if wt in entities: # Eliminate known entity references
                    vlist.append( ['<>', 'E'] )
                    found = true
                    iw += nwds
                    # print '  yes!'
                    break                
                # print '   no!'                
                # This loop tests an enlarging sequence of up to 3 words
                # as an entity name.  It terminates when it encounters
                # a non word, or the end of the predicate
                if nwds > 3 or (iw+nwds) >= tlist-1: break                
                nxt, t = px[iw+nwds]                
                if t != 'W': break
                # Enlarge the potential entity name.
                wt += ' ' + nxt
                # print 'next test is', wt
                nwds += 1
                
            if not found:
                vlist.append( [w, 'R'] )
     
        else:
            vt = 'X'
            if   t == 'P': vt = 'R'
            elif t == 'W': vt = 'R'
            elif t == 'N': vt = 'V'
            elif t == '{': vt = 'V'
            elif t == '[': vt = 'C'
            elif t == '(': vt = 'V'
            elif t == '<': vt = 'E'
            elif t == '"': vt = 'V'
            elif t == 'w': vt = ' '
            
            if   vt == ' ': pass
            elif vt == 'R': vlist.append( ( w,   vt ) )
            elif vt == 'V': vlist.append( ( '()',vt ) )
            elif vt == 'C': vlist.append( ( w,   vt ) )
            elif vt == 'E': vlist.append( ( '<>',vt ) )
            else :
                if w: vlist.append( ('!'+w+'!',vt) )
        # Advance through the entire predicate building up vlist
        iw += 1
        
                                    
    vtag = unlex( vlist )
    vtag = replace( vtag, '<>', ' ' )
    vtag = replace( vtag, '()', ' ' )
    vtag_list = split(vtag)
    vtag = join(vtag_list)
    # print "vtag is", vtag
    enter_syntax( vtag, vlist )
        
    return

#----------------------------------------------------------
#         Main Program
#----------------------------------------------------------


def main():
    global factf, factv, factfx
    global entities, relations, rel_keys, rel_tags
    # Process command line options

    try:
        opts, args = getopt(sys.argv[1:], "hvVqf:v:",\
                ["help", "facts=", "vocab="])
    except GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if   o == "-q": verbose = false
        elif o == "-v": verbose = true
        elif o == "-V": verbose = false      
        elif o in ("-f", "--facts"):
            factbase = a
            if a:
                logdir = "./"
            else:
                (logdir,factn) = os.path.split(a)
                factf = factn + ".f"
                factv = factn + ".v"
                factfx = factn + ".fx"
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        else: assert False, "unhandled option"

    text  = []
    stats = {}
 
    # Put fact data structure entities directory.
    
    if os.path.exists( factd + factfx ):
        # check to see if it is newer than the input files
        # exit if it is.
        pass

    # Pass 1 -- Do names: pickup entity names and aliases.
    # Build up Entity data base, from users fact file.
    # Users fact file never read again after this.
    a = m = s = p = r = c = ' '
    px = []  # This is the predicate pre-lexed in (token,type) tuples
    
    ff = file( factd + factf, 'r' )
    afact = ''
    current_subject = unique_name()   # create a current subject
   
    next_line = ''
    next_line = ff.readline()         # set up first line.
    # print '1st line >' + next_line + '<'
    # print 'subject is:', current_subject
    
    while len(next_line) > 0:
        afact = next_line[:-1]
        next_line = ''
        next_line = ff.readline()
                       
        # Group together continuation lines.
                   
        while (len(next_line) > 0) and (next_line[0] == '-'):
            afact += '\n' + next_line[1:-1]
            next_line = ''
            next_line = ff.readline()
            continue

        # print 'working on >' + afact + '<'
        if strip( afact ) == "": continue

        (m,s,p,px,r,c) = lex_fact( afact )
        p = strip(p)

        # Fix subject and get rid of \< > subjects
        if s[0:2] == "\<":       # then a multi-word subject
            se = find( p, '>' )  # look for end of subject
            if se > 0:           # End of subject found; adjust predicate
                a = s[2:] + ' ' + p[:se-1]
                p = strip( p[se:] )
                # px = lex_string( px )
                s = unique_name()
                enter_alias( m, s, a, [], [], r, c )
            else:
                s = s[2:]

        if m == '#' or m == '#"':   # Then it is a remark
            enter_remarks( m, s, p, px, r, c )
            continue

        elif m ==  ':<':       # Then it is an include
            # do the include thing
            continue

        elif m[0] == ':':
            # process the alias
            if p[:2] == '<-':    # normal alias definition
                a = strip( p[2:] )
                enter_alias( m, s, a, '', [], r, c )
            elif p[:2] == '->':  # reverse alias definition
                a = s
                s = strip( p[2:] )
                enter_alias( m, a, s, [], r, c )
            elif p[:1] == '<':   # type association
                te = find( p, '>' ) # end of type name
                if te > 0:
                    t = strip(p[1:te])
                else:
                    print 'Type has no ending >'
                    t = strip(p[1:])
                enter_type( m, s, t, [], r, c )
            elif m == ":[":       # entity citations
                ec = rfind( p, ']' )
                if ec > 0: p = p[0:ec]
                enter_cits( m, s, '', [], r, p )
            continue

        else:
            enter_fact( m, s, p, px, r, c )       

    ff.close()

    e_tags = entities.keys()
    e_tags.sort()

    print( '\nEntities are:' )
    for e in e_tags:
        print "    "+e
        for i in entities[e]:
            it = i[0]
            if   it == 'T': print "        Type is", i[3], i[5]
            elif it == 'R': print "        #", i[5]
            elif it == 'A': print "        Alias for", i[3], i[5]
            elif it == 'a': print "        Alias for", i[3], i[5]
            elif it == 'C': print "        Citations", i[6]
            elif it == 'F':
                if i[5]:    print "       ", i[3], '#', i[5]
                else:       print "       ", i[3]
            else:           print "      ", `i`
        print ''
        


    # Pass 2 -- break predicates into objects, relations, and values.
    # create a vocabulary.
    
    # Establish type information

    for e in entities:
        for item in entities[e]:
            it = item[0]
            if   it == 'T': set_type_info( item[3], 'ent', e )

    # Report type information

    print "Types used:"

    tlist = types.keys()
    tlist.sort()
    
    for t in tlist:
        print ''
        print '    ' + t
        for et in types[t]:
            if et == 'par': continue
            elif et == 'ent':                
                print '    Entities:',
                itlist = types[t]['ent'] # get entity names
                itlist.sort()            # sort entity names
                n = 0
                for it in itlist[:-1]:   # format lines
                    if n != 0 and (n % 5) == 0: print "\n      ",
                    print it + ", ",
                    n += 1                    
                print itlist[-1]           # print last one with new-line
                
                
            else:
                if types[t][et] != []:
                    print "    " + et, `types[t][et]`

    # Process predicate information

    for e in entities:
        for item in entities[e]:
            it = item[0]
            if it == 'F':
                set_relations( item[4] )


    # Report Relation information
    
    print '\nAbstract Relations:'
    print ''

#-------------------

    r_tags = relations.keys()
    r_tags.sort()
    
    print "\nRelations Table:"
    print ''
    for rt in r_tags:
        if len( relations[rt][1] ) > 5:
            print "   ", rt, relations[rt][0], unlex(relations[rt][1][:5]), "..."
        else:
            print "   ", rt, relations[rt][0], unlex(relations[rt][1])

#--------------------

    r_keys = rel_keys.keys()
    r_keys.sort()
        
    print "\nRelation Key Table:"
    print ''
    
    for rk in r_keys:
        label = rk
        for i in rel_keys[rk]:
            x, rv = relations[i]       
            if len(label) > 15:
                print "    " + label, "-->"
                print "        " + unlex(rv)
            else:
                print "    %-15s" % (label,),
                print "-->", unlex(rv)
            label = ""
        
#-------------------
    
    r_tags = rel_tags.keys()
    r_tags.sort()
    
    print "\nRelation Tag Table:"
    print ''
    for r in r_tags:
        rn, rv = relations[ rel_tags[r][0] ]
        if len(rn) > 15:
            print "    " + rn, "-->"
            print "        " + unlex(rv)
        else:
            print "    %-15s" % (rn,),
            print "-->", unlex(rv)

#-------------------
    return

    sys.exit(0)

if __name__ == "__main__":
    main()
