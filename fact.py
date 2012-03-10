import os, sys, time, glob
from string import *
import model

entities = {} #global

def init_entity(ename):
	entities[ename]={}
	entities[ename]['Name']=str(ename)
	entities[ename]['Alias']=[]
	entities[ename]['Types']=[]
	entities[ename]['Relations']={}
	entities[ename]['Parameters']={}

def add_param(ename,pname,val):
	
	if ename not in entities.keys():
		print(ename,' not in entities')
	else:
		if pname=='Alias':
			entities[ename]['Alias'].append(val)
		elif pname=='Types':
			if val in model.types.keys():
				entities[ename]['Types'].append(val)
			else:
				print('type not defined')
		elif pname=='Relations':
			init_relation(ename,val)
		elif pname=='Parameters':
			init_parameter(ename,val)
		elif pname=='Name':
			if entities[ename]['Name']:
				print('cannot add name, use modify')
			else:
				entities[ename]['Name']=str(val)
		else:
			print('wrong parameter name')


def modify_param(ename,pname,oval,nval):
	
	if ename not in entities.keys():
		print(ename+' not in entities')
	else:
		if pname=='Alias' or pname=='Types':
			if oval not in entities[ename][pname]:
				print('value '+oval+' to be modified not present')
			else:
				entities[ename][pname].remove(oval)
				entities[ename][pname].append(nval)
		elif pname=='Relations' or pname=='Parameters':
			print('dummy') #edit later
		elif pname=='Name':
			if oval != entities[ename]['Name']:
				print(oval + 'is not the current name')
			else:
				entities[ename]['Name']=str(nval) 
		else:
			print('wrong parameter name')


def del_param(ename,pname,val):
	if ename not in entities.keys():
		print(ename+' not in entities')
	else:
		if pname=='Alias' or pname=='Types':
			if val not in entities[ename][pname]:
				print(val + ' not present')
			else:
				entities[ename][pname].remove(oval)
		elif pname=='Relations' or pname =='Parameters':
			del entities[ename][pname][val]
		elif pname=='Name':
			entities[ename]['Name']=''
		else:
			print('wrong parameter name')

def get_value(ename,pname):
	if ename not in entities.keys():
		print(ename+' not in entities')
	else:
		if pname not in entities[ename].keys():
			print('wrong parameter name')
		else:
			return entities[ename][pname]	

def show_all():
	print(entities)

def init_relation(ename,rel):
	if rel in model.relations.keys(): 
		entities[ename]['Relations'][rel]={}
		entities[ename]['Relations'][rel]['Name']= model.relations[rel]['Name'] #describes the relation.
		entities[ename]['Relations'][rel]['Format']= model.relations[rel]['Format'] #desired output format
		entities[ename]['Relations'][rel]['Object']=model.relations[rel]['Object'] #list of types
		entities[ename]['Relations'][rel]['Pattern']=model.relations[rel]['Pattern']  #pattern of input distinguished by marker
	else:
		print('relation not defined')	

def init_parameter(ename,param):
	entities[ename]['Parameters'][param]={}
	entities[ename]['Parameters'][param]['Value']=''
	entities[ename]['Parameters'][param]['Unit']=''
	entities[ename]['Parameters'][param]['Name']=''


#e = input()
#init_entity(e)
#f = input()
#add_param(e,'Relations',f)
#show_all()
#g = get_value(e,'Alias')
#print(g)
#g = input()
#modify_param(e,'Types',f,g)
#print(entities)
