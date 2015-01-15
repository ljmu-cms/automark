#!/usr/bin/env python
# vim: et:ts=4:textwidth=80
"""
execcode

David Llewellyn-Jones
Liverpool John Moores University
18/12/2014
Execute code with given inputs and return the outputs
"""

import sys
import os
from subprocess import PIPE, Popen, STDOUT
import time
import collections
import shutil
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

Status = collections.namedtuple('Status', ['key', 'value'])
ON_POSIX = 'posix' in sys.builtin_module_names

class ExecCode:
    'Compile and execute a piece of code so it can be evaluted'
    # user and password are ignored in this implementation

    # createSubmission(sourceCode, input)
    # return error
    
    # getSubmissionStatus()
    # return error, status, result
    
    # getSubmissionDetails(withSource, withOutput, withStderr, withCmpinfo)
    # return time, date, status, result, memory, signal, source, input, output, stderr, cmpinfo

    def __init__(self, tempfolder, classname):
        'Create a new instane of ExecCode(tempfolder)'
        # Establish the temp folder
        self.tempfolder = tempfolder
        self.classname = classname
        self.tempsourceleaf = classname + '.java'

    def createSubmission(self, user, password, sourceCode, language, input, run, private):
        'Create a new piece of code to be compiled and executed'
        # Store the persistent info
        self.sourceCode = sourceCode
        self.input = input
        self.status = 0
        self.date = time.strftime('%Y-%m-%d %H-%M-%S')

        # Create the temp folder if it doesn't already exist
        if not os.path.exists(self.tempfolder):
            os.makedirs(self.tempfolder)
        if not os.path.exists(self.tempfolder + '/uk'):
            shutil.copytree('java/uk', self.tempfolder + '/uk')

        # Create the temporary source file to build based on the source code provided
        self.tempsource = os.path.join(self.tempfolder, self.tempsourceleaf)
        ExecCode.tidyup(self.tempfolder)
        with open(self.tempsource, 'w') as file:
            file.write(sourceCode)

        # Set up details of the submission in the sub-thread
        self.submission = self.Submission(self.tempfolder, self.tempsource, self.classname, input)
        self.status = 1
        # Spawn the sub-thread to perform compilation and execution of the submission
        self.submission.start()
        status = {'item': [Status('error', 'OK'), Status('link', 0)]}

        return status

    def getSubmissionStatus(self, user, password, link):
        'Get the status of the code submission'
        if self.status == 0:
            # The compilation/execution sub-thread hasn't been spawned yet, so we construct the response ourselves
            status = {'item': [Status('error', 'OK'), Status('status', -1), Status('result', 0)]}
        else:
            # Get the response from the compilation/executionsub-thread
            status = self.submission.getSubmissionStatus()
        return status

    def getSubmissionDetails(self, user, password, link, withSource, withInput, withOutput, withStderr, withCmpinfo):
        'Get detailed information about a submission compilation and execution'
        if self.status == 0:
            # The compilation/execution sub-thread hasn't been spawned yet, so we construct the response ourselves
            details = {'item': []}
            details['item'].append(Status('error', 'OK'))
            details['item'].append(Status('time', 0))
            details['item'].append(Status('status', -1))
            details['item'].append(Status('result', 0))
            details['item'].append(Status('memory', 0))
            details['item'].append(Status('signal', 0))
            details['item'].append(Status('public', False))
            if withInput:
                details['item'].append(Status('input', self.input))
            if withOutput:
                details['item'].append(Status('output', ''))
            if withStderr:
                details['item'].append(Status('stderr', ''))
            if withCmpinfo:
                details['item'].append(Status('cmpinfo', ''))
        else:
            # Get the response from the compilation/executionsub-thread
            details = self.submission.getSubmissionDetails(withSource, withInput, withOutput, withStderr, withCmpinfo)
        details['item'].append(Status('date', self.date))
        if withSource:
            details['item'].append(Status('source', self.sourceCode))
        return details

    @staticmethod
    def getValue(response, key):
        'Helper function to extract a value from the return data for the given key'
        value = ''
        # Find the item with the appropriate key
        for item in response['item']:
            if item.key == key:
                # Return the value for this item
                value = item.value
        return value

    @staticmethod
    def checkSubmissionsStatus(status):
        'Print out a status string based on the status number'
        if status < 0:
            print 'Waiting for compilation'
        elif status == 1:
            print 'Compiling'
        elif status == 3:
            print 'Running'

    #http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    @staticmethod
    def which(program):
        'Check whether a given executable exists'
        def is_exe(fpath):
            # Establish whether the file is executablee
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
     
        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                # The file exists and is executable
                return program
        else:
            # Check the PATH environment variable
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    # the path is executable and has the correct name
                    return exe_file
        # Couldn't find the executable either directly or in the path     
        return None

    @staticmethod
    def responseCheckCompiled(response):
        compiled = False
        if response >= 12:
            compiled = True
        return compiled

    @staticmethod
    def tidyup(tempfolder):
        for file in os.listdir(tempfolder):
            extension = os.path.splitext(file)[1]
            if (extension == '.class') or (extension == '.java'):
                path = os.path.join(tempfolder, file)
                os.remove(path)

    import threading
    class Submission(threading.Thread):
        'Threading class to allow compilation and execution in parallel with other tasks'
        def __init__(self, tempfolder, tempsource, classname, input):
            'Initialise the thread'
            # Set up the initial variable values that the thread needss
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
            self.maxexectime = 3.0
            ExecCode.threading.Thread.__init__(self)

        def run(self):
            'The thread entry point'
            # Compile the source file
            self.compileResult = self.compile_source(self.tempfolder, self.tempsource)
            if self.compileResult[0] != 0:
                # The compilation failed, so just return the output from the compilation
                self.cmpinfo = self.compileResult[1]
                self.setSubmissionStatus('OK', 0, 11)
            else:
                # The compilation was successful
                self.cmpinfo = ''
                self.setSubmissionStatus('OK', 3, 0)
                # Execute the resulting Java class file
                self.execResult = self.execute(self.tempfolder, self.classname, self.input)
                # Capture the returned output from the execution
                self.output = self.execResult[1]
                self.stderr = self.execResult[2]
                if self.execResult[0] != 0:
                    # The execuation failed, so note the details
                    self.setSubmissionStatus('OK', 0, 12)
                else:
                    if self.timelimitexceeded:
                        # The execution took too long
                        self.setSubmissionStatus('OK', 0, 13)
                    else:
                        # The execuation was successful
                        self.setSubmissionStatus('OK', 0, 15)

        def setSubmissionStatus(self, error, status, result):
            'For internal use. Sets the status info for a given submssion.'
            # Ensure only one thread can read/write the details simultaneously by acquring a lock
            self.updateStatus.acquire()
            # Set the details
            self.error = error
            self.status = status
            self.result = result
            # Release the lock
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
            'For internal use. Gets status info about a given submssion.'
            # Ensure only one thread can read/write the details simultaneously by acquring a lock
            self.updateStatus.acquire()
            # Structure the data appropriately
            status = {'item': [Status('error', self.error), Status('status', self.status), Status('result', self.result)]}
            # Release the lock
            self.updateStatus.release()
            return status

        def getSubmissionDetails(self, withSource, withInput, withOutput, withStderr, withCmpinfo):
            'For internal use. Gets details of a completed submssion.'
            details = {'item': []}
            details['item'].append(Status('error', self.error))
            details['item'].append(Status('time', (self.timeEnd - self.timeStart)))
            details['item'].append(Status('status', self.status))
            details['item'].append(Status('result', self.result))
            details['item'].append(Status('memory', 0))
            details['item'].append(Status('signal', self.execResult[0]))
            details['item'].append(Status('public', False))
            # Some of the return key-value pairs are optional
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
            'For internal use. Compiles the java source code.'
            result = False
            output = ''
            if ExecCode.which('javac') == None:
                # The Java compiler couldn't be found
                output = 'Java compiler javac could not be found'
                self.setSubmissionStatus('OK', 0, 20)
            else:
                # The Java compiler is present
                self.setSubmissionStatus('OK', 1, 0)
                # Execuate the compilation as a subprocess
                program = Popen(['javac', '-classpath', tempfolder, '-sourcepath', tempfolder, '-d', tempfolder, tempsource], shell=False, cwd='.', stderr=STDOUT, stdin=PIPE, stdout=PIPE)
                # Collect any outputs from the compilation process
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
            'For internal use. Executes the java source code.'
            output = ''
            if ExecCode.which('java') == None:
                # The Java VM could not be found
                print 'Java VM could not be found'
                self.setSubmissionStatus('OK', 1, 0)
            else:
                # The Java VM is present
                self.timeStart = time.time()
                # Execute the compiled code as a subprocess
                program = Popen(['java', classname], shell=False, cwd=tempfolder, bufsize=1, stderr=PIPE, stdin=PIPE, stdout=PIPE, close_fds=ON_POSIX)
                outputQueue = Queue()
                outputCollector = ExecCode.threading.Thread(target=ExecCode.Submission.enqueue_output, args=(program.stdout, outputQueue))
                outputCollector.daemon = True
                outputCollector.start()
                # Pass the input to the running code
                program.stdin.write(input)
                # Collect any output form the the running code
                output = ''
                exectime = 0.0
                result = None
                self.timelimitexceeded = False
                while (result == None) and not self.timelimitexceeded:
                    program.poll()
                    try:
                        line = outputQueue.get_nowait()
                    except Empty:
                        # No output, wait a bit and check again
                        time.sleep(0.1)
                        result = program.returncode
                    else:
                        # We caught some output, so record it
                        output += line
                    # Check how long the program's been running for
                    exectime = time.time() - self.timeStart
                    if exectime >= self.maxexectime:
                        # Too long!
                        self.timelimitexceeded = True

                if self.timelimitexceeded:
                    program.kill()
                error = program.stderr.read()
                result = program.returncode
                if result == None:
                    result = 0
                self.timeEnd = time.time()
            return [result, output.decode("utf-8"), error.decode("utf-8")]

        # http://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python
        @staticmethod
        def enqueue_output(out, queue):
                for line in iter(out.readline, b''):
                    queue.put(line)
                out.close()


#program = ExecCode('build', 'CourseworkTask1')
#sourceCode = ''
#with open('/home/flypig/Documents/LJMU/Projects/AutoMarking/automark/DLJ/cmpgyate/temp.java') as file:
#    sourceCode = file.read()
#program.createSubmission('', '', sourceCode, 11, '10\n11\n12\n', True, True)
#status = -1;
#waitTime = 0
#while status != 0:
#    time.sleep(waitTime)
#    waitTime = 0.1
#    response = program.getSubmissionStatus('', '', '')
#    status = ExecCode.getValue(response, 'status')
#    ExecCode.checkSubmissionsStatus (status)
#details = program.getSubmissionDetails('', '', '', True, True, True, True, True)
#print ExecCode.getValue(details, 'output')


