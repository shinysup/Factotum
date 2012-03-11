false = 0
true = 1
from string import *
import factotum_lex
import factotum_globals
import fact
lex = factotum_lex.LexFacts()
g = factotum_globals.GlobalClass()

class EntityClass:
	entities = fact.entities

	def __init__(self,parent=None):
		self.parent = parent
		return

	def alias(self,m,s,a,px,r,c):
		if not s:
			s=g.current_subject
		if not a:
			print("error in " + s + ": alias empty.")
		if a not in self.entities:
			print('alias: ' + a)
			self.entities[a]=[]
			self.entities[a].append(['A',m,a,s,[],r,c])
		if s not in self.entities:
			print('alias: '+s)
			self.entities[s]=[]
			self.entities[s].append(['a','',s,a,[],r,c])
		return

	def cits(self,m,s,p,px,r,c):
		if not s:
			s=g.current_subject
		if s not in self.entities:
			self.entities[s]=[]
		self.entities[s].append(["C",m,s,'',[],r,c])
		return
	
	def restrictions(self,m,s,p,px,r,c):
		if not s: s=g.current_subject
		if s not in self.entities:
			self.entities[s]=[]
		self.entities[s].append(["P",m,s,p,[],r,c])
		return

	def predicate(self,m,s,p,px,r,c):
		if not s:
			s=g.current_subject
		if s not in self.entities:
			self.entities[s]=[]
		px=lex.str(p)
		self.entities[s].append(["F",m,s,p,px,r,c])
		return

	def type(self,m,s,t,px,r,c):
		if not s:
			s=g.current_subject
		if s not in self.entities:
			self.entities[s]=[]
		self.entities[s].append(["T",m,s,t,[],r,c])
		return

	def build_entities(self,factf):
		a=m=s=p=r=c=''
		px=[]
	
		g.current_subject=g.unique_name()

		next_line=''
		next_line=factf.readline()
		print('Subject: ', g.current_subject)
	
		while len(next_line) > 0:
			afact = next_line[:-1]
			next_line=''
			next_line=factf.readline()

			while (len(next_line) >0 ) and (next_line[0] == '-'):
				afact += '\n'+next_line[1:-1]
				next_line=''
				next_line=factf.readline()
				continue
			
			afact=str(afact)
			print('Current Fact: ' + afact)
		#	if strip(afact) == "":
		#		continue

			(m,s,p,px,r,c)=lex.breakup_fact(afact)
			p=p.strip()

			if s[0:2]=="\<":
				se=p.find('>')
				if se > 0:
					a=s[2:]+' '+p[:se-1]
					p=strip(p[se:])
					s=self.unique_name()
					e.alias(m,s,a,[],[],r,c)
				else:
					s=s[2:]
			elif len(m) and m[0] == ':':
				if p[:2] =='<-':
					a=strip(p[2:])
					self.alias(m,s,a,'',[],r,c)
				elif p[:2] == '->':
					a=s
					s=strip(p[2:])
					self.alias(m,a,s,[],r,c)
				elif p[:1] == '[':
					te=p.find(']')
					if te > 0:
						t=p.strip(p[1:te])
					else:
						print('Warning: Type has no ending ]\nin ',p)
						t=strip(p[1:])
					print('Type: '+ t)
					self.type(m,s,t,[],r,c)
				elif p[:1]=='#':
					self.restrictions(m,s,p,px,r,c)
				elif p[:2]=='>>':
					self.parentType(m,s,p,px,r,c)
				elif m==":[":
					ec=rfind(p,']')
					if ec>0:
						p=p[0:ec]
					self.cits(m,s,'',[],r,p)
				continue
			else:
				self.predicate(m,s,p,px,r,c)
		return

	def entity(self,e):
		if e in self.entities:
			return self.entities[e]
		else:
			return none

	def keys(self):
		keys=list(self.entities.keys())
		return kys

	def show(self,etag,dent1=4,dent2=4):

		indent1=dent1*" "
		indent2=indent1 + dent2 * " "

		if etag not in self.entities:
			print('No entity named:',etag)
			return

		print(indent1+etag)
		for i in self.entities[etag]:
			it=i[0]
			if it=='T':
				print(indent2+"Type is",i[3],i[5])
			elif it=='R':
				print(indent2+"Has a Restriction:",i[5])
			elif it=='A':
				print(indent2+"Alias for",i[3],i[5])
			elif it=='a':
				print(indent2+"Alias for",i[3],i[5])
			elif it=='C':
				print(indent2+"Citations",i[6])
			elif it=='F':
				if i[5]:
					print(indent2,i[3],'#',i[5])
				else:
					print(indent2,i[3])
			else:
				print(indent2,repr(i))
		print('')

	def show_all(self):
		e_tags=list(self.entities.keys())
		e_tags.sort(key=str.lower)
		print('\nEntities are:')
		for et in e_tags:
			self.show(et)
