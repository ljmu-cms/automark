# vim: et:ts=4:textwidth=80

# Automark
#
# David Llewellyn-Jones
# Liverpool John Moores University
# 18/12/2014
# Released under the GPL v.3. See the LICENSE file for more details.

"""
Check a program against task requirements.

Implements the Automark interface for task 4 of the 4001COMP Java 
programming module in 2015 at LJMU.
"""

import os
import re

from random import randint
from plyjext.model import Visitor, Literal

import automark
from execcode import ExecCode
from comments import check_comment_quality
from indentation import check_indentation
from variables import check_variable_name_quality

__all__ = ('Automark')


class Automark(automark.Automark):
    """
    Check Java source against the task 4 requirements.
    """

    """
    OUTPUT_CHECKS represents the number of additional checks that are 
    performed by the marking process. These will be output individually 
    to the summary csv file.
    """
    OUTPUT_CHECKS = 3

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
        # Find the username, password and account name
	    find_vars = Field_Visitor()
	    if self._program_structure.program_tree != None:
		    self._program_structure.program_tree.accept(find_vars)

        self._username = ""
        self._password = ""
        self._account_number = ""
        for var in find_vars.variables:
            if re.search(re.escape("pass"), var[1], re.IGNORECASE) != None:
                self._password = var[2].strip('"')
            if re.search(re.escape("name"), var[1], re.IGNORECASE) != None:
                self._username = var[2].strip('"')
            if re.search(re.escape("numb"), var[1], re.IGNORECASE) != None:
                self._account_number = var[2].strip('"')

        #print self._username
        #print self._password
        #print self._account_number
	    find_vars = Variable_Visitor()
	    if self._program_structure.program_tree != None:
		    self._program_structure.program_tree.accept(find_vars)

        for var in find_vars.variables:
            if not self._password:
                if re.search(re.escape("pass"), var[1], re.IGNORECASE) != None:
                    self._password = var[2].strip('"')
            if not self._username:
                if re.search(re.escape("name"), var[1], re.IGNORECASE) != None:
                    self._username = var[2].strip('"')
            if not self._account_number:
                if re.search(re.escape("numb"), var[1], re.IGNORECASE) != None:
                    self._account_number = var[2].strip('"')

        #print self._username
        #print self._password
        #print self._account_number

        # Clear out the folder
        # Remove any files with .txt or .dat extensions
        for file in os.listdir(self._build_dir):
            extension = os.path.splitext(file)[1]
            if (extension == '.txt') or (extension == '.dat'):
                path = os.path.join(self._build_dir, file)
                os.remove(path)

        # Create a port-account.txt file
        file_to_write = os.path.join(self._build_dir, "port-account.txt")
        with open(file_to_write, 'w') as input_file:
            input_file.write("1000\n")

        # Create a transaction-list.txt file
        file_to_write = os.path.join(self._build_dir, "transaction-list.txt")
        with open(file_to_write, 'w') as input_file:
            input_file.write("")


        # Establish the name of the account input/output file
        # Establish the name of the transaction input/output file

        # Create the value to be passed on stdin
        stdin = ""
        menus = 0

        # Login to the account system
        stdin += "{}\n{}\n".format(self._account_number, self._password)
        menus += 1

        # Output the current balance
        stdin += "3\n"
        menus += 1

        transactions = []
        # Perform seven 1 unit transactions
        for trans_num in range(0, 7):
            stdin += "1\n"
            menus += 1
            transfer = 1
            transactions.append(transfer)
            stdin += "{:d}\n".format(transfer)

        # Perform six random transactions
        for trans_num in range(0, 6):
            stdin += "1\n"
            menus += 1
            transfer = randint(1 + trans_num, 1 + (trans_num * 2))
            transactions.append(transfer)
            stdin += "{:d}\n".format(transfer)

        # Perform a large transaction
        stdin += "1\n"
        menus += 1
        transfer = 1000000
        transactions.append(transfer)
        stdin += "{:d}\n".format(transfer)

        # Output the current balance
        stdin += "3\n"
        menus += 1

        # Output recent transactions
        stdin += "2\n"
        menus += 1

        # Logout
        stdin += "4\n"

        return [stdin, transactions, menus]

    def check_output_correctness(self, output, inputs):
        """
        Checks whether outputs generated conform to the task requirements.
        """
        transactions = inputs[1]
        menus = inputs[2]
        output_score = 0
        execution_comments = ''
        output_check = []
        
        # Figure out a line from the menu
        output_lines = output.splitlines()
        line_num = 0
        found_menu_start = False
        menu_start = ""
        while (line_num < len(output_lines)) and not found_menu_start:
            menu_start = output_lines[line_num]
            if len(menu_start) > 3:
                found = 0
                for line in output_lines:
                    if menu_start == line:
                        found += 1
                if found >= (menus - 1):
                    #print menu_start
                    found_menu_start = True
            line_num += 1

        line_num = len(output_lines) - 1
        menu_end = ""
        found_menu_end = False
        while (line_num >= 0) and not found_menu_end:
            menu_end = output_lines[line_num]
            if re.search(r'\d+', menu_end) != None:
                option = int(re.search(r'\d+', menu_end).group())
                if (len(menu_end) > 3) and (option >= 0) and (option <= 10):
                    found = 0
                    for line in output_lines:
                        if menu_end == line:
                            found += 1
                    if found >= (menus - 1):
                        #print menu_end
                        found_menu_end = True
            line_num -= 1
            
        # Split the output into sections
        section_num = 0
        sections = []
        sections.append([])
        in_menu = False
        for line in output_lines:
            if line == menu_start:
                in_menu = True
            if not in_menu:
                sections[section_num].append(line)
            if line == menu_end:
                section_num += 1
                sections.append([])
                in_menu = False

        #print "Sections: {}, Menus: {}".format(section_num, menus)
        good_transactions = 0
        found_count = 0
        logged_in = False
        if section_num < 5:
            execution_comments += ("Log to account {} attempted with 
                password {}.\n").format(self._account_number, self._password)
            execution_comments += "Account name: {}.\n".format(self._username)
            execution_comments += ("Failed to login or couldn't complete all "
                "{:d} of the operations.\n").format(menus)
        else:
            execution_comments += ("Successfully logged in to account {} with "
                "password {}.\n").format(self._account_number, self._password)
            execution_comments += "Account name: {}.\n".format(self._username)
            logged_in = True

            section = 1
            balance = self.section_balance(sections[section])
            section += 1

            log = []
            transaction = 0
            for trans_num in range(0, 7):
                balance = self.transfer(balance, transactions[transaction], 
                    log)
                transaction += 1
                found = self.section_transaction(sections[section], balance)
                if found:
                    good_transactions += 1
                section += 1
            
            for trans_num in range(0, 6):
                balance = self.transfer(balance, transactions[transaction], 
                    log)
                transaction += 1
                found = self.section_transaction(sections[section], balance)
                if found:
                    good_transactions += 1
                section += 1

            balance = self.transfer(balance, transactions[transaction], log)
            transaction += 1
            found = self.section_transaction(sections[section], balance)
            if found:
                good_transactions += 1
            section += 1

            if good_transactions == len(transactions):
                execution_comments += "All transactions correctly executed.\n"
            else:
                execution_comments += ("Only {} out of {} transactions "
                    "correctly executed.\n").format(good_transactions, 
                    len(transactions))

            output_score += 2.0 * (float(good_transactions) / 
                float(len(transactions)))
            
            self.section_balance(sections[section])
            section += 1

            found_count = self.section_recent(sections[section], log[::-1])
            section += 1
            if found_count >= 6:
                execution_comments += ("Last six logged transactions output "
                    "correctly.\n")
            else:
                execution_comments += ("Only {} out of 6 logged transactions "
                    "output correctly.\n").format(found_count)

            output_score += 2.0 * (float(found_count) / 6.0)

            output_score = round(output_score * 2.0) / 2.0

        output_check = [section_num, good_transactions, found_count]

        return [output_score, execution_comments, output_check]

    def transfer(self, balance, amount, log):
        if balance >= amount:
            balance -= amount
            log.append(balance)
        return balance

    def section_balance(self, lines):
        balance = 0
        for line in lines:
            number = re.search(r'\d+', line)
            if number != None:
                found_number = int(number.group())
                if found_number != int(self._account_number):
                    balance = found_number
        return balance

    def section_transaction(self, lines, balance):
        found = False
        for line in lines:
            number = re.search(r'\d+', line)
            if number != None:
                found_number = int(number.group())
                if found_number == balance:
                    found = True
        return found

    def section_recent(self, lines, log):
        found_count = 0
        log_index = 0
        for line in lines:
            found = line.find(str(log[log_index]))
            if found < 0:
                found = line.find(str(log[6 - log_index]))
            if found >= 0:
                log_index += 1
                found_count += 1
        return found_count

    def check_execute_result(self, result):
        """
        Assigns marks based on execution results.
        """
        output_score = 0
        if ExecCode.response_check_compiled(result):
            # The code compiled without errors
            output_score += 1.0
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

    def check_variable_name_quality(self):
        """
        Assigns marks based on variable quality.
        """
        result = check_variable_name_quality(
            self._program_structure, 5)
        variables_score = result[0]
        self._variable_short = result[1]
        self._variable_enumeration = result[2]
        self._error_list.extend(result[3])
        return variables_score


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
            # Store the relevant parameter and the line number the code 
            # occurs
            param = [element.arguments[self._param_num].value, element.lineno]
            self._params.append(param)
        return True
        
    def get_param_list(self):
        """
        Return the parameters found when checking the AST.
        """
        return self._params

# This doesn't confirm to PEP 8, but has been left to match 
# Java and the PLYJ API
class Variable_Visitor(Visitor):
    """
    Find names of variales declared in the AST.
    
    Visitor for checking the Java AST for any variable declarations. 
    If they exist, the name of the variable is recorded, along with the 
    line number it was declared on.
    """

	def __init__(self, verbose=False):
        """
        Initialise the Variable_Visitor class.
        
        Attributes:
        verbose: True if the results are to be output directly.
        """
		super(Variable_Visitor, self).__init__()
		self.variables = []

	def leave_VariableDeclaration(self, element):
        """
        Record the details of the variable declaration.
        """
		#msg = 'Variable type ({}); name ({}); line no ({})'
		#print msg.format(
		#   element.type, element.variable_declarators[0].variable.name, 
		#   element.variable_declarators[0].variable.lineno)

        # Establish the value the field is assigned to if it exists
		value = "";
		if isinstance(element.variable_declarators[0].initializer, Literal):
		    value = element.variable_declarators[0].initializer.value

            # Store the variable name and the line number the code occurs
		self.variables.append(
		    [element.modifiers, element.variable_declarators[0].variable.name, 
		    value, element.variable_declarators[0].variable.lineno])
		#print "{} {} {}".format(element.modifiers, 
		#    element.variable_declarators[0].variable.name, value)
		return True

# This doesn't confirm to PEP 8, but has been left to match 
# Java and the PLYJ API
class Field_Visitor(Visitor):
    """
    Find names of fields declared in the AST.
    
    Visitor for checking the Java AST for any variable declarations. 
    If they exist, the name of the variable is recorded, along with the 
    line number it was declared on.
    """

	def __init__(self, verbose=False):
        """
        Initialise the Variable_Visitor class.
        
        Attributes:
        verbose: True if the results are to be output directly.
        """
		super(Field_Visitor, self).__init__()
		self.variables = []

	def leave_FieldDeclaration(self, element):
        """
        Record the details of the field declaration.
        """
		#msg = 'Variable type ({}); name ({}); line no ({})'
		#print msg.format(
		#   element.type, element.variable_declarators[0].variable.name, 
		#   element.variable_declarators[0].variable.lineno)

        # Establish the value the field is assigned to if it exists
		value = "";
		if isinstance(element.variable_declarators[0].initializer, Literal):
		    value = element.variable_declarators[0].initializer.value

        # Store the variable name and the line number the code occurs
		self.variables.append(
		    [element.modifiers, element.variable_declarators[0].variable.name, 
		    value, element.variable_declarators[0].variable.lineno])
		#print "{} {} = {}".format(element.modifiers, 
		#    element.variable_declarators[0].variable.name, value)
		return True

# This doesn't confirm to PEP 8, but has been left to match 
# Java and the PLYJ API
class Assignment_Visitor(Visitor):
    """
    Find names of fields declared in the AST.
    
    Visitor for checking the Java AST for any variable declarations. 
    If they exist, the name of the variable is recorded, along with the 
    line number it was declared on.
    """

	def __init__(self, verbose=False):
        """
        Initialise the Variable_Visitor class.
        
        Attributes:
        verbose: True if the results are to be output directly.
        """
		super(Assignment_Visitor, self).__init__()
		self.variables = []

	def leave_Assignment(self, element):
        """
        Record the details of the field declaration.
        """
		#msg = 'Variable type ({}); name ({}); line no ({})'
		#print msg.format(
		#   element.type, element.variable_declarators[0].variable.name, 
		#   element.variable_declarators[0].variable.lineno)

        # Establish the value the field is assigned to if it exists
		value = "";
		print "{} {} {}".format(element.lhs, element.operator, element.rhs)
		return True


