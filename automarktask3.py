# vim: et:ts=4:textwidth=80

# Automark
#
# David Llewellyn-Jones
# Liverpool John Moores University
# 18/12/2014
# Released under the GPL v.3. See the LICENSE file for more details.

"""
Check a program against task requirements.

Implements the Automark interface for task 3 of the 4001COMP Java 
programming module in 2015 at LJMU.
"""

import os
import re

from random import randint
from plyjext.model import Visitor

import automark
from execcode import ExecCode
from comments import check_comment_quality
from indentation import check_indentation

__all__ = ('Automark')


class Automark(automark.Automark):
    """
    Check Java source against the task 3 requirements.
    """

    """
    OUTPUT_CHECKS represents the number of additional checks that are 
    performed by the marking process. These will be output individually 
    to the summary csv file.
    """
    OUTPUT_CHECKS = 6

    def __init__(self, filename, credentials_file, build_dir):
        """
        Initialise the Automark class.
        
        Attributes:
            filename: The Java source file to mark.
            credentials_file: File containing username and password on 
                separate lines. The contents are ignored if the execution is 
                to be done locally. If using Sphere Engine, these should be 
                ideone credentials.
            build_dir: Temporary folder to store build and execution files.
        """
        automark.Automark.__init__(self, filename, credentials_file, build_dir)

    def setup_inputs(self):
        """
        Set up the inputs needed for marking the code.
        
        Generates random values to pass via the input.txt file and stdin.
        """
        # Establish the name of the input file
        find_file_input = InstanceCreationParam_Visitor('FileReader')
        if self._program_structure.program_tree != None:
            self._program_structure.program_tree.accept(find_file_input)

        # Replace the input file with "input.txt" so we can control it
        filename = find_file_input.get_param_list()
        if len(filename) > 0:
            transformed = re.sub(
                r'(FileReader\s*\(\s*)(' + re.escape(filename[0][0]) + 
                ')(\s*\))', r'\1"input.txt"\3', 
                self._program_structure.program)
            self._program_structure = self._program_structure._replace(
                program = transformed)

        # Establish the name of the output file
        find_file_output = InstanceCreationParam_Visitor('PrintWriter')
        if self._program_structure.program_tree != None:
            self._program_structure.program_tree.accept(find_file_output)

        # Replace the output file with "output.txt" so we can control it
        filename = find_file_output.get_param_list()
        if len(filename) > 0:
            transformed = re.sub(
                r'(PrintWriter\s*\(\s*)(' + re.escape(filename[0][0]) + 
                ')(\s*\))', r'\1"output.txt"\3', 
                self._program_structure.program)
            self._program_structure = self._program_structure._replace(
                program = transformed)

        # Generate the input file
        journey_costs = []
        input_contents = ''
        num_of_ships = randint(5,9)
        ship_ids = []
        journey_ids = []
        for ship in range(0, num_of_ships):
            ship_id = u'Boat{:d}ID'.format(randint(1000,9999))
            ship_ids.append(ship_id)
            input_contents += '{}\n'.format(ship_id)
            journey_id = u'Journey{:d}ID'.format(randint(1000, 9999))
            journey_ids.append(journey_id)
            input_contents += '{}\n'.format(journey_id)
            journey_length = randint(4, 30)
            input_contents += '{:d}\n'.format(journey_length)
            crew_num = randint(1, 10)
            input_contents += '{:d}\n'.format(crew_num)
            journey_cost = 0
            for crew_member in range(0, crew_num):
                rate = randint(20, 100) / 2.0
                input_contents += '{:.1f}\n'.format(rate)
                journey_cost += rate * journey_length
            input_contents += '\n'
            journey_costs.append(journey_cost)

        # Find median journey cost
        recommended_max = int ((journey_costs[int (num_of_ships / 2)] + 
            journey_costs[int (num_of_ships / 2) + 1]) / 2.0)

        if not os.path.exists(self._build_dir):
            os.makedirs(self._build_dir)

        file_to_write = os.path.join(self._build_dir, "input.txt")
        with open(file_to_write, 'w') as input_file:
            input_file.write(input_contents)

        stdin = '{:d}\n'.format(recommended_max)

        self._extra_program_input.append(
            ['Input from input.txt', input_contents])

        return [stdin, num_of_ships, ship_ids, journey_ids, journey_costs, 
            recommended_max]

    def check_output_correctness(self, output, inputs):
        """
        Checks whether outputs generated conform to the task requirements.
        """
        num_of_ships = inputs[1]
        ship_ids = inputs[2]
        journey_ids = inputs[3]
        journey_costs = inputs[4]
        recommended_max = inputs[5]

        execution_comments = ''
        output_check = [False, False, False, False, False, False]
        output_score = 0

        # Search for ship names and ensure they're in the right order
        ship_ids_output_dup = re.findall(r'Boat\d\d\d\dID', output)
        # Remove duplicates but retain ordering
        # From http://stackoverflow.com/questions/480214/how-do-you-remove-
        # duplicates-from-a-list-in-python-whilst-preserving-order
        seen = set()
        seen_add = seen.add
        ship_ids_output = [ x for x in ship_ids_output_dup if not (
            x in seen or seen_add(x))]

        # Search for journey names and ensure they're in the right order
        journey_ids_output_dup = re.findall(r'Journey\d\d\d\dID', output)
        # Remove duplicates but retain ordering
        # From http://stackoverflow.com/questions/480214/how-do-you-remove-
        # duplicates-from-a-list-in-python-whilst-preserving-order
        seen = set()
        seen_add = seen.add
        journey_ids_output = [ x for x in journey_ids_output_dup if not (
            x in seen or seen_add(x))]

        #print ship_ids_output
        #print ship_ids
        #print journey_ids_output
        #print journey_ids

        if len(ship_ids_output) >= len(ship_ids):
            ships_match = True
            for ship_id in range(0, len(ship_ids)):
                if ship_ids_output[ship_id] != ship_ids[ship_id]:
                    ships_match = False
        else:
            ships_match = False

        if len(journey_ids_output) >= len(journey_ids):
            journeys_match = True
            for journey_id in range(0, len(journey_ids)):
                if journey_ids_output[journey_id] != journey_ids[journey_id]:
                    journeys_match = False
        else:
            journeys_match = False

        if journeys_match:
            sections = list(journey_ids)

        if ships_match:
            sections = list(ship_ids)

        console_ships_match = ships_match or journeys_match

        if console_ships_match:
            execution_comments += ("You've correctly output all the ship "
                "journeys to the console.\n")
        else:
            execution_comments += ("You didn't output all of the journeys "
            "correctly to the console.\n")

        correct_cost_count = 0
        correct_legality_count = 0
        output_lines = output.splitlines()
        if console_ships_match:
            # Check the journey cost and viability
            journey_costs_int = [int(x) for x in journey_costs]
            correct_cost_count = Automark._check_existence_in_sections(
                output, sections, journey_costs_int)
            sections.append('defenestrate')
            section = 0
            current = sections[section]
            next = sections[section + 1]
            legal_found = False
            for line in output_lines:
                if re.search(next, line):
                    if legal_found:
                        correct_legality_count += 1
                    section += 1
                    current = next
                    next = sections[section + 1]
                legal = Automark._check_legal(line)
                if legal[0] and (legal[1] == (
                        journey_costs[section] <= recommended_max)):
                    legal_found = True;

            if legal_found:
                correct_legality_count += 1

        if correct_cost_count == num_of_ships:
            execution_comments += ('You correctly calculated and output all '
                'of the journey costs to the console.\n')
        else:
            execution_comments += ('Not all of the costs were correctly '
                'calculated and output to the console '
                '({:d} out of {:d})\n').format(
                correct_cost_count, num_of_ships)

        if correct_legality_count == num_of_ships:
            execution_comments += ('You correctly determined whether each of '
                'the ships was within cost.\n')
        else:
            execution_comments += ('You only determined whether the ships '
                'were within cosst correctly for '
                '{:d} out of the {:d} ships.\n').format(
                correct_legality_count, num_of_ships)

        #Establish the list of viable journeys
        viable_ship_ids = [j for i, j in enumerate(
            ship_ids) if journey_costs[i] <= recommended_max]
        viable_journey_ids = [j for i, j in enumerate(
            journey_ids) if journey_costs[i] <= recommended_max]
        viable_journey_costs = [
            i for i in journey_costs if i <= recommended_max]
        viable_ship_num = len(viable_ship_ids)

        # Find the highest cost lower than the maxumum recommended
        highest_index = max(enumerate(
            viable_journey_costs), key= lambda x: x[1])[0]
        highest_ship_id = viable_ship_ids[highest_index]
        highest_journey_id = viable_journey_ids[highest_index]
        highest_journey_cost = viable_journey_costs[highest_index]

        # Find whether the hightest cost below the maximum has been correctly 
        # calculated
        max_start = len(output_lines) - 1
        max_found = False
        while (not max_found) and (max_start >= 0):
            if Automark._find_keywords(
                    output_lines[max_start - 1], 
                    ['highest', 'expensive', 'maximum']):
                max_found = True
            max_start -= 1

        if max_found:
            max_found = False
            for line in output_lines[max_start:]:
                max_found |= Automark._find_keywords(
                    line, [highest_ship_id, highest_journey_id, 
                    '{:.0f}'.format(highest_journey_cost)])

        execution_comments += ('The maximum recommended journey cost entered '
            'by the user was {:d}.\n').format(recommended_max)
        execution_comments += ('The most expensive journey within this cost '
            'was {} costing {:.1f}.\n').format(
            highest_ship_id, highest_journey_cost)
        if max_found:
            execution_comments += ('Your program correctly determined this '
                'maximum journey.\n')
        else:
            execution_comments += ('Your program didn\'t correctly determine '
                'and output this.\n')

        #print '************************* STDOUT *************************'
        #print Automark.clean_text(output)

        #print '*************************  FILE  *************************'
        file_to_read = os.path.join(self._build_dir, "output.txt")
        with open(file_to_read) as output_file:
            file_output = output_file.read()
        file_output = Automark.clean_text(file_output)
        #print file_output

        # Search for ship names and ensure they're in the right order
        ship_ids_output_dup = re.findall(r'Boat\d\d\d\dID', file_output)
        # Remove duplicates but retain ordering
        # From http://stackoverflow.com/questions/480214/how-do-you-remove-
        # duplicates-from-a-list-in-python-whilst-preserving-order
        seen = set()
        seen_add = seen.add
        ship_ids_output = [ x for x in ship_ids_output_dup if not (
            x in seen or seen_add(x))]

        # Search for journey names and ensure they're in the right order
        journey_ids_output_dup = re.findall(r'Journey\d\d\d\dID', file_output)
        # Remove duplicates but retain ordering
        # From http://stackoverflow.com/questions/480214/how-do-you-remove-
        # duplicates-from-a-list-in-python-whilst-preserving-order
        seen = set()
        seen_add = seen.add
        journey_ids_output = [ x for x in journey_ids_output_dup if not (
            x in seen or seen_add(x))]

        viable_ships_match = False
        if viable_ship_ids == ship_ids_output:
            viable_ships_match = True

        viable_journeys_match = False
        if viable_journey_ids == journey_ids_output:
            viable_journeys_match = True

        if viable_journeys_match:
            sections = list(viable_journey_ids)

        if viable_ships_match:
            sections = list(viable_ship_ids)

        file_ships_match = viable_ships_match or viable_journeys_match

        if file_ships_match:
            execution_comments += ('Your program correctly listed the ships '
                'within cost in your output file.\n')
        else:
            execution_comments += ("Your program didn't correctly list the "
                "ships within cost in your output file.\n")

        viable_correct_cost_count = 0
        if file_ships_match:
            viable_journey_costs_int = [int(x) for x in viable_journey_costs]
            viable_correct_cost_count = Automark._check_existence_in_sections(
                output, sections, viable_journey_costs_int)

        if viable_correct_cost_count == viable_ship_num:
            execution_comments += ('Your program correctly output the costs '
                'for these ships.\n')
        else:
            execution_comments += ('Your program only correctly output the '
                'costs for {:d} out of {:d} of these ships.\n').format(
                viable_correct_cost_count, len(viable_journey_costs))

        output_score = 0

        if console_ships_match:
            output_score += 0.2

        if correct_cost_count == num_of_ships:
            output_score += 0.2

        if correct_legality_count == num_of_ships:
            output_score += 1.1

        if max_found:
            output_score += 1.5

        if file_ships_match:
            output_score += 0.7

        if viable_correct_cost_count == viable_ship_num:
            output_score += 0.2

        self._extra_program_output.append(
            ['Output to wagedaily.txt', file_output])

        output_check = [console_ships_match, 
            (correct_cost_count == num_of_ships), 
            (correct_legality_count == num_of_ships), 
            max_found, file_ships_match, 
            (viable_correct_cost_count == viable_ship_num)]

        return [output_score, execution_comments, output_check]

    def check_execute_result(self, result):
        """
        Assigns marks based on execution results.
        """
        output_score = 0
        if ExecCode.response_check_compiled(result):
            output_score += 1.5
        return output_score

    def check_indentation(self):
        """
        Assigns marks based on indentation quality.
        """
        result = check_indentation(self._program_structure, 7, 23)
        self._indentation_errors = result[0]
        indentation_score = result[1]
        self._error_list.extend(result[2])
        return indentation_score

    def check_comment_quality(self):
        """
        Assigns marks based on comment quality.
        """
        result = check_comment_quality(
            self._program_structure, 0.75, 0.75, 1.0, 4.0, 0.06)
        comment_score = result[0]
        self._comment_gap_average = result[1]
        self._comment_gap_sd = result[2]
        self._error_list.extend(result[3])
        return comment_score

    @staticmethod
    def _check_legal(line):
        """
        Check if a line of text relates to seaworthiness.
        
        The task requires the program to state whether the ship is too 
        heavy to sail, so check the line to find keywords that relate to 
        this.
        
        Return whether anything relevant was found. If it was, the best 
        guess as to whether it said the boat was seaworthy, or dangerous, 
        is returned.
        """
        legal_words = ['legal', 'under', 'less', 'below', 'safe', 'lighter', 
            'lower', 'acceptable']
        illegal_words = ['illegal', 'over', 'more', 'above', 'unsafe', 
            'heavier', 'greater', 'higher', 'too', 'larger', 'unacceptable']

        found_legal = False
        legal_result = False

        found = Automark._find_keywords(line, legal_words)
        if found:
            legal_result = True
            found_legal = True

        found = Automark._find_keywords(line, illegal_words)
        if found:
            legal_result = False
            found_legal = True

        return [found_legal, legal_result]

    @staticmethod
    def _find_keywords(line, words):
        """
        Search a line for any of the keywords in a list.
        
        Return True if any of the keywords are there, False otherwise.
        """
        found = False
        for keyword in words:
            if re.search(re.escape(keyword), line, re.IGNORECASE) != None:
                found = True
        return found

    @staticmethod
    def _check_existence_in_sections(output, sections, check_list):
        """
        Check whether the right output numbers are in the right sections.
        
        The task requires various details about ships to be output. As a 
        result, the output is created in sections. Usually the ship or 
        journey title is given on the first line, followed by numerical 
        details such as the hold-volume of the ship, number of containers 
        it can hold, and so on.
        
        This method looks for section titles, and if found, looks for 
        any of the numbers related to those sections.
        
        Return the number of sections correctly containing the data 
        associated with that section.
        """
        # Check the journey cost and viability
        correct_count = 0
        output_lines = output.splitlines()

        sections.append('defenestrate')
        section = 0
        current = sections[section]
        next = sections[section + 1]
        found = False
        for line in output_lines:
            if re.search(next, line):
                if found:
                    correct_count += 1
                section += 1
                current = next
                next = sections[section + 1]
            if re.search(str(check_list[section]), line):
                found = True

        if found:
            correct_count += 1

        return correct_count

    
# This doesn't confirm to PEP 8, but has been left to match 
# Java and the PLYJ API
class InstanceCreationParam_Visitor(Visitor):
    """
    Find parameter passed when creating instances in the AST.
    
    Visitor for checking the Java AST for any class instantiations of the 
    class specified. If they exist, the requested parameter passed to the 
    initialiser are recorded, along with the line number it occured on.
    """

    def __init__(self, class_name, param_num=0, verbose=False):
        """
        Initialise the InstanceCreationParam_Visitor class.
        
        Attributes:
        class_name: Name of the class to check for.
        param_num: Index of the parameter to record (default 0).
        verbose: True if the results are to be output directly.
        """
        super(InstanceCreationParam_Visitor, self).__init__()
        self._class_name = class_name
        self._param_num = param_num
        self._params = []

    def leave_InstanceCreation(self, element):
        """
        Record the details for the class instantiation.
        """
        if element.type.name.value == self._class_name:
            param = [element.arguments[self._param_num].value, element.lineno]
            self._params.append(param)
        return True
        
    def get_param_list(self):
        """
        Return the parameters found when checking the AST.
        """
        return self._params


