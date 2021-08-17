from raytkTypes import evalSpecInOp
import re

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from typing import Dict, List, Optional, Union
	from raytkUtil import OpDefParsT
	from _stubs.PopDialogExt import PopDialogExt


def parentPar() -> 'Union[ParCollection, OpDefParsT]':
	return parent().par

def _host() -> 'Optional[COMP]':
	return parentPar().Hostop.eval()

def buildName():
	host = _host()
	if not host:
		return ''
	pathParts = host.path[1:].split('/')
	for i in range(len(pathParts)):
		if pathParts[i].startswith('_'):
			pathParts[i] = 'U' + pathParts[i][1:]
	name = '_'.join(pathParts)
	name = re.sub('_+', '_', name)
	if name.startswith('_'):
		name = 'o_' + name
	return 'RTK_' + name

def _evalType(category: str, supportedTypes: 'DAT', inputDefs: 'DAT'):
	return evalSpecInOp(
		spec=supportedTypes[category, 'spec'].val,
		expandedTypes=supportedTypes[category, 'types'].val,
		inputCell=inputDefs[1, category],
	)

def buildTypeTable(dat: 'scriptDAT', supportedTypes: 'DAT', inputDefs: 'DAT'):
	dat.clear()
	dat.appendRows([
		['coordType', _evalType('coordType', supportedTypes, inputDefs)],
		['returnType', _evalType('returnType', supportedTypes, inputDefs)],
		['contextType', _evalType('contextType', supportedTypes, inputDefs)],
	])

def buildInputTable(dat: 'DAT', inDats: 'List[DAT]'):
	dat.clear()
	dat.appendRow(['slot', 'inputFunc', 'name', 'path', 'coordType', 'contextType', 'returnType'])
	for i, inDat in enumerate(inDats):
		slot = f'inputName{i + 1}'
		if inDat.numRows < 2 or not inDat[1, 'name'].val:
			dat.appendRow([slot])
		else:
			dat.appendRow([
				slot,
				f'inputOp{i + 1}',
				inDat[1, 'name'],
				inDat[1, 'path'],
				inDat[1, 'coordType'],
				inDat[1, 'contextType'],
				inDat[1, 'returnType'],
			])

def buildLegacyTypeSettingsTable(dat: 'DAT', inputTable: 'DAT'):
	dat.clear()
	typeVal = parentPar().Coordtype.eval()
	if typeVal != 'useinput':
		dat.appendRow(['coordType', typeVal, '0'])
	else:
		typeVal = inputTable['inputName1', 'coordType'] or parentPar().Fallbackcoordtype
		dat.appendRow(['coordType', typeVal, '1'])
	typeVal = parentPar().Contexttype.eval()
	if typeVal != 'useinput':
		dat.appendRow(['contextType', typeVal, '0'])
	else:
		typeVal = inputTable['inputName1', 'contextType'] or parentPar().Fallbackcontexttype
		dat.appendRow(['contextType', typeVal, '1'])
	typeVal = parentPar().Returntype.eval()
	if typeVal != 'useinput':
		dat.appendRow(['returnType', typeVal, '0'])
	else:
		typeVal = inputTable['inputName1', 'returnType'] or parentPar().Fallbackreturntype
		dat.appendRow(['returnType', typeVal, '1'])

def combineInputDefinitions(
		dat: 'DAT',
		inDats: 'List[DAT]',
		defFields: 'DAT',
):
	dat.clear()
	if not inDats:
		return
	cols = defFields.col(0)
	dat.appendRow(cols)
	inDats = [d for d in inDats if d.numRows > 1]
	if not inDats:
		return
	usedNames = set()
	for d in reversed(inDats):
		insertRow = 0
		for inDatRow in range(1, d.numRows):
			name = d[inDatRow, 'name'].val
			if not name or name in usedNames:
				continue
			usedNames.add(name)
			cells = [
				d[inDatRow, col] or ''
				for col in cols
			]
			dat.appendRow(cells, insertRow)
			insertRow += 1

def processInputDefinitionTypes(dat: 'scriptDAT', supportedTypeTable: 'DAT'):
	_processInputDefTypeCategory(dat, supportedTypeTable, 'coordType')
	_processInputDefTypeCategory(dat, supportedTypeTable, 'contextType')
	_processInputDefTypeCategory(dat, supportedTypeTable, 'returnType')

