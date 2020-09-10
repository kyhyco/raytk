from typing import Optional, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from src.components.inspectorCore.inspectorCoreExt import InspectorCore

	class ipar:
		class inspectorState:
			Selectedview: 'Union[str, Par]'
			Selectedbodytab: 'Union[str, Par]'

class ReturnTypes:
	Sdf = 'Sdf'
	vec4 = 'vec4'
	float = 'float'

	values = [
		Sdf,
		vec4,
		float,
	]

class CoordTypes:
	vec2 = 'vec2'
	vec3 = 'vec3'

	values = [
		vec2,
		vec3,
	]

def updateStateMenus():
	p = ipar.inspectorState.Selectedbodytab
	table = op('body_tabs')
	p.menuNames = table.col('name')[1:]
	p.menuLabels = table.col('label')[1:]

class Inspector:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp
		self.state = ipar.inspectorState
		self.core = iop.inspectorCore  # type: Union[InspectorCore, COMP]

	def Openwindow(self, _=None):
		self.ownerComp.op('window').par.winopen.pulse()

	def Reset(self, _=None):
		self.core.Reset()

	def Inspect(self, o: 'Union[OP, DAT, COMP, str]'):
		self.core.Inspect(o)
		views = self.ownerComp.op('available_views')
		p = self.state.Selectedview
		p.menuNames = ['none'] + views.row(1) or []
		p.menuLabels = ['None'] + views.row(0) or []
		if len(p.menuNames) > 1:
			p.val = p.menuNames[1]
		else:
			p.val = 'none'
		if self.core.par.Hastarget:
			self.Openwindow()

def _pathOrEmpty(o: Optional['OP']):
	return o.path if o else ''
