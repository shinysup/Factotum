#!/usr/bin/python
# vi: ts=4 sw=4 et ai sm

false = 0
true  = 1
from string import *

# This module handles type information about entities

class TypesClass:

    # Establish type information

                  
	types = {}    # Dict info about organization and uses of types
                  # ent: list of entities of this type
                  # rel: list of relations used for this type
                  # res: list of restrictions to apply to this type
                  # par: father type of this type
                  # sib: list of child types of this type
                  # div: list of type-parts that go to make up this type
                  # rem: remarks about the type (e.g. informal definition)
                  
#----------------------------------------------------------
 
def __init__(self,parent=None):
	self.parent = parent
	return
        
#----------------------------------------------------------

def set_type_info( self, t, field, val):
	lists = ( 'ent', 're', 'res', 'sib', 'rem' )
	if t not in self.types:
        	self.types[t] = {}          # create a named type dict in the types dict
        	self.types[t]['ent'] = []   # entities that belong to this type
        	self.types[t]['rel'] = []   # relations used in entities of this type
        	self.types[t]['res'] = []   # restriction applied to this type
        	self.types[t]['par'] = ''   # It's a tree only one father
        	self.types[t]['sib'] = []   # It's a tree multiple sons
        	self.types[t]['div'] = []   # It's an object divided into independent parts
        	self.types[t]['rem'] = []   # Remarks about this type (informal def.)
	if field in lists:
        	self.types[t][field].append( val )
	elif field == 'par':
		if   self.types[t]['par'] == val: return
		elif self.types[t]['par'] == []:  self.types[t]['par'] = val
		else: 
                	print('replacing previous parent of type %s ( %s ) by %s' %\
                		( t, self.types[t]['par'], val ))
                	self.types[t]['par'] = val        
	return
        
#---------------------------------------------------------- 
   
def establish_types( self, ent ): 
    # This does a pass through the entities in ent and creates a  types directory
    # for everthing that is found.
   	#print 'establish_types\n' 
	for et in ent:
	    #print 'et: '+ str(et)+'\n'
		for item in ent[et]:
		#print 'item: ' + str(et)+'\n'
			it = item[0]
		#print 'it: ' + str(it) + '\n'
			if it == 'T':
                        	print('Set Type Info for:' + str(item[3]))
		    #print "item[1] is:", item[1]
	  	    #print "item[2] is:", item[2]
                        	self.set_type_info( item[3], 'ent', et )
			if it == 'R':
		    		item[3]=str(item[3]).strip('#')
		    		print('Type Restrictions for ' + str(item[2]) + ': ' + item[3])
		    		self.set_type_info( item[2], 'res', item[3] )
			if it == 'P':
		    		item[3]=str(item[3]).strip('>>')
		    		print('Type ' + str(item[2]) + ' Has Parent: ' + item[3])
		    		self.set_type_info( item[2], 'par', item[3])
	return
        
#----------------------------------------------------------

def entity( self, etag ):   # Return list of types for entity
	if etag not in e.entities:
		return None
	tlist = []
	for item in e.entities[etag]:
		it = item[0]
		if it == 'T':
			tlist.append(item[3])
	print("Entity", etag, "has types.", repr(tlist))
	return tlist
                                              
#----------------------------------------------------------                    

def entities( self, typ ):   # Return list of entities that have this type 
        if typ not in self.types:
        	return None
        return self.types[typ]['ent']
        
#----------------------------------------------------------                    

def show( self, typ ):   #  Print collected information about a type
        if typ not in self.types:
            	print(typ, "unknown")
            	return
        for t in types[t]:
            	if t == []: continue
            	print('%-10s' % t, end=' ')
            	for i in types[t]:
                	print(i, end=' ')
        return
        
#----------------------------------------------------------

def show_all( self ):   #  Print all collected information about all types
        tlist = list(self.types.keys())
        tlist.sort(key=str.lower)
        for typ in tlist:
        	self.show( typ )
        return
            
#----------------------------------------------------------  

def show_all_entities( self ):   #  Print types with lists of entities
     
    # Report type information

	tlist = list(self.types.keys())
	tlist.sort(key=str.lower)
        
	for t in tlist:
		print('')
		print('t: ' + t)
		for et in self.types[t]:
			if et == 'par': continue
			elif et == 'ent':                
				print('Entities:', end=' ')
				itlist = self.types[t]['ent'] # get entity names
				itlist.sort()            # sort entity names
				n = 0
				for it in itlist[:-1]:   # format lines
                        		if n != 0 and (n % 5) == 0: print("\n      ", end=' ')
                        		print(it + ", ", end=' ')
                        		n += 1
				if len(itlist):                     
                    			print(itlist[-1])           # print last one with new-line
                    
                    
			else:
				if self.types[t][et] != []:
					print("    " + et, repr(self.types[t][et]))
                        
	return
