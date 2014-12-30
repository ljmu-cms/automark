
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
import time
import collections

Status = collections.namedtuple('Status', ['key', 'value'])

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
		self.status = 0

		# Create the temp folder if it doesn't already exist
		if not os.path.exists(self.tempfolder):
			os.makedirs(self.tempfolder)

		# Create the temporary source file to build based on the source code provided
		self.tempsource = os.path.join(self.tempfolder, 'temp2.java')
		with open(self.tempsource, 'w') as file:
			file.write(sourceCode)

		self.submission = self.Submission(self.tempfolder, self.tempsource, 'CourseworkTask1', '10\n11\n12\n')
		self.status = 1
		self.submission.start()

	def getSubmissionStatus(self):
		if self.status == 0:
			status = {'item': [Status('error', 'OK'), Status('status', -1), Status('result', 0)]}
		else:
			status = self.submission.getSubmissionStatus()
		return status

	def getSubmissionDetails(self, withSource, withInput, withOutput, withStderr, withCmpinfo):
		if self.status == 0:
			status = {'error': 'FAIL'}
		else:
			status = self.submission.getSubmissionDetails(withSource, withInput, withOutput, withStderr, withCmpinfo)
		if withSource:
			status['item'].append(Status('source', self.sourceCode))
		return status

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
		def __init__(self, tempfolder, tempsource, classname, input):
			self.error = 'OK'
			self.status = -1
			self.result = 0
			self.updateStatus = ExecCode.threading.Lock()
			self.tempfolder = tempfolder
			self.tempsource = tempsource
			self.classname = classname
			self.input = input
			self.cmpinfo = ''
			self.timeStart = 0
			self.timeEnd = 0
			self.date = ''
			self.compileResult = [0, '']
			self.execResult = [0, '', '']
			ExecCode.threading.Thread.__init__(self)

		def run(self):
			self.date = time.strftime('%Y-%m-%d %H-%M-%S')
			self.compileResult = self.compile_source(self.tempfolder, self.tempsource)
			if self.compileResult[0] != 0:
				self.cmpinfo = self.compileResult[1]
				self.setSubmissionStatus('OK', 0, 11)
			else:
				self.cmpinfo = ''
				self.setSubmissionStatus('OK', 3, 0)
				self.execResult = self.execute(self.tempfolder, self.classname, self.input)
				self.output = self.execResult[1]
				self.stderr = self.execResult[2]
				if self.execResult[0] != 0:
					self.setSubmissionStatus('OK', 0, 12)
				else:
					self.setSubmissionStatus('OK', 0, 15)

		def setSubmissionStatus(self, error, status, result):
			self.updateStatus.acquire()
			self.error = error
			self.status = status
			self.result = result
			self.updateStatus.release()

		# Status
		# < 0 - waiting for compilation - the submission awaits execution in the queue
		#   0 - done - the program has finished
		#   1 - compilation - the program is being compiled
		#   3 - running - the program is being executed
		
		# Result
		#   0 - not running - the submission has been created with run parameter set to false
		#  11 - compilation error - the program could not be executed due to compilation error
		#  12 - runtime error - the program finished because of the runtime error, for example: division by zero, array index out of bounds, uncaught exception
		#  13 - time limit exceeded - the program didn't stop before the time limit
		#  15 - success - everything went ok
		#  17 - memory limit exceeded - the program tried to use more memory than it is allowed to
		#  19 - illegal system call - the program tried to call illegal system function
		#  20 - internal error - some problem occurred; try to submit the program again

		def getSubmissionStatus(self):
			self.updateStatus.acquire()
			status = {'item': [Status('error', self.error), Status('status', self.status), Status('result', self.result)]}
			self.updateStatus.release()
			return status

		def getSubmissionDetails(self, withSource, withInput, withOutput, withStderr, withCmpinfo):
			details = {'item': []}
			details['item'].append(Status('error', self.error))
			details['item'].append(Status('time', (self.timeEnd - self.timeStart)))
			details['item'].append(Status('date', self.date))
			details['item'].append(Status('status', self.status))
			details['item'].append(Status('result', self.result))
			details['item'].append(Status('memory', 0))
			details['item'].append(Status('signal', self.execResult[0]))
			details['item'].append(Status('public', False))
			if withInput:
				details['item'].append(Status('input', self.input))
			if withOutput:
				details['item'].append(Status('output', self.execResult[1]))
			if withStderr:
				details['item'].append(Status('stderr', self.execResult[2]))
			if withCmpinfo:
				details['item'].append(Status('cmpinfo', self.cmpinfo))
			return details

		def compile_source(self, tempfolder, tempsource):
			result = False
			output = ''
			if ExecCode.which('javac') == None:
				output = 'Java compiler javac could not be found'
				self.setSubmissionStatus('OK', 0, 20)
			else:
				self.setSubmissionStatus('OK', 1, 0)
				program = subprocess.Popen(['javac', '-sourcepath', tempfolder, '-d', tempfolder, tempsource], shell=False, cwd='.', stderr=subprocess.STDOUT, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
				output = program.stdout.read()
				program.communicate()
				result = program.returncode
				if result == 0:
					# Compilation error
					self.setSubmissionStatus('OK', 0, 11)
				else:
					# Compilation success
					self.setSubmissionStatus('OK', 3, 0)
			return [result, output]

		def execute(self, tempfolder, classname, input):
			output = ''
			if ExecCode.which('java') == None:
				print 'Java VM could not be found'
				self.setSubmissionStatus('OK', 1, 0)
			else:
				self.timeStart = time.time()
				program = subprocess.Popen(['java', classname], shell=False, cwd=tempfolder, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
				program.stdin.write(input)
				output = program.stdout.read()
				error = program.stderr.read()
				result = program.returncode
				self.timeEnd = time.time()
			return [result, output, error]
	 
def getValue(response, key):
	value = ''
	for item in response['item']:
		if item.key == key:
			value = item.value
	return value

def checkSubmissionsStatus(status):
	if status < 0:
		print 'Waiting for compilation'
	elif status == 1:
		print 'Compiling'
	elif status == 3:
		print 'Running'


#program = ExecCode('build')
#sourceCode = ''
#with open('/home/flypig/Documents/LJMU/Projects/AutoMarking/automark/DLJ/cmpgyate/temp.java') as file:
#	sourceCode = file.read()
#program.createSubmission(sourceCode, 'CourseworkTask1', '10\n11\n12\n')
#status = -1;
#waitTime = 0
#while status != 0:
#	time.sleep(waitTime)
#	waitTime = 0.1
#	response = program.getSubmissionStatus()
#	status = getValue(response, 'status')
#	checkSubmissionsStatus (status)
#details = program.getSubmissionDetails(True, True, True, True, True)
#print getValue(details, 'output')


