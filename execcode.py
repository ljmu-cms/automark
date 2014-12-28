
#!/usr/bin/env python 
"""
execcode

David Llewellyn-Jones
Liverpool John Moores University
18/12/2014
Execute code with given inputs and return the outputs
"""

import os
import subprocess

class ExecCode:
	def __init__(self, sourcefolder, leafname, classname, tempfolder):
		self.folder = sourcefolder
		self.leafname = leafname
		self.classname = classname
		self.tempfolder = tempfolder
		filename = os.path.join(sourcefolder, leafname)
		# Load in the program from file
		self.fullProgram = ''
		with open(filename) as file:
			self.fullProgram = file.read()

	def getFullProgram(self):
		return self.fullProgram

	def compile_source(self):
		result = False
		output = ''
		if ExecCode.which('javac') == None:
			output = 'Java compiler javac could not be found'
		else:
			if not os.path.exists(self.tempfolder):
				os.makedirs(self.tempfolder)
			source_compile = 'javac -sourcepath \"{}\" -d \"{}\" \"{}/{}\"'.format(self.folder, self.tempfolder, self.folder, self.leafname)
			print source_compile
			# Returns True if an error occurs
			#result = os.system(source_compile) != 0

			program = subprocess.Popen(['javac', '-sourcepath', self.folder, '-d', self.tempfolder, self.folder + '/' + self.leafname], shell=False, cwd='.', stderr=subprocess.STDOUT, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
			output = program.stdout.read()
			program.communicate()
			result = program.returncode

		return [result, output]

	def execute(self):
		output = ''
		if ExecCode.which('java') == None:
			print 'Java VM could not be found'
		else:
			program = subprocess.Popen(['java', self.classname], shell=False, cwd=self.folder, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
			program.stdin.write('10\n11\n12\n')
			output = program.stdout.read()
		return output
 
	#http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
	@staticmethod
	def which(program):
		def is_exe(fpath):
			return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
	 
		fpath, fname = os.path.split(program)
		if fpath:
			if is_exe(program):
				return program
		else:
			for path in os.environ["PATH"].split(os.pathsep):
				path = path.strip('"')
				exe_file = os.path.join(path, program)
				if is_exe(exe_file):
					return exe_file
	 
		return None
					
program = ExecCode('/home/flypig/Documents/LJMU/Projects/AutoMarking/automark/DLJ/cmpgyate', 'temp.java', 'CourseworkTask1', 'build')
program.compile_source()
print program.execute()

