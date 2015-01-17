# vim: et:ts=4:textwidth=80

# Automark
#
# David Llewellyn-Jones
# Liverpool John Moores University
# 18/12/2014
# Released under the GPL v.3. See the LICENSE file for more details.

"""
Return statistics about the frequency and consistency of Java comments.

Analyse a Java source file and return the average and standard deviation 
of the lines per comment, ignoring blank lines.
"""

from re import finditer, MULTILINE, DOTALL

__all__ = ('check_comment_quality')


def _line_from_character_no_space(program, char_pos):
    """
    Return line number of a character for code with blanks lines removed.
    
    For internal use, returns the line number for the character with a 
    given index. Works on the program refactored to remove blank lines.
    
    Args:
        program: The lines of code as a String, with blank lines removed.
        char_pos: Index of the character.
        
    Returns:
        The line number that the character appears on.
    """
	line = 0
	while (line < len(program.line_character_start)) and (
	        char_pos >= program.line_character_start[line]):
		line += 1
	return line


def _line_from_character(program, char_pos):
    """
    Return line number of a character in the original code (with blank lines).
    
    For internal use, returns the line number for the character with a 
    given index. Works on the original program containing blank lines.
    
    Args:
        program: The lines of code as a String.
        char_pos: Index of the character.
        
    Returns:
        The line number that the character appears on.
    """
	return program.line_number[_line_from_character_no_space(
	    program, char_pos) - 1]


def check_comment_quality(
        program, frequency_threshold, consistency_threshold, 
        ave_offset, sd_offset, ave_weight):
    """
    Check the quality of comments in a piece of code.
    
    Return details about the quality of comments in a given piece of code.
    
    Args:
        program: The code to mark.
        frequency_threshold: Threshold for frequency above which to generate 
            a feedback comment.
        consistency_threshold: Threshold for consistency above which to 
            generate a feedback comment.
        ave_offset: Offset value for calculating frequency marks.
        sd_offset: Offset value for calculating consistency marks.
        ave_weight: Weighting of ave to sd for calculating marks.
        
    Returns:
        List containing the calculated mark, the average gap between 
        comments, the standard deviation of the gap between comments and 
        a list of errors to provide as feedback.
    """
	# Regex expressions search for block comments or full-line comments.
	# Multiple full-line comments without other text are considered as a 
	# single match
	block_comments = list(finditer(
	    r'/\*.*?\*/|//.*?$(?!\s*//)', program.program, 
	    (MULTILINE | DOTALL)))

	error_list = []
	comment_gap_average = 1000.0
	comment_gap_sd = 1000.0
	last_comment_line = 0
	comment_count = len(block_comments)
	if comment_count > 0:
		gap_sum = 0
		previous_end = 0
		for block_comment in block_comments:
			gap_sum += _line_from_character_no_space(
			    program, block_comment.start()) - previous_end
			previous_end = _line_from_character_no_space(
			    program, block_comment.end()) + 1
		gap_sum += len(program.program_lines) - previous_end
		comment_gap_average = gap_sum / float(comment_count)

		gap_sum_squared = 0.0
		previous_end = 0
		for block_comment in block_comments:
			gap_sum_squared += ((_line_from_character_no_space(
			    program, block_comment.start()) - previous_end) - 
			    comment_gap_average)**2.0
			previous_end = _line_from_character_no_space(
			    program, block_comment.end()) + 1
		gap_sum_squared += ((len(program.program_lines) - 
		    previous_end) - comment_gap_average)**2.0
		comment_gap_sd = (gap_sum_squared / comment_count)**0.5
		
		last_comment_line = _line_from_character(
		    program, block_comments[comment_count - 1].end())

	comment_frequency = max(1.0 - ((max(
	    comment_gap_average - ave_offset, 0.0)) * ave_weight), 0.0)
	comment_consistency = max(1.0 - ((max(
	    comment_gap_sd - sd_offset, 0.0)) * 1.0), 0.0)
	comment_score = int(round(comment_frequency + comment_consistency))

	if comment_frequency < frequency_threshold:
		error_list.append(
		    [last_comment_line, 'Try to include more comments in your code'])
	if comment_consistency < consistency_threshold:
		error_list.append(
		    [last_comment_line, 'Include comments evenly throughout your '
		    'code, not just in a few places'])
	return [comment_score, comment_gap_average, comment_gap_sd, error_list]




