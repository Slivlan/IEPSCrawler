"""
	Class that implements mode B - xpath extraction.
"""

class XPath:
	def __init__(self, overstock_sample_one, overstock_sample_two, rtv_sample_one, rtv_sample_two):#, selected_webpage_one_sample_one, selected_webpage_one_sample_two, selected_webpage_two_sample_one, selected_webpage_one_sample_two):
		print("[XPath] Hello World XPath!")
		self.overstock_sample_one = overstock_sample_one
		self.overstock_sample_two = overstock_sample_two
		self.rtv_sample_one = rtv_sample_one
		self.rtv_sample_two = rtv_sample_two
		"""self.selected_webpage_one_sample_one = selected_webpage_one_sample_one
		self.selected_webpage_one_sample_two = selected_webpage_one_sample_two
		self.selected_webpage_two_sample_one = selected_webpage_two_sample_one
		self.selected_webpage_two_sample_two = selected_webpage_two_sample_two"""

	def extract_overstock(self):
		pass

	def extract_rtvslo(self):
		pass

	def extract_selected_one(self): # TODO replace selected_one with actual webpage name
		pass

	def extract_selected_two(self): # TODO replace selected_two with actual webpage name
		pass