def _processInputDefTypeCategory(dat: 'scriptDAT', supportedTypeTable: 'DAT', category: 'str'):
	supported = supportedTypeTable[category, 'types'].val.split(' ')
	cells = dat.col(category)
	if not cells:
		return
	errors = []
	ownName = parentPar().Name.eval()
	# TODO: consolidate this and the typeRestrictor
	for cell in cells[1:]:
		inputName = dat[cell.row, 'name']
		inputTypes = cell.val.split(' ')
		supportedInputTypes = [t for t in inputTypes if t in supported]
		if not supportedInputTypes:
			errors.append(f'No supported {category} for {inputName} ({" ".join(inputTypes)}')
		elif len(supportedInputTypes) == 1:
			cell.val = supportedInputTypes[0]
		else:
			# cell.val = ' '.join(supportedInputTypes)
			cell.val = '@' + ownName

def _getParamsOp() -> 'Optional[COMP]':
	return parentPar().Paramsop.eval() or _host()

# Builds the primary table from which all other parameter tables are built.
# This table contains regular parameters and special parameters, with both runtime and macro handling.
def buildParamSpecTable(dat: 'scriptDAT', paramListTable: 'DAT'):
	dat.clear()
	dat.appendRow([
		'localName',
		'globalName',
		'source',
		'style',
		'tupletName',
		'tupletGlobalName',
		'vecIndex',
		'status',
		'handling',
		'conversion',
	])
	globalPrefix = parentPar().Name.eval() + '_'

	def addPar(p: 'Par', handling: str):
		dat.appendRow([
			p.name,
			globalPrefix + p.name,
			'param',
			p.style,
			p.tupletName,
			globalPrefix + p.tupletName,
			p.vecIndex,
			'',
			handling,
			'',
		])


	def getNamesFromListTable(category: str):
		rowCells = paramListTable.row(category)
		if not rowCells:
			return []
		names = []
		for cell in rowCells[1:]:
			for n in tdu.split(cell.val.strip()):
				if n not in names:
					names.append(n)
		return names

	# Add regular params from Paramlisttable
	for par in _getRegularParams(getNamesFromListTable('params')):
		addPar(par, handling='runtime')
	# Add macro params from Paramlisttable
	for par in _getRegularParams(getNamesFromListTable('macroParams')):
		addPar(par, handling='macro')

	# Add special params from opDefinition Specialparams par
	specialNames = getNamesFromListTable('specialParams')
	for name in specialNames:
		dat.appendRow([
			name,
			globalPrefix + name,
			'special',
			'Float',
			'',
			'',
			'0',
			'',
			'runtime',
			'',
			])
	# TODO: tuplet placeholder special params ("_")?

	# Update conversions from opDefinition Angleparams par
	for par in _getRegularParams(getNamesFromListTable('angleParams')):
		dat[par.name, 'conversion'] = 'angle'

	# Update param statuses based on tuplets
	_fillParamStatuses(dat)

	# Group special parameters into tuplets
	_groupSpecialParamsIntoTuplets(dat)

def _fillParamStatuses(dat: 'DAT'):
	parsByTuplet = {}  # type: Dict[str, List[Par]]
	host = _getParamsOp()
	if not host:
		return
	for i in range(1, dat.numRows):
		if dat[i, 'source'] != 'param':
			continue
		name = dat[i, 'localName']
		tupletName = dat[i, 'tupletName'].val
		par = host.par[name]
		if par is None:
			continue
		if tupletName not in parsByTuplet:
			parsByTuplet[tupletName] = [par]
		else:
			parsByTuplet[tupletName].append(par)
	for tupletName, pars in parsByTuplet.items():
		if _canBeReadOnlyTuplet(pars):
			for par in pars:
				dat[par.name, 'status'] = 'readOnly'

def _groupSpecialParamsIntoTuplets(dat: 'DAT'):
	parts = []
	tupletIndex = 0
	globalPrefix = parentPar().Name.eval() + '_'

	# TODO: handle placeholders ???? "_"
	def addTuplet():
		tupletName = _getTupletName(parts) or f'special{tupletIndex}'
		for vecIndex, part in enumerate(parts):
			dat[part, 'tupletName'] = tupletName
			dat[part, 'tupletGlobalName'] = globalPrefix + tupletName
			dat[part, 'vecIndex'] = vecIndex

	for i in range(1, dat.numRows):
		if dat[i, 'source'] != 'special':
			continue
		name = dat[i, 'localName'].val
		parts.append(name)
		if len(parts) == 4:
			addTuplet()
			parts.clear()
			tupletIndex += 1
	if parts:
		addTuplet()

