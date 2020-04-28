"""
	Class that implements mode A - regex extraction.
"""

class Regex:
	def __init__(self, overstock_sample_one, overstock_sample_two, rtv_sample_one, rtv_sample_two, selected_sample_one, selected_sample_two):
		self.overstock_sample_one = overstock_sample_one
		self.overstock_sample_two = overstock_sample_two
		self.rtv_sample_one = rtv_sample_one
		self.rtv_sample_two = rtv_sample_two
		self.selected_sample_one = selected_sample_one
		self.selected_sample_two = selected_sample_two

	def extract_overstock(self):
		pass

	def extract_rtvslo(self):
		pass
	
	def extract_selected(self): # TODO replace selected_one with actual webpage name
		pass