from typing import Optional, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

	class ipar:
		class inspectorState:
			Hastarget: bool
			Hasownviewer: bool
			Targettype: 'Union[str, Par]'
			Rawtarget: 'Union[str, OP, DAT, COMP]'
			Definitiontable: 'Union[str, DAT]'
			Targetcomp: 'Union[str, COMP]'

class TargetTypes:
	none = 'none'
	rop = 'rop'
	outputOp = 'outputOp'
	definitionTable = 'definitionTable'

	values = [
		none,
		rop,
		outputOp,
		definitionTable,
	]

def updateTargetTypeMenu():
	p = ipar.inspectorState.Targettype  # type: Par
	p.menuNames = p.menuLabels = TargetTypes.values

class Inspector:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp
		self.state = ipar.inspectorState

	def Reset(self, _=None):
		self.state.Hastarget = False
		self.state.Targettype = TargetTypes.none
		self.state.Rawtarget = ''
		self.state.Targetcomp = ''
		self.state.Definitiontable = ''

	def Inspect(self, o: 'Union[OP, DAT, COMP, str]'):
		o = o and op(o)
		if not o:
			self.Reset()
			return
		if o.isCOMP and o.name == 'opDefinition' and o.par['Hostop']:
			o = o.par.Hostop.eval()
		if o.isDAT and o.isTable and o.numRows > 1:
			self.inspectDefinitionTable(o)
		elif o.isCOMP and 'raytkOP' in o.tags:
			self.inspectComp(o)
		else:
			# TODO: better error handling
			raise Exception(f'Unsupported OP: {o!r}')

	def inspectDefinitionTable(self, dat: 'DAT'):
		if 'raytkOP' in dat.parent().tags and dat.name == 'definition' and dat[1, 'path'] == dat.parent().path:
			self.inspectComp(dat.parent())
			return
		self.state.Rawtarget = dat
		self.state.Targettype = TargetTypes.definitionTable
		self.state.Definitiontable = _pathOrEmpty(dat)
		self.state.Targetcomp = _pathOrEmpty(op(dat[1, 'path']))
		self.state.Hastarget = True
		self.state.Hasownviewer = False

	def inspectComp(self, comp: 'COMP'):
		self.state.Rawtarget = _pathOrEmpty(comp)
		self.state.Targetcomp = _pathOrEmpty(comp)
		isOutput = 'raytkOutput' in comp.tags
		if isOutput:
			self.state.Targettype = TargetTypes.outputOp
		else:
			self.state.Targettype = TargetTypes.rop
		self.state.Definitiontable = _pathOrEmpty(comp.op('definition'))
		self.state.Hastarget = True
		self.state.Hasownviewer = isOutput

def _pathOrEmpty(o: Optional['OP']):
	return o.path if o else ''
