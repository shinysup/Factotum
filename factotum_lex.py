false=0
true=1
from string import *
import factotum_globals
g=factotum_globals.GlobalClass()

class LexException(Exception): pass

class LexFacts:
	markers = (':"',':[',':','*',':*','#*','#"',':<','"','#',' ')

	def __init__(self,parent=None):
		self.parent=parent
		return

	def breakup_fact(self,f):
		m=s=p=r=c=''
		cp=0

		for pm in self.markers:
			cp=len(pm)
			if f[:cp]==pm:
				m=pm
				f=f[cp:]
				break
		mlen = len(m)
		if m=="*" or m==':*' or m=='#*':
			s=g.unique_name()
			f=f[meln:]
		elif m=='"' or m==':"' or m=='#' or m=='#"' or m==':[':
			s=g.current_subject
			f=f[meln:]
		elif m==':<':
			s='\\include'
			f=f[mlen:]
		else:
			pass

		f=f.expandtabs(4)

		cb=f.rfind('\\[')
		if cb>=0:
			c=strip(f[cb:])
			f=f[:cb]

		if m=='#' or m=='#"':
			return(m,g.current_subject,'',[],strip(f),c)

		rb=f.rfind('\\#')
		if rb>=0:
			r=strip(f[rb+2:])
			f=strip(f[:rb])

		if s=='':
			sf=f.split()
			if len(sf):
				se=len(sf[0])
				if se>0:
					s=f[:se]
					f=f[se:]
			else:
				pass

		p=f;
		px=self.str(f)
		if s != '':
			g.current_subject=s
		else:
			s=g.current_subject=g.unique_name()
		return(m,s,p,px,r,c)

	def str(self,p):
		depth=0

		tokens=[]
		ttype=' '
		token=''
		words='a9_-'
		numbers='9-.'

		cp=0
		p=p.strip()
		plen=len(p)
		token_done=false

		esym=''
		while cp<plen:
			c=p[cp]
			try:
				n=p[cp+1]
			except:
				n=' '
			dc=false
			ctype='x'

			if c=='"' and not depth:
				depth += 1; ttype='"'; esym='"'
			elif c=='\\' and n=='<' and not depth:
				depth +=1; ttype='<'; esym='>'; dc=true
			elif c=='\\' and n=='[' and not depth:
				depth+=1; ttype='['; esym=']'; dc=true
			elif c=='\\' and n=='{' and not depth:
				depth+=1; ttype='{'; esym='}'; dc=true
			elif c=='\\' and n=='(' and not depth:
				depth+=1; ttype='('; esym=')'; dc=true
			elif c==esym and depth:
				depth -= 1;
				if not depth:
					token_done=true
					token +=c
					cp+=1
					ctype='x'
			elif c=='\\' and n=='"' and ttype=='"':
				dc=true
			elif c=='\\' and not depth:
				token_done=true; dc=true

			elif c in digits:
				ctype='9'
			elif c in ascii_letters:
				ctype='a'
			elif c in whitespace:
				ctype='w'
			elif c =='+':
				ctype='+'
			elif c=='_':
				ctype='_'
			elif c=='-':
				ctype='-'
			elif c=='.':
				ctype='.'
			else:
				ctype='p'

			if ttype==' ':
				if ctype=='w':
					cp+=1; token_done=true
				elif ctype=='a':
					ttype='W'
				elif ctype=='9' or \
					ctype=='-': ttype='N'
				else:
					token+=c
					cp+=1
					if dc:
						token+=n
						cp+=1
					ttype='P'
					ctype='w'
					token_done=true
			if ttype=='N' and ctype not in numbers:
				token_done=true
			elif ttype=='W' and ctype not in words:
				token_done=true
	
			if token_done:
				if token:
					tokens.append((token,ttype))
				token_done=false
				ttype=' '
				token=''
				ctype='x'
			else:
				token+=c;
				cp+=1
				if dc:
					token+=n;
					cp+=1
		if depth!=0:
			raise LexException("Unbalanced grouping -- %s not found.\n in %s" %\
				(esym,p))
		tokens.append((token,ttype))
		return tokens

	def __repr__(self,s):
		self.lex(s)
		return s

	def unlex(self,lex):
		str=''
		if len(lex) <= 1:str += lex[0][0]
		else:
			for i in lex[:-1]:
				str+=i[0]+' '
			str+=lex[-1][0]
		return str

