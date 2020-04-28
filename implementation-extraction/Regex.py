"""
	Class that implements mode A - regex extraction.
"""

import re

class Regex:
	def __init__(self, overstock_sample_one, overstock_sample_two, rtv_sample_one, rtv_sample_two, selected_sample_one, selected_sample_two):
		self.overstock_sample_one = overstock_sample_one
		self.overstock_sample_two = overstock_sample_two
		self.rtv_sample_one = rtv_sample_one
		self.rtv_sample_two = rtv_sample_two
		self.selected_sample_one = selected_sample_one
		self.selected_sample_two = selected_sample_two
		self.extract_overstock(self.overstock_sample_one)
		self.extract_overstock(self.overstock_sample_two)
		self.extract_rtvslo(self.rtv_sample_one)
		self.extract_rtvslo(self.rtv_sample_two)
		self.extract_selected(self.selected_sample_one)
		self.extract_selected(self.selected_sample_two)

	def extract_overstock(self, sample):


		pass

	def extract_rtvslo(self, sample):
		print(sample)

		# Author
		re_exp_author = r"<div class=\"author-name\">(.*)</div>"
		author_match = re.compile(re_exp_author).search(sample)
		author = author_match.group(1)

		# PublishedTime
		re_exp_published_time = r"<div class=\"publish-meta\">\n\t\t(.*)<br>"
		published_time_match = re.compile(re_exp_published_time).search(sample)
		published_time = published_time_match.group(1)

		# Title
		re_exp_published_title = r"<h1>(.*)</h1>"
		title_match = re.compile(re_exp_published_title).search(sample)
		title = title_match.group(1)

		# SubTitle
		re_exp_published_subtitle = r"<div class=\"subtitle\">(.*)</div>"
		subtitle_match = re.compile(re_exp_published_subtitle).search(sample)
		subtitle = subtitle_match.group(1)

		# Lead
		re_exp_lead = r"<p class=\"lead\">(.*)</p>"
		lead_match = re.compile(re_exp_lead).search(sample)
		lead = lead_match.group(1)

		# Content
		re_exp_content = r"<div class=\"article-body\">(.*?)</span>(.*?)</figcaption>(.*?)<p class=\"Body\"></p><p class=\"Body\">(.*?)<div class=\"gallery\">"
		content_match = re.compile(re_exp_content, re.DOTALL).search(sample)
		content = content_match.group(1)
		content = content_match.group(2)
		content = content_match.group(3)


		# data = {
		# 	'Author': author,
		# 	'PublishedTime': publishedtime,
		# 	'Title': title,
		# 	'SubTitle': subtitle,
		# 	'Lead': lead,
		# 	'Content': content
		# }
		# print(json.dumps(data, indent=4, ensure_ascii=False))
		pass
	
	def extract_selected(self, sample): # TODO replace selected_one with actual webpage name
		pass