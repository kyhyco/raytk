from raytkTools import RaytkTools
import yaml

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _InspectorCorePars(ParCollection):
		Hastarget: 'BoolParamT'
		Definitiontable: 'DatParamT'
		Targetcomp: 'CompParamT'
	ipar.inspectorCore = _InspectorCorePars()

	class _StatePar(ParCollection):
		Includeparams: 'BoolParamT'
	ipar.specPanelState = _StatePar()

class SpecPanel:
	def __init__(self, ownerComp: COMP):
		self.ownerComp = ownerComp

	def generateSpec(self) -> str | None:
		spec = RaytkTools().loadROPSpec(ipar.inspectorCore.Targetcomp.eval(), checkExists=False)
		if not spec:
			return None
		return yaml.dump(spec, default_style='', sort_keys=False)

	def Update(self):
		self.ownerComp.op('generateSpec').cook(force=True)

