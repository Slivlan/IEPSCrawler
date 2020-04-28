"""
	Class that implements mode A - regex extraction.
"""

import re
import json

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
		# Titles
		re_exp_titles = r"<td><a href=\"http://www\.overstock\.com/cgi-bin/d2\.cgi\?PAGE=PROFRAME[\w\W]*?\"><b>(.*?)</b></a><br>"
		titles_match = re.compile(re_exp_titles, re.DOTALL)
		titles = titles_match.findall(sample)

		# Content
		re_exp_contents = r"<span class=\"normal\">(.*?)<br>"
		contents_match = re.compile(re_exp_contents, re.DOTALL)
		contents = contents_match.findall(sample)

		# ListPrice
		re_exp_list_prices = r"<b>List Price:[\w\W]*?<s>(.*?)</s>"
		list_prices_match = re.compile(re_exp_list_prices, re.DOTALL)
		list_prices = list_prices_match.findall(sample)

		# Price
		re_exp_prices = r"<b>Price:[\w\W]*?<b>(.*?)</b>"
		prices_match = re.compile(re_exp_prices, re.DOTALL)
		prices = prices_match.findall(sample)

		# Saving
		re_exp_savings = r"<b>You Save:[\w\W]*?class=\"littleorange\"(.*?)</span>"
		savings_match = re.compile(re_exp_savings, re.DOTALL)
		savings = savings_match.findall(sample)

		dict_list = []
		for i in range(len(titles)):
			data = {
				'Title': titles[i],
				'Content': contents[i].replace('\n', ' '),
				'ListPrice': list_prices[i],
				'Price': prices[i],
				'Saving': savings[i].split(' (')[1],
				'SavingPercent': savings[i].split(' (')[1].strip(')')
			}
			dict_list.append(data)
		print(json.dumps(dict_list, indent=4))
		print()

		pass

	def extract_rtvslo(self, sample):
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
		#re_exp_content = r"<div class=\"article-body\">(.*?)</span>(.*?)\s*</figcaption>(.*?)<p class=\"Body\"></p><p class=\"Body\">(.*?)<div class=\"gallery\">"
		re_exp_content = r"<div class=\"article-body\">(.*?)</article>"
		content_match = re.compile(re_exp_content, re.DOTALL).search(sample)
		#figure_caption = content_match.group(2)
		#content = figure_caption + content_match.group(4)
		content = content_match.group(1)



		data = {
			'Author': author,
			'PublishedTime': published_time,
			'Title': title,
			'SubTitle': subtitle,
			'Lead': lead,
			'Content': content
		}
		print(json.dumps(data, indent=4, ensure_ascii=False))
		pass
	
	def extract_selected(self, sample): # TODO replace selected_one with actual webpage name
		pass