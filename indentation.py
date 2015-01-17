# vim: et:ts=4:textwidth=80

# Automark
#
# David Llewellyn-Jones
# Liverpool John Moores University
# 18/12/2014
# Released under the GPL v.3. See the LICENSE file for more details.

"""
Check program indentation correctness.

Check a single Java source file and measure the accuracy of the indentation 
used in it. Check the code as if tabs or spaces have been used. Either two,
three or four spaces are acceptable. The tab-type that generates the minimum 
number of errors is assumed.

Indentation is expected to fulfil the following rules:
1. The file starts with an indentation level of zero.
2. For openining braces, the indentation level of subsequent lines 
    increases by one.
3. For closing braces, the indentation on this and subsequent lines
    decreases by one.
4. At any other time the indentation remains the same.
If a line has erroneous indentation, the current indentation level is reset 
to match the erroneous line.
"""

__all__ = ('check_indentation')


def _substring(line, tab, start):
    """
    Check whether the next block of text matches a character sequence.
    
    For internal use, checks from a given point in a string to establish 
    whether the characters match the character sequence povided.
    
    Args:
        line: String to check.
        tab: Sequence of characters to match.
        start: Index of character in line to start the check.
        
    Returns:
        True if the next block matches the sequence exactly.
    """
    match = True
    if (len(tab) + start) <= len(line):
        for position in range(0, len(tab)):
            if line[start + position] != tab[position]:
                match = False
    else:
        match = False
    return match


def _check_indentation_type(program, tab, notab):
    """
    Check indentation based on a given tab type.
    
    For internal use, check a piece of code to establish how many 
    indentation errors there are based on the given tab style. It 
    assumes the start of the code has no indentation.
    
    Args:
        program: The code to check.
        tab: Character sequence used for tabs.
        notab: A character that can't immediately proceed an indented 
            section. For example, if tabs are represented as spaces then
            the code following the indentation shouldn't start with a tab 
            character. Contrariwise, if indentation uses the tab 
            character, the code following the indentation shouldn't start 
            with a space.

    Returns:
        A list containing the number of indentation errors and the line 
        number where the first indentation error occurred.
    """
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
    """
    Check the indentation of a program where the tab type is unknown.
    
    Check against a mixture of tab styles and return the minimum number 
    of errors that are found.
    
    Args:
        program: The code to check.
        thresholdlower: The threshold for the number of errors to lose
            half marks.
        thresholdUpper: The threshold for the number of errors that 
            will lose all of the marks.
    
    Returns:
        A list containing the number of errors found, the score obtained 
        based no the threshold values, and an error list to offer as 
        feedback.
    """
    indent_errors = []
    indent_errors.append(_check_indentation_type(program, '\t', ' '))
    indent_errors.append(_check_indentation_type(program, '  ', '\t'))
    indent_errors.append(_check_indentation_type(program, '   ', '\t'))
    indent_errors.append(_check_indentation_type(program, '    ', '\t'))

    min_error, min_error_index = min((val, idx) for (idx, val) in enumerate(
        indent_errors))
    indentation_errors = min_error[0]

    error_list = []
    indentatino_score = 0
    if indentation_errors <= thresholdupper:
        indentatino_score += 0.5
    if indentation_errors <= thresholdlower:
        indentatino_score += 0.5

    if indentation_errors > thresholdlower:
        error_list.append(
            [program.line_number[min_error[1]], 'Indentation errors'])

    return [indentation_errors, indentatino_score, error_list]


