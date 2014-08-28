# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 11:48:36 2014

@author: a8243587
"""

class GeneralError(Exception):
    '''Non-descript error.'''
    def __init__(self, value):
		self.value = value
    def __str__(self):
		return repr(self.value)

class GraphError(Exception):
    '''Error relating to a network not be suitable to compute or run the 
    selected function on.'''
    def __init__(self, value):
		self.value = value
    def __str__(self):
		return repr(self.value)

class OutputError(Exception):
    ''''''
    def __init__(self, value):
		self.value = value
    def __str__(self):
		return repr(self.value)
  
class CalculationError(Exception):
    '''Could not calculate a value.'''
    def __init__(self, value):
		self.value = value
    def __str__(self):
		return repr(self.value)

class SearchError(Exception):
    '''Could not find the node or edge inteneded to be found.'''
    def __init__(self, value):
		self.value = value
    def __str__(self):
		return repr(self.value)
  
class WriteError(Exception):
    '''Could not open and read or could not write to the text file.'''
    def __init__(self, value):
		self.value = value
    def __str__(self):
		return repr(self.value)