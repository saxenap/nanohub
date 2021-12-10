import sys
import os
import mmap
from ctypes import *



class SharedMatrix:
	"""
	Implements a 2D array (matrix) in shared memory with the intended use for collecting results from multiprocessing.
	Note that the elements are NOT locked in anyway and that race conditions can develop if two or more processes
	are manipulating the same elements of memory.  Instances of this class are best used when memory cells are mutually
	exclusive (with respect to the multiple subprocesses) by the nature of the processing algorithm.
	"""
	def __init__(self, rowkeys, colkeys, celltype = None):
		self.celltype = None
		self._rows    = None
		self._columns = None
		self.rowdex   = { }
		self.coldex   = { }
		self.extent   = (len(rowkeys), len(colkeys))
		
		if celltype == None:
			self.celltype = c_double
		else:
			self.celltype = celltype

		self._rows    = rowkeys[:]
		self._columns = colkeys[:]

		for i, rowkey in enumerate(rowkeys):
			self.rowdex[rowkey] = i

		for j, colkey in enumerate(colkeys):
			self.coldex[colkey] = j
		
		cType = c_double * (len(rowkeys) * len(colkeys))
		
		mem = mmap.mmap(-1, sizeof(cType), mmap.MAP_SHARED)
		
		self.matrix = cType.from_buffer(mem)
		
	@property
	def rows(self):
		return self._rows

	@property
	def columns(self):
		return self._columns

	def at(self, r, c, val = None):
		h, w = self.extent
		
		if (r >= 0) and (r < h) and (c >= 0) and (c < w):		
			if val is not None:
				self.matrix[((r * w) + c)] = val
			
			return self.matrix[((r * w) + c)]
		else:
			raise IndexError('(%s,%s) is not a valid index in a matrix of %s by %s'%(r, c, h, w))

	def __getitem__(self, k):
		#at = self.at(*k)
		#return self.matrix[at]
		#-- Sorry for the complicated logic, but it's faster.
		return self.matrix[(self.rowdex[k[0]] * self.extent[1]) + self.coldex[k[1]]]

	def __setitem__(self, k, v):
		#at = self.at(*k)
		#self.matrix[at] = v
		#-- Sorry for the complicated logic, but it's faster.
		self.matrix[(self.rowdex[k[0]] * self.extent[1]) + self.coldex[k[1]]] = v

	def save(self, fname, **kwargs):
		prefix     = kwargs.get('prefix', None)
		cellfilter = kwargs.get('cellfilter', (lambda x,y,z: True))

		fOut = open(fname, 'wt')

		if prefix is not None:
			if isinstance(prefix, list) or isinstance(prefix, tuple):
				for header in prefix:
					fOut.write('#-- %s\n'%header)
			if isinstance(prefix, str):
				fOut.write('#-- %s\n'%prefix)
		
		fOut.write('ROWS|%s\n'%len(self.rows))
		
		fOut.write('COLUMNS|%s\n'%len(self.columns))
		
		for row in self.rows:
			fOut.write('ROWNAME|%s\n'%row)
		
		for col in self.columns:
			fOut.write('COLNAME|%s\n'%col)
		
		for row in self.rows:
			for col in self.columns:
				if cellfilter(self, row, col):
					fOut.write('CELL|%s|%s|%s\n'%(row, col, self[row,col]))

		fOut.close( )

	def saveJson(self, fname, **kwargs):
		encoding = kwargs.get('encoding', 'utf-8')
		cellfilter = kwargs.get('cellfilter', (lambda x,y,z: True))

		sparse = [ ]
		rextent, cextent = self.extent
		for i in xrange(rextent):
			for j in xrange(cextent):
				if cellfilter(self, i, j):
					sparse.append([i,j,self.at(i,j)])
		
		obj = [self.rowdex.keys( ), self.coldex.keys( ), sparse]
		
		json.dump(open(fname,'wb'), encoding = encoding, sort_keys=True, indent=4)

	@staticmethod
	def load(fname, constructor = None):
		rows   = [ ]
		cols   = [ ]
		matrix = None

		states = ['ROWS', 'COLUMNS', 'ROWNAME', 'COLNAME', 'CELL']
		
		rowttl = 0
		colttl = 0
		rowcnt = 0
		colcnt = 0

		state = 'ROWS'
		
		if constructor is None:
			constructor = float
		
		for line in open(fname):
			next = state
			
			line = line.strip( )
			
			if len(line) > 0:
				if line[0] != '#':
					tokens = line.split('|')

					cmd  = tokens[0]
					args = tuple(tokens[1:])

					if cmd == state:
						if cmd == 'ROWS':
							rowttl = int(args[0])
							next   = 'COLUMNS'
							
						if cmd == 'COLUMNS':
							colttl = int(args[0])
							next   = 'ROWNAME'
							
						if cmd == 'ROWNAME':
							rows.append(args[0])
							
							rowcnt += 1
							
							if rowcnt >= rowttl:
								next = 'COLNAME'
							
						if cmd == 'COLNAME':
							cols.append(args[0])
							
							colcnt += 1
							
							if colcnt >= colttl:
								matrix = SharedMatrix(rows, cols)
								
								#-- Zero out the newly created table.
								for r in rows:
									for c in cols:
										matrix[r,c] = 0.0

								next = 'CELL'

						if cmd == 'CELL':
							rowdx, coldx, x = args
							matrix[rowdx, coldx] = constructor(x)

					else:
						raise Exception("Confused state???")

			state = next

		return matrix

	@staticmethod
	def loadJson(fname, encoding = None):
		if encoding is not None:
			obj = json.load(open(fname), encoding)
		else:
			obj = json.load(open(fname))

		rows   = obj[0]
		cols   = obj[1]
		sparse = obj[2]
		
		m = SharedMatrix(rows, cols)
		
		#-- Zero out the newly created table.
		for r in rows:
			for c in cols:
				matrix[r,c] = 0.0
		
		for entry in sparse:
			m.at(*tuple(entry))

		return m

	@staticmethod
	def forkload(fname, constructor = None):
		"""
		Like the .load static method, but forks off a subprocess to do the heavy I/O in reading the cell contents.
		Returns a tuple of the form, (matrix, subprocessid) where matrix is the allocated SharedMatrix instance
		and subprocessid is the process id of the subprocess that is doing the I/O.  Note that SharedMatrix will
		be in an indeterminate state until the subprocess terminates.
		"""
		rows   = [ ]
		cols   = [ ]
		matrix = None

		states = ['ROWS', 'COLUMNS', 'ROWNAME', 'COLNAME', 'CELL']
		
		rowttl = 0
		colttl = 0
		rowcnt = 0
		colcnt = 0

		state = 'ROWS'
		
		if constructor is None:
			constructor = float
		
		for line in open(fname):
			next = state
			
			line = line.strip( )
			
			if len(line) > 0:
				if line[0] != '#':
					tokens = line.split('|')

					cmd  = tokens[0]
					args = tuple(tokens[1:])

					if cmd == state:
						if cmd == 'ROWS':
							rowttl = int(args[0])
							next   = 'COLUMNS'
							
						if cmd == 'COLUMNS':
							colttl = int(args[0])
							next   = 'ROWNAME'
							
						if cmd == 'ROWNAME':
							rows.append(args[0])
							
							rowcnt += 1
							
							if rowcnt >= rowttl:
								next = 'COLNAME'
							
						if cmd == 'COLNAME':
							cols.append(args[0])
							
							colcnt += 1
							
							if colcnt >= colttl:
								matrix = SharedMatrix(rows, cols)
								
								pid = os.fork( )
								
								if pid == 0:
									#-- I'm the child.
									#-- Zero out the newly created table.								
									for r in rows:
										for c in cols:
											matrix[r,c] = 0.0
								
									next = 'CELL'

								else:
									return (matrix, pid)

						if cmd == 'CELL':
							rowdx, coldx, x = args
							matrix[rowdx, coldx] = constructor(x)

					else:
						raise Exception("Confused state???")

			state = next

		#-- Should only ever reach this line if I am the child subprocess.
		sys.exit(0)
