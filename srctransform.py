#!/usr/bin/env python
# vim: et:ts=4:textwidth=80
"""
automark

David Llewellyn-Jones
Liverpool John Moores University
18/12/2014
Check a program against task requirements

This script allows a program to be checked using the ideone api.
"""

import re
import plyjext.parser as plyj
import os
import collections

Program = collections.namedtuple('Program', ['program', 'program_lines', 'full_program', 'program_tree', 'line_number', 'line_character_start'])

def load_source(filename):
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
    with open(filename) as file:
        for line in file.xreadlines():
            if not line.startswith('package '):
                if (not found_main) and (line.find('public class') >= 0):
                    line = re.sub(r'(class\s*).*?($|\s|{)', r'\1Main\2', line)
                    found_main = True
                line = re.sub(r'(import\s*)javax.swing.', r'\1uk.ac.ljmu.automark.', line)
                if not (line.isspace() or (len(line) == 0)):
                    program += line
                    line_number.append(lines_read)
                    line_character_start.append(character_pos)
                    lines_added += 1
                    character_pos += len(line)
            lines_read += 1

    # Store a line-delimited version of the program 
    program_lines = program.splitlines()
    
    # Store a AST version of the program
    parser = plyj.Parser()
    program_tree = parser.parse_string(full_program)

    program_structure = Program(program, program_lines, full_program, program_tree, line_number, line_character_start)

    return program_structure

