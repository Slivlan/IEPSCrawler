"""
	Class that implements mode C - auto extraction.
"""
from htmldom import htmldom

class Auto:
	def __init__(self, overstock_sample_one, overstock_sample_two, rtv_sample_one, rtv_sample_two, selected_sample_one, selected_sample_two):
		self.overstock_sample_one = overstock_sample_one
		self.overstock_sample_two = overstock_sample_two
		self.rtv_sample_one = rtv_sample_one
		self.rtv_sample_two = rtv_sample_two
		self.selected_sample_one = selected_sample_one
		self.selected_sample_two = selected_sample_two

		self.build_dom(self.overstock_sample_one)
	def build_dom(self, sample):
		dom  = htmldom.HtmlDom().createDom(sample)
		print(dom)
		#Using the dom instance from the above code snippet
		html = dom.find( "html" )
		# Gets all the children
		chldrn = html.children()
		print(chldrn.first().html())
		self.build_dom(html)

	def extract_overstock(self, sample_one, sample_two):
		pass

	def extract_rtvslo(self, sample_one, sample_two):
		pass
	
	def extract_selected(self, sample_one, sample_two): # TODO replace selected_one with actual webpage name
		pass