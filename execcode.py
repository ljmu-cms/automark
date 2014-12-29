
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
	# createSubmission(sourceCode, input)
	# return error
	
	# getSubmissionStatus()
	# return error, status, result
	
	# getSubmissionDetails(withSource, withOutput, withStderr, withCmpinfo)
	# return time, date, status, result, memory, signal, source, input, output, stderr, cmpinfo

	def __init__(self, tempfolder):
		# Establish the temp folder
		self.tempfolder = tempfolder

	def createSubmission(self, sourceCode, classname, input):
		# Store the persistent info
		self.sourceCode = sourceCode
		self.input = input
		self.classname = classname

		# Create the temp folder if it doesn't already exist
		if not os.path.exists(self.tempfolder):
			os.makedirs(self.tempfolder)

		# Create the temporary source file to build based on the source code provided
		self.tempsource = os.path.join(self.tempfolder, 'temp2.java')
		with open(self.tempsource, 'w') as file:
			file.write(sourceCode)

		submission = self.Submission()
		submission.run()


	def getSubmissionStatus(self):
		 pass


	def compile_source(self):
		result = False
		output = ''
		if ExecCode.which('javac') == None:
			output = 'Java compiler javac could not be found'
		else:
			program = subprocess.Popen(['javac', '-sourcepath', self.tempfolder, '-d', self.tempfolder, self.tempsource], shell=False, cwd='.', stderr=subprocess.STDOUT, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
			output = program.stdout.read()
			program.communicate()
			result = program.returncode

		return [result, output]

	def execute(self):
		output = ''
		if ExecCode.which('java') == None:
			print 'Java VM could not be found'
		else:
			program = subprocess.Popen(['java', self.classname], shell=False, cwd=self.tempfolder, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
			program.stdin.write(self.input)
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

	import threading
	class Submission(threading.Thread):
		def __init__(self):
			self.error = 'OK'
			self.status = ''
			self.result = ''
			self.updateStatus = ExecCode.threading.Lock()
			pass

		def run(self):
			print 'Hello thread'

		def setSubmissionStatus(self, error, status, result):
			self.updateStatus.acquire()
			self.error = error
			self.status = status
			self.result = result
			self.updateStatus.release()

		def getSubmissionStatus(self):
			self.updateStatus.acquire()
			status = {'error': self.error, 'status': self.status, 'result': self.result}
			self.updateStatus.release()
			return status


program = ExecCode('build')

sourceCode = ''
with  open('/home/flypig/Documents/LJMU/Projects/AutoMarking/automark/DLJ/cmpgyate/temp.java') as file:
	sourceCode = file.read()
program.createSubmission(sourceCode, 'CourseworkTask1', '10\n11\n12\n')
program.compile_source()
print program.execute()

