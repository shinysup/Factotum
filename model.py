import os, sys, time, glob
from string import *

patterns={} #global used by both relations and parameters dictionaries
types={}
relations={}
parameters={}

class typesClass:
	#types = {} #global

	def init_type(self,tname):
		types[tname]={}
		types[tname]['Name']=tname
		types[tname]['Restrictions']=[]
		types[tname]['Parent']='' #unique parent type

	def add_restriction(self,type,res):
		if type not in types:
			print('type not defined')
		else:
			types[type]['Restrictions'].append(res)

	def set_parent(self,type,ptype):
		if type not in types:
			print('type not defined')
		else:
			types[type]['Parent']=str(ptype)

	def del_restriction(self,type,res):
		if type not in types:
			print('type not defined')
		else:
			types[type]['Restrictions'].remove(res)

	def del_parent(self,type):
		if type not in types:
			print('type not defined')
		else:
			types[type]['Parent']=''

	def modify_restriction(self,type,ores,nres):
		#call del_restriction and add_restriction
		if type not in types:
			print('type not defined')
		else:
			self.del_restriction(type,ores)
			self.add_restriction(type,nres)

	def modify_parent(self,type,nptype):
		if type not in types:
			print('type not defined')
		else:
			self.del_parent(type)
			self.set_parent(type,nptype)

	def get_value(self,type,param):
		if type not in types:
			print('type not defined')
		elif param != 'Restrictions' and param != 'Name' and param !='Parent':
			print('parameter not defined')
		else:
			return types[type][param]

	def return_keys(self):
		return types.keys()
	
	def show_all(self):
		print(types)

class relationsClass:
	#relations = {}

	def init_relation(self,rname):
		relations[rname]={}
		relations[rname]['Name']=rname
		relations[rname]['Format']=''
		relations[rname]['Objects']=[]	

	def set_format(self,rname,format):
		if rname in relations.keys():
			relations[rname]['Format']=str(format)
		else:
			print('relation not defined')

	def add_object(self,rname,obj):
		if rname in relations.keys():
			relations[rname]['Objects'].append(obj)
		else:
			print('relation not defined')

	def del_format(self,rname):
		if rname in relations.keys():
			relations[rname]['Format']=''
		else:
			print('relation not defined')	
	
	def del_object(self,rname,obj):
		if rname in relations.keys():
			relations[rname]['Objects'].remove(obj)
		else:
			print('relation not defined')

	def modify_format(self,rname,format):
		if rname in relations.keys():
			self.del_format(rname)
			self.set_format(rname,format)
		else:
			print('relation not defined')

	def modify_object(self,rname,oobj,nobj):
		if rname in relations.keys():
			self.del_object(rname,oobj)
			self.add_object(rname,nobj)	
		else:
			print('relation not defined')

	def get_value(self,rname,param):
		if rname in relations.keys():
			if param=='Name' or param=='Format' or param=='Objects':
				return relations[rname][param]

			else:
				print('parameter not defined')
		else:
			print('relation not defined')

	def show_all(self):
		print(relations)

	def return_keys(self):
		return relations.keys()

	#def add_patternrname,pat):


class parametersClass:
	#parameters = {}	
	
	def init_parameter(self,pname):
		parameters[pname]={}
		parameters[pname]['Name']=''
		parameters[pname]['Value']=''
		parameters[pname]['Unit']=''
	
	def set_value(self,pname,val):
		if pname in parameters.keys():
			parameters[pname]['Value']=val
		else:
			print('parameter not defined')

	def set_unit(self,pname,unit):
		if pname in parameters.keys():
			parameters[pname]['Unit']=str(unit)
		else:
			print('parameter not defined')		

	def del_value(self,pname):
		if pname in parameters.keys():
			parameters[pname]['Value']=''
		else:
			print('parameter not defined')		

	def del_unit(self,pname):
		if pname in parameters.keys():
			parameters[pname]['Unit']=''
		else:
			print('parameter not defined')

	def modify_value(self,pname,val):
		if pname in parameters.keys():
			self.del_value(pname)
			self.set_value(pname,val)
		else:
			print('parameter not defined')

	def modify_unit(self,pname,unit):
		if pname in parameters.keys():
			self.del_unit(pname)
			self.set_unit(pname,unit)
		else:
			print('parameter not defined')

	def get_value(self,pname,param):
		if pname in parameters.keys():
			if param=='Name' or param=='Value' or param=='Unit':
				return parameters[pname][param]
			else:
				print('parameter not defined')
		else:
			print('parameter not defined')

	def show_all(self):
		print(parameters)

	def return_keys(self):
		return parameters.keys()

	#def add_pattern(self,pname,pat):


#t = parametersClass()
#e=input()
#t.init_parameter(e)
#res='this is restriction'
#t.set_unit(e,res)
#par = 'Human'
#t.set_value(e,par)
#t.del_unit(e)
#t.del_value(e)
#modres='modified restriction'
#t.set_unit(e,res)
#t.modify_unit(e,modres)
#mpar='Asian'
#t.modify_value(e,mpar)
#g=t.return_keys()
#print(g)
#t.show_all()
