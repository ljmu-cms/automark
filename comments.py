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

def _line_from_character_no_space(program, char_pos):
	line = 0
	while (line < len(program.line_character_start)) and (char_pos >= program.line_character_start[line]):
		line += 1
	return line

def _line_from_character(program, char_pos):
	return program.line_number[_line_from_character_no_space(program, char_pos) - 1]

def check_comment_quality(program, frequency_threshold, consistency_threshold, ave_offset, sd_offset, ave_weight):
	# Regex expressions search for block comments or full-line comments.
	# Multiple full-line comments without other text are considered as a single match
	block_comments = list(re.finditer(r'/\*.*?\*/|//.*?$(?!\s*//)', program.program, (re.MULTILINE | re.DOTALL)))

	error_list = []
	comment_gap_average = 1000.0
	comment_gap_sd = 1000.0
	last_comment_line = 0
	comment_count = len(block_comments)
	if comment_count > 0:
		gap_sum = 0
		previous_end = 0
		for block_comment in block_comments:
			gap_sum += _line_from_character_no_space(program, block_comment.start()) - previous_end
			previous_end = _line_from_character_no_space(program, block_comment.end()) + 1
		gap_sum += len(program.program_lines) - previous_end
		comment_gap_average = gap_sum / float(comment_count)

		gap_sum_squared = 0.0
		previous_end = 0
		for block_comment in block_comments:
			gap_sum_squared += ((_line_from_character_no_space(program, block_comment.start()) - previous_end) - comment_gap_average)**2.0
			previous_end = _line_from_character_no_space(program, block_comment.end()) + 1
		gap_sum_squared += ((len(program.program_lines) - previous_end) - comment_gap_average)**2.0
		comment_gap_sd = (gap_sum_squared / comment_count)**0.5
		
		last_comment_line = _line_from_character(program, block_comments[comment_count - 1].end())

	comment_frequency = max(1.0 - ((max(comment_gap_average - ave_offset, 0.0)) * ave_weight), 0.0)
	comment_consistency = max(1.0 - ((max(comment_gap_sd - sd_offset, 0.0)) * 1.0), 0.0)
	comment_score = int(round(comment_frequency + comment_consistency))

	if comment_frequency < frequency_threshold:
		error_list.append([last_comment_line, 'Try to include more comments in your code'])
	if comment_consistency < consistency_threshold:
		error_list.append([last_comment_line, 'Include comments evenly throughout your code, not just in a few places'])
	return [comment_score, comment_gap_average, comment_gap_sd, error_list]




