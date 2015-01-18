# vim: et:ts=4:textwidth=80

# Automark
#
# David Llewellyn-Jones
# Liverpool John Moores University
# 18/12/2014
# Released under the GPL v.3. See the LICENSE file for more details.

"""
Load in a Java file and create various transformed copies of the code.

The file is loaded in and either refactored or transformed in various ways. 
Some of the transformations alter the semantics of the program to allow 
it to be executed in the constrained Automark environment.
"""

from re import sub
from collections import namedtuple
from plyjext.parser import Parser

__all__ = ('load_source')


Program = namedtuple(
    'Program', ['program', 'program_lines', 'full_program', 'program_tree', 
    'line_number', 'line_character_start'])


def load_source(filename):
    """
    Load a Java source file and refactor/transform it in various ways.
    
    Performs various transformations and refactorings that are helpful 
    later on when performing automated marking. This is done at the 
    outset to avoid having to do it multiple times in the code elsewhere.
    
    Args:
        filename: The Java program to load.
        
    Returns:
        The structure contains the code in various forms.
        program: Program as a single string with blank lines removed, and 
            some imports switched to command-line alternatives.
        program_lines: Code split into lines.
        full_program: Original code with no changes made.
        program_tree: AST for the code.
        line_number: List of the original line number for each line, indexed 
            by the line numbers after blank lines have been removed.
        line_character_start: List of character indices for the start of 
            each line of code. These relate to the code after blank lines 
            have been removed.
    """
    # Load in the program from file
    full_program = ''
    with open(filename) as file:
        full_program = file.read()

    program = ""
    line_number = []
    line_character_start = []
    found_main = True
    lines_read = 1
    lines_added = 0
    character_pos = 0
    # Read in thee file a line at a time
    with open(filename) as file:
        for line in file.xreadlines():
            # Remove the package identifier (it'll cause problems for 
            # compilation).
            if not line.startswith('package '):
                # Ensure the class is called Main
                if (not found_main) and (line.find('public class') >= 0):
                    line = sub(r'(class\s*).*?($|\s|{)', r'\1Main\2', line)
                    found_main = True
                # Switch any javax.swing imports to use uk.ac.ljmu.automark
                # instead. This allows us to switch GUI inputs and outputs 
                # use stdin and stdout respectively.
                line = sub(
                    r'(import\s*)javax.swing.', r'\1uk.ac.ljmu.automark.', 
                    line)
                # Remove any blank lines. They'll distort the comment gap
                # average and standard deviation calculations
                if not (line.isspace() or (len(line) == 0)):
                    program += line
                    line_number.append(lines_read)
                    # Keep track of the original vs. the transformed line 
                    # numbers, so that any feedback comments can be referred
                    # to the correct line
                    line_character_start.append(character_pos)
                    lines_added += 1
                    character_pos += len(line)
            lines_read += 1

    # Store a line-delimited version of the program 
    program_lines = program.splitlines()
    
    # Store a AST version of the program
    parser = Parser()
    program_tree = parser.parse_string(full_program)

    # Store all of the various ways of interpreting the program code
    program_structure = Program(
        program, program_lines, full_program, program_tree, line_number, 
        line_character_start)

    return program_structure