def _getRegularParams(specs: 'List[str]') -> 'List[Par]':
	host = _getParamsOp()
	if not host:
		return []
	# TODO: clean this up. joining and splitting and rejoining, etc.
	paramNames = tdu.expand(str(' '.join(specs)).strip())
	if not paramNames:
		return []
	return [
		p
		for p in host.pars(*[pn.strip() for pn in paramNames])
		if p.isCustom and not (p.isPulse and p.name == 'Inspect')
	]

# Builds a table that lists global names of runtime-based parameters.
def buildParamTable(dat: 'DAT', paramSpecTable: 'DAT'):
	dat.clear()
	for i in range(1, paramSpecTable.numRows):
		if paramSpecTable[i, 'handling'] != 'runtime':
			continue
		dat.appendRow([paramSpecTable[i, 'globalName']])

# Builds a table of parameters organized into tuplets.
def buildParamDetailTable(dat: 'DAT', paramSpecTable: 'DAT'):
	dat.clear()
	dat.appendRow(['tuplet', 'source', 'size', 'part1', 'part2', 'part3', 'part4', 'status', 'conversion', 'localNames'])
	namesByTupletName = {}  # type: Dict[str, List[str]]
	for i in range(1, paramSpecTable.numRows):
		tupletName = paramSpecTable[i, 'tupletName'].val
		vecIndex = int(paramSpecTable[i, 'vecIndex'] or 0)
		if not tupletName:
			continue
		if tupletName not in namesByTupletName:
			namesByTupletName[tupletName] = ['', '', '', '']
		namesByTupletName[tupletName][vecIndex] = paramSpecTable[i, 'localName'].val

	for tupletName, parts in namesByTupletName.items():
		if paramSpecTable[parts[0], 'handling'] != 'runtime':
			continue
		size = 0
		for part in parts:
			if part:
				size += 1
			else:
				break
		dat.appendRow([
			paramSpecTable[parts[0], 'tupletGlobalName'],
			paramSpecTable[parts[0], 'source'],
			size,
			paramSpecTable[parts[0], 'globalName'] or '',
			paramSpecTable[parts[1], 'globalName'] or '',
			paramSpecTable[parts[2], 'globalName'] or '',
			paramSpecTable[parts[3], 'globalName'] or '',
			paramSpecTable[parts[0], 'status'],
			paramSpecTable[parts[0], 'conversion'],
			' '.join(p for p in parts if p),
		])


def _canBeReadOnlyTuplet(pars: 'List[Par]'):
	return all(p.readOnly and p.mode == ParMode.CONSTANT for p in pars)

def _getTupletName(parts: 'List[str]'):
	if len(parts) <= 1 or len(parts[0]) <= 1:
		return None
	prefix = parts[0][:-1]
	for part in parts[1:]:
		if not part.startswith(prefix):
			return None
	return prefix

def buildParamTupletAliases(dat: 'DAT', paramTable: 'DAT'):
	dat.clear()
	for i in range(1, paramTable.numRows):
		size = int(paramTable[i, 'size'])
		if size > 1:
			dat.appendRow([
				'#define {} vec{}({})'.format(paramTable[i, 'tuplet'].val, size, ','.join([
					paramTable[i, f'part{j + 1}'].val
					for j in range(size)
				]))
			])

# Builds a table with lists of parameter local names, for use in CHOP parameter expressions.
def buildParamChopNamesTable(dat: 'DAT', paramSpecTable: 'DAT'):
	dat.clear()
	regularNames = []
	specialNames = []
	angleNames = []
	for i in range(1, paramSpecTable.numRows):
		if paramSpecTable[i, 'handling'] != 'runtime':
			continue
		name = paramSpecTable[i, 'localName'].val
		source = paramSpecTable[i, 'source']
		if source == 'param':
			regularNames.append(name)
		elif source == 'special':
			specialNames.append(name)
		if paramSpecTable[i, 'conversion'] == 'angle':
			angleNames.append(name)
	dat.appendRow(['regular', ' '.join(regularNames)])
	dat.appendRow(['special', ' '.join(specialNames)])
	dat.appendRow(['angle', ' '.join(angleNames)])

