#!/usr/bin/env python 
"""
automark

David Llewellyn-Jones
Liverpool John Moores University
18/12/2014
Check a program against task requirements

This script allows a program to be checked using the ideone api.
"""

import automark
import random
import re
import plyjext.model as model
import os
import math
import string

class Automark(automark.Automark):
	outputChecks = 6

	def __init__(self, filename, credentialsFile, build_dir):
		automark.Automark.__init__(self, filename, credentialsFile, build_dir)

	def setupInputs(self):
		# Establish the name of the input file
		findFileInput = InstanceCreationParamVisitor('FileReader')
		if self.programStructure.programTree != None:
			self.programStructure.programTree.accept(findFileInput)

		# Replace the input file with "input.txt" so we can control it
		filename = findFileInput.getParamList()
		if len(filename) > 0:
			transformed = re.sub(r'(FileReader\s*\(\s*)(' + re.escape(filename[0][0]) + ')(\s*\))', r'\1"input.txt"\3', self.programStructure.program)
			self.programStructure = self.programStructure._replace(program = transformed)

		# Establish the name of the output file
		findFileOutput = InstanceCreationParamVisitor('PrintWriter')
		if self.programStructure.programTree != None:
			self.programStructure.programTree.accept(findFileOutput)

		# Replace the output file with "output.txt" so we can control it
		filename = findFileOutput.getParamList()
		if len(filename) > 0:
			transformed = re.sub(r'(PrintWriter\s*\(\s*)(' + re.escape(filename[0][0]) + ')(\s*\))', r'\1"output.txt"\3', self.programStructure.program)
			self.programStructure = self.programStructure._replace(program = transformed)



		# Generate the input file
		journeyCosts = []
		inputContents = ''
		numOfShips = random.randint(5,9)
		shipIDs = []
		journeyIDs = []
		for ship in range(0, numOfShips):
			shipID = u'XshipY{:d}Z'.format(random.randint(1000,9999))
			shipIDs.append(shipID)
			inputContents += '{}\n'.format(shipID)
			journeyID = u'XjourneyY{:d}Z'.format(random.randint(1000, 9999))
			journeyIDs.append(journeyID)
			inputContents += '{}\n'.format(journeyID)
			journeyLength = random.randint(4, 30)
			inputContents += '{:d}\n'.format(journeyLength)
			crewNum = random.randint(1, 10)
			inputContents += '{:d}\n'.format(crewNum)
			journeyCost = 0
			for crewMember in range(0, crewNum):
				rate = random.randint(100, 500) / 10.0
				inputContents += '{:.1f}\n'.format(rate)
				journeyCost += rate * journeyLength
			inputContents += '\n'
			journeyCosts.append(journeyCost)

		# Find median journey cost
		recommendedMax = int ((journeyCosts[int (numOfShips / 2)] + journeyCosts[int (numOfShips / 2) + 1]) / 2.0)

		if not os.path.exists(self.build_dir):
			os.makedirs(self.build_dir)

		fileToWrite = os.path.join(self.build_dir, "input.txt")
		with open(fileToWrite, 'w') as inputFile:
			inputFile.write(inputContents)

		stdin = '{:d}\n'.format(recommendedMax)

		return [stdin, numOfShips, shipIDs, journeyIDs, journeyCosts, recommendedMax]

	@staticmethod
	def check_legal(line):
		legal_words = ['legal', 'under', 'less', 'below', 'safe', 'lighter', 'lower', 'acceptable']
		illegal_words = ['illegal', 'over', 'more', 'above', 'unsafe', 'heavier', 'greater', 'higher', 'too', 'larger', 'unacceptable']

		found_legal = False
		legal_result = False

		found = Automark.find_keywords(line, legal_words)
		if found:
			legal_result = True
			found_legal = True

		found = Automark.find_keywords(line, illegal_words)
		if found:
			legal_result = False
			found_legal = True

		return [found_legal, legal_result]

	@staticmethod
	def find_keywords(line, words):
		found = False
		for keyword in words:
			if re.search(re.escape(keyword), line, re.IGNORECASE) != None:
				found = True
		return found

	@staticmethod
	def checkExistenceInSections(output, sections, checkList):
		# Check the journey cost and viability
		correctCount = 0
		outputLines = output.splitlines()

		sections.append('defenestrate')
		section = 0
		current = sections[section]
		next = sections[section + 1]
		found = False
		for line in outputLines:
			if re.search(next, line):
				if found:
					correctCount += 1
				section += 1
				current = next
				next = sections[section + 1]
			if re.search(str(checkList[section]), line):
				found = True

		if found:
			correctCount += 1

		return correctCount
	
	def checkOutputCorrectness(self, output, inputs):
		numOfShips = inputs[1]
		shipIDs = inputs[2]
		journeyIDs = inputs[3]
		journeyCosts = inputs[4]
		recommendedMax = inputs[5]

		executionComments = ''
		outputCheck = [False, False, False, False, False, False]
		outputScore = 0

		# Search for ship names and ensure they're in the right order
		shipIDsOutput_dup = re.findall(r'XshipY\d\d\d\dZ', output)
		# Remove duplicates but retain ordering
		# From http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
		seen = set()
		seen_add = seen.add
		shipIDsOutput = [ x for x in shipIDsOutput_dup if not (x in seen or seen_add(x))]

		# Search for journey names and ensure they're in the right order
		journeyIDsOutput_dup = re.findall(r'XjourneyY\d\d\d\dZ', output)
		# Remove duplicates but retain ordering
		# From http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
		seen = set()
		seen_add = seen.add
		journeyIDsOutput = [ x for x in journeyIDsOutput_dup if not (x in seen or seen_add(x))]


		#print shipIDsOutput
		#print shipIDs
		#print journeyIDsOutput
		#print journeyIDs



		if len(shipIDsOutput) >= len(shipIDs):
			shipsMatch = True
			for shipID in range(0, len(shipIDs)):
				if shipIDsOutput[shipID] != shipIDs[shipID]:
					shipsMatch = False
		else:
			shipsMatch = False

		if len(journeyIDsOutput) >= len(journeyIDs):
			journeysMatch = True
			for journeyID in range(0, len(journeyIDs)):
				if journeyIDsOutput[journeyID] != journeyIDs[journeyID]:
					journeysMatch = False
		else:
			journeysMatch = False

		if journeysMatch:
			sections = list(journeyIDs)

		if shipsMatch:
			sections = list(shipIDs)

		consoleShipsMatch = shipsMatch or journeysMatch

		if consoleShipsMatch:
			executionComments += 'You\'ve correctly output all the ship journeys to the console.\n'
		else:
			executionComments += 'You didn\'t output all of the journeys correctly to the console.\n'

		correctCostCount = 0
		correctLegalityCount = 0
		outputLines = output.splitlines()
		if consoleShipsMatch:
			# Check the journey cost and viability
			correctCostCount = Automark.checkExistenceInSections(output, sections, journeyCosts)
			sections.append('defenestrate')
			section = 0
			current = sections[section]
			next = sections[section + 1]
			legalFound = False
			for line in outputLines:
				if re.search(next, line):
					if legalFound:
						correctLegalityCount += 1
					section += 1
					current = next
					next = sections[section + 1]
				legal = Automark.check_legal(line)
				if legal[0] and (legal[1] == (journeyCosts[section] <= recommendedMax)):
					legalFound = True;

			if legalFound:
				correctLegalityCount += 1

		if correctCostCount == numOfShips:
			executionComments += 'You correctly calculated and output all of the journey costs to the console.\n'
		else:
			executionComments += 'Not all of the costs were correctly calculated and output to the console ({:d} out of {:d})\n'.format(correctCostCount, numOfShips)

		if correctLegalityCount == numOfShips:
			executionComments += 'You correctly determined whether each of the ships was within cost.\n'
		else:
			executionComments += 'You only determined whether the ships were within cosst correctly for {:d} out of the {:d} ships.\n'.format(correctLegalityCount, numOfShips)

		#Establish the list of viable journeys
		viableShipIDs = [j for i, j in enumerate(shipIDs) if journeyCosts[i] <= recommendedMax]
		viableJourneyIDs = [j for i, j in enumerate(journeyIDs) if journeyCosts[i] <= recommendedMax]
		viableJourneyCosts = [i for i in journeyCosts if i <= recommendedMax]
		viableShipNum = len(viableShipIDs)

		# Find the highest cost lower than the maxumum recommended
		highestIndex = max(enumerate(viableJourneyCosts), key= lambda x: x[1])[0]
		highestShipID = viableShipIDs[highestIndex]
		highestJourneyID = viableJourneyIDs[highestIndex]
		highestJourneyCost = viableJourneyCosts[highestIndex]

		# Find whether the hightest cost below the maximum has been correctly calculated
		maxStart = len(outputLines) - 1
		maxFound = False
		while (not maxFound) and (maxStart >= 0):
			if Automark.find_keywords(outputLines[maxStart - 1], ['highest', 'expensive', 'maximum']):
				maxFound = True
			maxStart -= 1

		if maxFound:
			maxFound = False
			for line in outputLines[maxStart:]:
				maxFound |= Automark.find_keywords(line, [highestShipID, highestJourneyID, '{:.0f}'.format(highestJourneyCost)])

		executionComments += 'The maximum recommended journey cost entered by the user was {:d}.\n'.format(recommendedMax)
		executionComments += 'The most expensive journey within this cost was {} costing {:.1f}.\n'.format(highestShipID, highestJourneyCost)
		if maxFound:
			executionComments += 'Your program correctly determined this maximum journey.\n'
		else:
			executionComments += 'Your program didn\'t correctly determine and output this.\n'


		#print '************************* STDOUT *************************'
		#print Automark.clean_text(output)

		#print '*************************  FILE  *************************'
		fileToRead = os.path.join(self.build_dir, "output.txt")
		with open(fileToRead) as outputFile:
			fileOutput = outputFile.read()
		fileOutput = Automark.clean_text(fileOutput)
		#print fileOutput

		# Search for ship names and ensure they're in the right order
		shipIDsOutput_dup = re.findall(r'XshipY\d\d\d\dZ', fileOutput)
		# Remove duplicates but retain ordering
		# From http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
		seen = set()
		seen_add = seen.add
		shipIDsOutput = [ x for x in shipIDsOutput_dup if not (x in seen or seen_add(x))]

		# Search for journey names and ensure they're in the right order
		journeyIDsOutput_dup = re.findall(r'XjourneyY\d\d\d\dZ', fileOutput)
		# Remove duplicates but retain ordering
		# From http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
		seen = set()
		seen_add = seen.add
		journeyIDsOutput = [ x for x in journeyIDsOutput_dup if not (x in seen or seen_add(x))]


		viableShipsMatch = False
		if viableShipIDs == shipIDsOutput:
			viableShipsMatch = True

		viableJourneysMatch = False
		if viableJourneyIDs == journeyIDsOutput:
			viableJourneysMatch = True

		if viableJourneysMatch:
			sections = list(viableJourneyIDs)

		if viableShipsMatch:
			sections = list(viableShipIDs)

		fileShipsMatch = viableShipsMatch or viableJourneysMatch

		if fileShipsMatch:
			executionComments += 'Your program correctly listed the ships within cost in your output file.\n'
		else:
			executionComments += 'Your program didn\'t correctly list the ships within cost in your output file.\n'

		viableCorrectCostCount = 0
		if fileShipsMatch:
			viableCorrectCostCount = Automark.checkExistenceInSections(output, sections, viableJourneyCosts)

		if viableCorrectCostCount == viableShipNum:
			executionComments += 'Your program correctly output the costs for these ships.\n'
		else:
			executionComments += 'Your program only correctly output the costs for {:d} out of {:d} of these ships.\n'.format(viableCorrectCostCount, len(viableJourneyCosts))

		outputScore = 0

		if consoleShipsMatch:
			outputScore += 1

		if correctCostCount == numOfShips:
			outputScore += 1

		if correctLegalityCount == numOfShips:
			outputScore += 1

		if maxFound:
			outputScore += 1

		if fileShipsMatch:
			outputScore += 1

		if viableCorrectCostCount == viableShipNum:
			outputScore += 1

		outputCheck = [consoleShipsMatch, (correctCostCount == numOfShips), (correctLegalityCount == numOfShips), maxFound, fileShipsMatch, (viableCorrectCostCount == viableShipNum)]

		return [outputScore, executionComments, outputCheck]

class InstanceCreationParamVisitor(model.Visitor):
	def __init__(self, className, paramNum=0, verbose=False):
		super(InstanceCreationParamVisitor, self).__init__()
		self.className = className
		self.paramNum = paramNum
		self.params = []

	def leave_InstanceCreation(self, element):
		if element.type.name.value == self.className:
			param = [element.arguments[self.paramNum].value, element.lineno]
			self.params.append(param)
		return True
		
	def getParamList(self):
		return self.params


