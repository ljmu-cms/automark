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

class Automark(automark.Automark):
	def __init__(self, filename, credentialsFile, build_dir):
		automark.Automark.__init__(self, filename, credentialsFile, build_dir)