_typeReplacements = {
	re.compile(r'\bCoordT\b'): 'THIS_CoordT',
	re.compile(r'\bContextT\b'): 'THIS_ContextT',
	re.compile(r'\bReturnT\b'): 'THIS_ReturnT',
}

def _getReplacements(
		inputTable: 'DAT',
		materialTable: 'DAT',
) -> 'Dict[str, str]':
	name = parentPar().Name.eval()
	repls = {
		'thismap': name,
		'THIS_': name + '_',
	}
	mat = materialTable[1, 'material']
	if mat:
		repls['THISMAT'] = str(mat)
	for i in range(inputTable.numRows):
		key = inputTable[i, 'inputFunc']
		val = inputTable[i, 'name']
		if val:
			repls[str(key)] = str(val)
	return repls

def prepareCode(
		dat: 'DAT',
		inputTable: 'DAT',
		materialTable: 'DAT',
):
	if not dat.inputs:
		dat.text = ''
		return
	dat.clear()
	repls = _getReplacements(inputTable, materialTable)
	text = _prepareText(dat.inputs[0].text, repls)
	dat.write(text)

def prepareTable(
		dat: 'DAT',
		inputTable: 'DAT',
		materialTable: 'DAT',
):
	dat.copy(dat.inputs[0])
	if dat.numRows < 1:
		return
	repls = _getReplacements(inputTable, materialTable)
	for row in dat.rows():
		for cell in row:
			cell.val = _prepareText(cell.val, repls)

def _prepareText(
		text: str,
		repls: 'Dict[str, str]',
) -> str:
	if not text:
		return ''
	for find, repl in _typeReplacements.items():
		text = find.sub(repl, text)
	for find, repl in repls.items():
		text = text.replace(find, repl)
	return text

def updateLibraryMenuPar(libsComp: 'COMP'):
	p = parentPar().Librarynames  # type: Par
	libs = libsComp.findChildren(type=DAT, maxDepth=1, tags=['library'])
	libs.sort(key=lambda l: -l.nodeY)
	p.menuNames = [lib.name for lib in libs]

def prepareMacroTable(dat: 'scriptDAT', inputTable: 'DAT', paramSpecTable: 'DAT'):
	dat.clear()
	for cell in inputTable.col('inputFunc')[1:]:
		if not cell.val:
			continue
		dat.appendRow([
			'',
			f'THIS_HAS_INPUT_{tdu.digits(cell.val)}',
			'',
		])
	macroParams = []
	host = _getParamsOp()
	for i in range(1, paramSpecTable.numRows):
		if paramSpecTable[i, 'handling'] != 'macro':
			continue
		par = host.par[paramSpecTable[i, 'localName']]
		if par is not None:
			macroParams.append(par)
	for par in macroParams:
		name = par.name
		val = par.eval()
		style = par.style
		if style in ('Menu', 'Str', 'StrMenu'):
			dat.appendRow(['', f'THIS_{name}_{val}', ''])
			dat.appendRow(['', f'THIS_{name}', val])
		elif style == 'Toggle':
			if val:
				dat.appendRow(['', f'THIS_{name}', ''])
		else:
			dat.appendRow(['', f'THIS_{name}', val])
	for table in [op(parentPar().Macrotable)] + parentPar().Generatedmacrotables.evalOPs():
		if not table or table.numCols == 0 or table.numRows == 0:
			continue
		elif table.numCols == 3:
			dat.appendRows(table.rows())
		elif table.numCols == 1:
			dat.appendRows([
				['', c.val, '']
				for c in table.col(0)
			])
		elif table.numCols == 2:
			dat.appendRows([
				['', cells[0], cells[1]]
				for cells in table.rows()
			])
		else:
			dat.appendRows([
				[cells[0], cells[1], ' '.join([c.val for c in cells[2:]])]
				for cells in table.rows()
			])

def prepareTextureTable(dat: 'scriptDAT'):
	dat.clear()
	dat.appendRow(['name', 'path', 'type'])
	table = parentPar().Texturetable.eval()
	if not table or table.numRows < 1:
		return
	namePrefix = parentPar().Name.eval() + '_'
	i = 0
	useNames = False
	if table[0, 0] == 'name' and table[0, 1] == 'path':
		i = 1
		useNames = True
	while i < table.numRows:
		name = str(table[i, 'name' if useNames else 0] or '')
		path = str(table[i, 'path' if useNames else 1] or '')
		if name and path:
			dat.appendRow([
				namePrefix + name,
				path,
				table[i, 'type' if useNames else 2] or '2d',
			])
		i += 1

