import os, sys, time, glob
from string import *

patterns={} #global used by both relations and parameters dictionaries

class typesClass:
	types = {} #global

	def init_type(tname):
		types[tname]={}
		types[tname]['Name']=tname
		types[tname]['Restrictions']=[]
		types[tname]['Parent']='' #unique parent type

	def add_restriction(type,res):
		if type not in types:
			print('type not defined')
		else:
			types[type]['Restrictions'].append(res)

	def set_parent(type,ptype):
		if type not in types:
			print('type not defined')
		else:
			types[type]['Parent']=str(ptype)

	def del_restriction(type,res):
		if type not in types:
			print('type not defined')
		else:
			types[type]['Restrictions'].remove(res)

	def del_parent(type):
		if type not in types:
			print('type not defined')
		else:
			types[type]['Parent']=''

	def modify_restriction(type,ores,nres):
		#call del_restriction and add_restriction
		if type not in types:
			print('type not defined')
		else:
			del_restriction(type,ores)
			add_restriction(type,nres)

	def modify_parent(type,nptype):
		if type not in types:
			print('type not defined')
		else:
			del_parent(type)
			set_parent(type,nptype)

	def get_value(type,param):
		if type not in types:
			print('type not defined')
		elif param != 'Restrictions' and param != 'Name' and param !='Parent':
			print('parameter not defined')
		else:
			return types[type][param]

	def return_keys():
		return types.keys()
	
	def show_all():
		print(types)

class relationsClass:
	relations = {}

	def init_relation(rname):
		relations[rname]={}
		relations[rname]['Name']=''
		relations[rname]['Format']=''
		relations[rname]['Objects']=[]	

	def set_format(rname,format):
		if rname in relations.keys():
			relations[rname]['Format']=str(format)
		else:
			print('relation not defined')

	def add_object(rname,obj):
		if rname in relations.keys():
			relations[rname]['Objects'].append(obj)
		else:
			print('relation not defined')

	def del_format(rname):
		if rname in relations.keys():
			relations[rname]['Format']=''
		else:
			print('relation not defined')	
	
	def del_object(rname,obj):
		if rname in relations.keys():
			relations[rname]['Objects'].remove(obj)
		else:
			print('relation not defined')

	def modify_format(rname,format):
		if rname in relations.keys():
			del_format(rname)
			set_format(rname,format)
		else:
			print('relation not defined')

	def modify_object(rname,oobj,nobj):
		if rname in relations.keys():
			del_object(rname,oobj)
			add_object(rname,nobj)	
		else:
			print('relation not defined')

	def get_value(rname,param):
		if rname in relations.keys():
			if param=='Name' or param=='Format' or param=='Objects':
				return relations[rname][param]

			else:
				print('parameter not defined')
		else:
			print('relation not defined')

	def show_all():
		print(relations)

	def return_keys():
		return relations.keys()

	#def add_patternrname,pat):


class parametersClass:
	parameters = {}	
	
	def init_parameter(pname):
		parameters[pname]={}
		parameters[pname]['Name']=''
		parameters[pname]['Value']=''
		parameters[pname]['Unit']=''
	
	def set_value(pname,val):
		if pname in parameters.keys():
			parameters[pname]['Value']=val
		else:
			print('parameter not defined')

	def set_unit(pname,unit):
		if pname in parameters.keys():
			parameters[pname]['Unit']=str(unit)
		else:
			print('parameter not defined')		

	def del_value(pname):
		if pname in parameters.keys():
			parameters[pname]['Value']=''
		else:
			print('parameter not defined')		

	def del_unit(pname):
		if pname in parameters.keys():
			parameters[pname]['Unit']=''
		else:
			print('parameter not defined')

	def modify_value(pname,val):
		if pname in parameters.keys():
			del_value(pname)
			set_value(pname,val)
		else:
			print('parameter not defined')

	def modify_unit(pname,unit):
		if pname in parameters.keys():
			del_unit(pname)
			set_unit(pname,unit)
		else:
			print('parameter not defined')

	def get_value(pname,param):
		if pname in parameters.keys():
			if param=='Name' or param=='Value' or param=='Unit':
				return parameters[pname][param]
			else:
				print('parameter not defined')
		else:
			print('parameter not defined')

	def show_all():
		print(parameters)

	def return_keys():
		return parameters.keys()

	#def add_pattern(pname,pat):

