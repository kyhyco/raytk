from pathlib import Path
from typing import Optional
from raytkModel import EditorItemGraph
from raytkUtil import RaytkTags
import subprocess

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *
	from devel.toolkitEditor.ropEditor.ropEditor import ROPEditor
	ext.ropEditor = ROPEditor(COMP())

	class _Pars(ParCollection):
		Selecteditem: 'StrParamT'

	class _COMP(COMP):
		par: _Pars

class DatEditorPanel:
	def __init__(self, ownerComp: '_COMP'):
		self.ownerComp = ownerComp

	@property
	def opDef(self) -> 'Optional[COMP]':
		info = ext.ropEditor.ROPInfo
		return info and info.opDef

	@property
	def _currentItemPar(self) -> 'Optional[Par]':
		if not hasattr(ext, 'ropEditor'):
			return
		info = ext.ropEditor.ROPInfo
		if not info or not info.opDef:
			return
		name = self.ownerComp.par.Selecteditem.eval()
		if name:
			return info.opDef.par[name]

	@property
	def currentSourceDat(self) -> 'Optional[DAT]':
		graph = self._currentItemGraph
		return graph and graph.sourceDat

	@property
	def _currentItemGraph(self) -> 'Optional[EditorItemGraph]':
		par = self._currentItemPar
		if par is None:
			return
		graph = EditorItemGraph.fromPar(par)
		if graph.supported:
			return graph

	@property
	def externalizeEnabled(self):
		graph = self._currentItemGraph
		return graph and bool(graph.sourceDat) and graph.file is not None and not bool(graph.file.eval())

	@property
	def fileParameterVisible(self):
		if not self.ownerComp.par.Showfile:
			return False
		graph = self._currentItemGraph
		return graph and graph.file is not None

	@property
	def _itemTable(self) -> 'DAT':
		return self.ownerComp.op('itemTable')

	def buildItemGraphInfo(self, dat: 'DAT'):
		dat.clear()
		dat.appendCol([
			'endDat',
			'sourceDat',
			'hasEval',
			'hasMerge',
			'supported',
			'file',
		])
		dat.appendCol([''])
		graph = self._currentItemGraph
		if not graph:
			return
		dat['endDat', 1] = graph.endDat or ''
		dat['sourceDat', 1] = graph.sourceDat or ''
		dat['hasEval', 1] = int(graph.hasEval)
		dat['hasMerge', 1] = int(graph.hasMerge)
		dat['supported', 1] = 1
		dat['file', 1] = graph.file or ''

	def onCreateClick(self):
		info = ext.ropEditor.ROPInfo
		itemGraph = self._currentItemGraph
		if not info or not itemGraph or itemGraph.file:
			return
		datType = self._itemTable[itemGraph.par.name, 'type'] or 'text'
		if datType == 'table':
			dat = info.rop.create(tableDAT)
		elif datType == 'text':
			dat = info.rop.create(textDAT)
		else:
			ui.status = f'Unsupported DAT type: {datType}'
			return
		name = self._itemTable[itemGraph.par.name, 'datName']
		if name:
			dat.name = name
		ui.undo.startBlock(f'Creating {dat}')
		try:
			self._externalize(itemGraph, dat)
		finally:
			ui.undo.endBlock()

	def onDeleteClick(self):
		info = ext.ropEditor.ROPInfo
		itemGraph = self._currentItemGraph
		if not info or not itemGraph or not self._confirmDelete(itemGraph):
			return
		ui.undo.startBlock(f'Delete {itemGraph.par.label} from {info.rop.path}')
		try:
			if itemGraph.file:
				file = Path(itemGraph.file.eval())
				file.unlink(missing_ok=True)
				itemGraph.file.val = ''
			itemGraph.par.val = ''
			if itemGraph.endDat and itemGraph.endDat.valid:
				itemGraph.endDat.destroy()
			if itemGraph.sourceDat and itemGraph.sourceDat.valid:
				itemGraph.sourceDat.destroy()
		finally:
			ui.undo.endBlock()

	def onExternalizeClick(self):
		info = ext.ropEditor.ROPInfo
		itemGraph = self._currentItemGraph
		if not info or not itemGraph or not itemGraph.sourceDat or itemGraph.file is None or itemGraph.file.eval():
			return
		dat = itemGraph.sourceDat
		ui.undo.startBlock(f'Externalizing {dat}')
		try:
			self._externalize(itemGraph, dat)
		finally:
			ui.undo.endBlock()

	def _externalize(self, itemGraph: 'EditorItemGraph', dat: 'DAT'):
		info = ext.ropEditor.ROPInfo
		if not info or not itemGraph or not itemGraph.sourceDat:
			return
		if itemGraph.file is None:
			ui.status = f'Unable to externalize, no file parameter on {itemGraph.sourceDat}!'
			return
		if itemGraph.file.eval():
			ui.status = f'No need to externalize, already have external file: {itemGraph.file}'
			return
		tox = info.toxFile
		if not tox:
			ui.status = f'Unable to externalize, no tox file for {itemGraph.par.name}'
			return
		suffix = str(self._itemTable[itemGraph.par.name, 'fileSuffix'] or '')
		if not suffix:
			ui.status = f'Unable to externalize, no file suffix found for {itemGraph.par.name}'
			return
		file = Path(tox.replace('.tox', suffix))
		file.touch(exist_ok=True)
		itemGraph.file.val = file.as_posix()
		RaytkTags.fileSync.apply(dat, True)
		ui.status = f'Externalized {itemGraph.sourceDat} to file {file.as_posix()}'

	def onExternalEditClick(self):
		graph = self._currentItemGraph
		if graph and graph.sourceDat and graph.sourceDat.par['edit'] is not None:
			binPath = Path(r'C:\Users\tekt\AppData\Local\JetBrains\Toolbox\apps\PyCharm-P\ch-0\202.7660.27\bin\pycharm64.exe')
			if binPath.exists():
				subprocess.Popen([str(binPath), graph.file.val])
				return
			graph.sourceDat.par.edit.pulse()

	@staticmethod
	def _confirmDelete(itemGraph: 'EditorItemGraph'):
		info = ext.ropEditor.ROPInfo
		return ui.messageBox(
			f'Delete {itemGraph.par.label}?',
			f'Are you sure you want to delete the {itemGraph.par.label} of {info.rop.path}?',
			buttons=['Cancel', 'Delete'],
		)