def prepareBufferTable(dat: 'scriptDAT'):
	dat.clear()
	dat.appendRow(['name', 'type', 'chop', 'uniformType', 'length', 'expr1', 'expr2', 'expr3', 'expr4'])
	table = parentPar().Buffertable.eval()
	if not table or table.numRows == 0:
		return
	namePrefix = parentPar().Name.eval() + '_'
	if table[0, 0] == 'name':
		for i in range(1, table.numRows):
			name = str(table[i, 'name'] or '')
			path = str(table[i, 'chop'] or '')
			expr1 = str(table[i, 'expr1'] or '')
			expr2 = str(table[i, 'expr2'] or '')
			expr3 = str(table[i, 'expr3'] or '')
			expr4 = str(table[i, 'expr4'] or '')
			if not name:
				continue
			if not path and not expr1 and not expr2 and not expr3 and not expr4:
				continue
			dat.appendRow([
				namePrefix + name,
				str(table[i, 'type'] or '') or 'vec4',
				path,
				str(table[i, 'uniformType'] or '') or 'uniformarray',
				table[i, 'length'],
				expr1, expr2, expr2, expr3,
			])
	else:
		for i in range(table.numRows):
			name = str(table[i, 0] or '')
			path = str(table[i, 1] or '')
			if not name or not path:
				continue
			dat.appendRow([
				namePrefix + name,
				str(table[i, 1] or '') or 'vec4',
				path,
				str(table[i, 2] or '') or 'uniformarray',
			])

def prepareMaterialTable(dat: 'scriptDAT'):
	dat.clear()
	dat.appendRow(['material', 'materialCode'])
	if parentPar().Materialcode:
		dat.appendRow([
			'MAT_' + parentPar().Name.eval(),
			parent().path + '/materialCode',
		])

def _isMaster():
	host = _host()
	return host and host.par.clone == host

def onValidationChange(dat: 'DAT'):
	if _isMaster():
		return
	host = _host()
	if not host:
		return
	host.clearScriptErrors()
	if dat.numRows < 2:
		return
	cells = dat.col('message')
	if not cells:
		return
	err = '\n'.join([c.val for c in cells])
	host.addScriptError(err)

def onHostNameChange():
	# Workaround for dependency update issue (#295) when the host is renamed.
	op('sel_funcTemplate').cook(force=True)

def _popDialog() -> 'PopDialogExt':
	# noinspection PyUnresolvedReferences
	return op.TDResources.op('popDialog')

def inspect(rop: 'COMP'):
	if hasattr(op, 'raytk'):
		inspector = op.raytk.op('tools/inspector')
		if inspector and hasattr(inspector, 'Inspect'):
			inspector.Inspect(rop)
			return
	_popDialog().Open(
		title='Warning',
		text='The RayTK inspector is only available when the main toolkit tox has been loaded.',
		escOnClickAway=True,
	)

def _useLocalHelp():
	return hasattr(op, 'raytk') and bool(op.raytk.par['Devel'])

def launchHelp():
	url = parentPar().Helpurl.eval()
	if not url:
		return
	if _useLocalHelp():
		url = url.replace('https://t3kt.github.io/raytk/', 'http://localhost:4000/raytk/')
	url += '?utm_source=raytkLaunch'
	ui.viewFile(url)

def updateOP():
	if not hasattr(op, 'raytk'):
		_popDialog().Open(
			title='Warning',
			text='Unable to update OP because RayTK toolkit is not available.',
			escOnClickAway=True,
		)
		return
	host = _host()
	if not host:
		return
	toolkit = op.raytk
	updater = toolkit.op('tools/updater')
	if updater and hasattr(updater, 'UpdateOP'):
		updater.UpdateOP(host)
		return
	if not host.par.clone:
		_popDialog().Open(
			title='Warning',
			text='Unable to update OP because master is not found in the loaded toolkit.',
			escOnClickAway=True,
		)
		return
	if host and host.par.clone:
		host.par.enablecloningpulse.pulse()
