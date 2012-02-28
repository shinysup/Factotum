import os, sys, time, glob
from getopt import *
from string import *
import factotum_lex
import factotum_entities
import factotum_relations
import factotum_types
import factotum_globals

curType=''
ent = factotum_entities.EntityClass()
typeDict = {}
subject=''
type=''

def readVocab(): #read __.v file and put them in typeDict
	typeLine = 'Type is'
	entityStart = 'Entities:'
	entityEnd= 'Abstract Relations:'
	parLine='Has Parent: '
	resLine='Type Restrictions for'
	append=False
	for line in open('test.v').readlines():
		if typeLine in line:
			append=False
			curType= line.strip(typeLine)
			curType = ''.join(c for c in curType if c.isalnum())
			curType = curType.strip('\n')
			typeDict[curType] = {}
			typeDict[curType]['entity'] = {}
			typeDict[curType]['parent'] = {}
			typeDict[curType]['restriction']=[]
		elif parLine in line:
			line = line.split()
			curType = str(line[1])
			curType = ''.join(c for c in curType if c.isalnum())
			#typPar = typPar.strip('\n')
			typPar = str(line[4])	
			typeDict[curType]['parent']=typPar
			typeDict[typPar] = {}
			typeDict[typPar]['entity']={}
			typeDict[typPar]['parent']={}
			typeDict[typPar]['restriction']=[]
		elif resLine in line:
			line = line.split()
			curType = str(line[3])
			curType = ''.join(c for c in curType if c.isalnum())
			#typRes = typRes.strip('\n')
			typRes = str(line[4])
			typeDict[curType]['restriction'].append(typRes)
		elif line.startswith('t: '):
			curType = line[3:]
			curType = ''.join(c for c in curType if c.isalnum())
			curType = curType.strip('\n')
		elif line.startswith(entityStart):
			data = line[len(entityStart):]
			data = ''.join(c for c in data if c.isalnum() or c.isspace())
			data = data.strip('\n')
			data = data.split()
			for et in data:
				#typeDict[curType]['entity']=et
				typeDict[curType]['entity'][et]={}
				typeDict[curType]['entity'][et]['relations']=[]
				typeDict[curType]['entity'][et]['parameters']={}
				typeDict[curType]['entity'][et]['alias']=[]
			append=True
		elif line.startswith(entityEnd):
			append=False
			break
		elif append:
			if line == '\n':
				append=False
			else:
				line = ''.join(c for c in line if c.isalnum() or c.isspace())
				line.strip('\n')
				line.split()
				typeDict[curtype]['entity'][et]={}
				typeDict[curtype]['entity'][et]['reltaions']=[]
				typeDict[curtype]['entity'][et]['alias']=[]

def collectRelations():
	start='Type is'
	collect=False
	entities=[]
	currentEnt=''
	currentTyp=''
	for ty in typeDict.keys():
		for e in typeDict[ty]['entity'].keys():
			entities.append(e)

	for line in open('test.v').readlines():
		if ''.join(c for c in line if c.isalnum()):
			temp = line.split()
			if temp:
				temp = str(temp[0])		
				if temp in entities:
					currentEnt = temp
		if not ''.join(c for c in line if c.isalnum()):
			collect=False
		if collect:
			line = ''.join(c for c in line if c.isalnum())
			if line:
				if hasNumeric(line):
					val = returnNumeric(line)
					line=line.replace(val,'()')
					typeDict[currentTyp]['entity'][currentEnt]['parameters'][line]=val
				else:
					typeDict[currentTyp]['entity'][currentEnt]['relations'].append(line)
				
		if start in line:
			collect=True
			temp=line.split()
			temp=str(temp[2])
			currentTyp=temp

def updateDict():#update new entity information for its type parents 
	for t in typeDict:
		if typeDict[t]['parent']:
			par = typeDict[t]['parent']
			for e in typeDict[t]['entity']:
				if e not in typeDict[par]['entity']:
					typeDict[par]['entity'][e]={}
					typeDict[par]['entity'][e]['relations']=[]
					typeDict[par]['entity'][e]['parameters']={}
					typeDict[par]['entity'][e]['alias']=[]

def getTypeOf(ent): #return type of entity
	for t in typeDict:
		if ent in typeDict[t]['entity']:
			return t

