def isIn(s, l, r):
	s = s.strip()
	if s.startswith(l) and s.endswith(r):
		return True
	else:
		return False
			
def peel(s, l, r):
	if isIn(s, l, r):
		peeled = s.lstrip(l)
		peeled = peeled.rstrip(r)
		return peeled
	else:
		return s
		
def isFloat(s):
	sep = s.split('.')
	if len(sep) == 2:
		pass
	else:
		return False
		
	try:
		float(s)
		return True
	except:
		return False
		
def isInt(s):
	if not isFloat(s):
		pass
	else:
		return False
		
	try:
		int(s)
		return True
	except:
		return False
		
def isNum(s):
	if isFloat(s) or isInt(s):
		return True
	else:
		return False

def toNum(s):
	if isNum(s):
		pass
	else:
		return s
		
	if isFloat(s):
		return float(s)
	elif isInt(s):
		return int(s)
	else:
		return False