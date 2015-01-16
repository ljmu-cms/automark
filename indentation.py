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

def _substring(line, tab, start):
    match = True
    if (len(tab) + start) <= len(line):
        for position in range(0, len(tab)):
            if line[start + position] != tab[position]:
                match = False
    else:
        match = False
    return match

def _check_indentation_type(program, tab, notab):
    indentation_errors = 0
    tabsize = len(tab)
    indent = 0
    line_num = 0
    first_error = 0
    for line in program.program_lines:
        add = line.count('{') * tabsize
        sub = line.count('}') * tabsize
        tabs = 0
        #while line[tabs] == '\t':
        while _substring(line, tab, tabs):
            tabs += tabsize
        indent -= sub
        if (indent != tabs) or ((len(line) > tabs) and (line[tabs] == notab)):
            indentation_errors += 1
            if indentation_errors <= 1:
                first_error = line_num
            indent = tabs
        indent += add
        line_num += 1
    return [indentation_errors, first_error]

def check_indentation(program, thresholdlower, thresholdupper):
    indent_errors = []
    indent_errors.append(_check_indentation_type(program, '\t', ' '))
    indent_errors.append(_check_indentation_type(program, '  ', '\t'))
    indent_errors.append(_check_indentation_type(program, '   ', '\t'))
    indent_errors.append(_check_indentation_type(program, '    ', '\t'))

    min_error, min_error_index = min((val, idx) for (idx, val) in enumerate(indent_errors))
    indentation_errors = min_error[0]

    error_list = []
    indentatino_score = 0
    if indentation_errors <= thresholdupper:
        indentatino_score += 0.5
    if indentation_errors <= thresholdlower:
        indentatino_score += 0.5

    if indentation_errors > thresholdlower:
        error_list.append([program.line_number[min_error[1]], 'Indentation errors'])

    return [indentation_errors, indentatino_score, error_list]