def hasNumeric(r):
	l=list(r)
	for c in l:
		if c.isdigit():
			return True
		else:
			continue
	return False

def returnNumeric(r): #returns the numeric parts within string
	l=list(r)
	numLs = []
	numStr = ''
	numStart = False
	for c in l:
		if c.isdigit():
			numStr = numStr + c
			numStart = True
		elif numStart:
			numLs.append(numStr)
			numStr=''
			numStart =False
			continue	
		else:
			continue
	if numStart:
		numLs.append(numStr)
	return numLs


def validateNewFact():
	done =  False
	subject=''
	relationValid = True
	while(not done):
		subEntered=False
		typEntered=False
		parEntered=False
		resEntered=False
		prompt='Enter a fact to validate:\n'
		prompt=prompt+'Enter ; if done\n'
		fact = raw_input(prompt)
		if ';' in fact:
			done=True
			break
		splitfact = fact.split()
		if '[' not in str(splitfact[0]): #first token is not type => it's subject
			subject = str(splitfact[0])
			subEntered=True
			type=getTypeOf(subject)
		
		if subject: 
			if '[[' not in str(splitfact) and ']]' not in str(splitfact) and '>>' not in str(splitfact) and '#' not in str(splitfact):
				#rest of the fact (excluding subject) is a relation
				if type in typeDict.keys(): #add relations only when subject is of valid type
					relation=''
					for tk in splitfact:
						if not str(tk)==subject:
							relation = relation+str(tk)
					relation = ''.join(c for c in relation if c.isalnum())
					num=''
					if relation not in typeDict[type]['entity'][subject]['relations']:
						if hasNumeric(relation): #parameters with values
							nums = returnNumeric(relation)
							parameter = relation
							for n in nums:
								parameter = parameter.replace(n,'()')
							if parameter not in typeDict[type]['entity'][subject]['parameters']:
								#if parameter is not in dictionary, add it as a validated parameter
								typeDict[type]['entity'][subject]['parameters'][parameter]=nums
							elif not nums == typeDict[type]['entity'][subject]['parameters'][parameter]:
								#parameter values do not match
								relationValid = False
						else: #relation and attribute
							typeDict[type]['entity'][subject]['relations'].append(relation)
							
						#if num: add value
					print 'Relations for '+subject+': '
					print typeDict[type]['entity'][subject]['relations']
					print 'Parameters for '+subject+': '
					print typeDict[type]['entity'][subject]['parameters']	
	
		for elem in splitfact:
			if elem.startswith('['):
				type = elem
				type = type.strip('[')
				type = type.strip(']')
				typEntered=True
			elif elem.startswith('>>'):
				parent = elem
				parent = parent.strip('>>')
				parEntered=True
			elif elem.startswith('#'):
				#restriction =  str(splitfact[(splitfact.index(elem)):])
				restriction = elem
				restriction = str(restriction.strip('#'))
				resEntered=True
				
		entInFact = True
		typInFact = True
		parInFact = True
		resInFact = True
		if typEntered:
			if type not in typeDict:
				typInFact=False
		if subEntered:
			if subject not in typeDict[type]['entity'].keys():
				#if subject not in typeDict, ask whether it satisfies type restrictions
				if typeDict[type]['restriction']:
					for rel in typeDict[type]['restriction']:
						qual= subject+' '+rel+'? (y/n)'
						ans = raw_input(qual)
						if not(ans == 'y') and not(ans == 'yes'):
							print 'not y'
							entInFact=False
				else:
					entInFact=False
				if entInFact:
					typeDict[type]['entity'][subject]={}
					typeDict[type]['entity'][subject]['relations']=[]
					typeDict[type]['entity'][subject]['parameters']={}
					typeDict[type]['entity'][subject]['alias']=[]
					updateDict()
					print typeDict
				
		if parEntered:
			if parent not in typeDict[type]['parent']:
				parInFact=False
		if resEntered:
			if restriction not in typeDict[type]['restriction']:
				resInFact=False
	
		if entInFact and typInFact and parInFact and resInFact and relationValid:
			print fact + ':validated'
			continue
		else:
			print fact + ':not validated'
			continue


readVocab()
updateDict()
collectRelations()
print 'Type Info in Vocab:'
print typeDict
validateNewFact()
