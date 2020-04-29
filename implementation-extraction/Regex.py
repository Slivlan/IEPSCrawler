"""
	Class that implements mode A - regex extraction.
"""

import re
import json
import html2text

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
		re_exp_savings = r"<b>You Save:[\w\W]*?class=\"littleorange\"\>(.*?)\)</span>"
		savings_match = re.compile(re_exp_savings, re.DOTALL)
		savings = savings_match.findall(sample)

		dict_list = []
		for i in range(len(titles)):
			data = {
				'Title': titles[i],
				'Content': contents[i].replace('\n', ' '),
				'ListPrice': list_prices[i],
				'Price': prices[i],
				'Saving': savings[i].split(' (')[0],
				'SavingPercent': savings[i].split(' (')[1].strip(')')
			}
			dict_list.append(data)
		print(json.dumps(dict_list, indent=4))
		print()

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
		content = content_match.group(1).strip()
		#content = self.cleanhtml(content)
		#print(content)
		h = html2text.HTML2Text()
		h.ignore_links = True
		h.ignore_images = True
		content = h.handle(content)

		data = {
			'Author': author,
			'PublishedTime': published_time,
			'Title': title,
			'SubTitle': subtitle,
			'Lead': lead,
			'Content': content
		}
		print(json.dumps(data, indent=4, ensure_ascii=False))

	def cleanhtml(self, raw_html):
		cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
		cleantext = re.sub(cleanr, '', raw_html)
		return cleantext

	def extract_selected(self, sample): # TODO replace selected_one with actual webpage name
		# Title
		re_exp_title = r"<h1 class=\"\">(.*?)\&nbsp\;<span"
		title_match = re.compile(re_exp_title).search(sample)
		title = title_match.group(1)

		# OrigTitle
		re_exp_orig_title = r"<div class=\"originalTitle\">(.*?)<span class=\"description\">"
		orig_title_match = re.compile(re_exp_orig_title).search(sample)
		orig_title = orig_title_match.group(1)

		# Year
		re_exp_year = r"<span id=\"titleYear\">\(<a href=\"[\w\W]*?\">(.*?)</a>\)</span>"
		year_match = re.compile(re_exp_year).search(sample)
		year = year_match.group(1)

		# Length
		re_exp_length = r"<time datetime=\"[\W\w]*?\">\s*(.*?)\s*</time>"
		length_match = re.compile(re_exp_length).search(sample)
		length = length_match.group(1)

		# Rating
		re_exp_rating = r"<span itemprop=\"ratingValue\">(.*?)</span>"
		rating_match = re.compile(re_exp_rating).search(sample)
		rating = rating_match.group(1)

		# Description
		re_exp_description = r"<div class=\"summary_text\">\s*(.*?)\s*</div>"
		description_match = re.compile(re_exp_description).search(sample)
		description = description_match.group(1)

		# Director
		re_exp_director = r"<h4 class=\"inline\">Director:</h4>\s<a href=\"[\w\W]*?\">(.*?)</a>"
		director_match = re.compile(re_exp_director).search(sample)
		director = director_match.group(1)

		# Cast
		re_exp_cast = r"<td>\s<a href=\"https://www\.imdb\.com/name/[\w\W]*?\">\s(.*?)\s</a>"
		cast_match = re.compile(re_exp_cast, re.DOTALL)
		cast = cast_match.findall(sample)

		data = {
			'Title': title,
			'OrigTitle': orig_title,
			'Year': year,
			'Length': length,
			'Rating': rating,
			'Description': description,
			'Director': director,
			'Cast': cast
		}
		print(json.dumps(data, indent=4, ensure_ascii=False))
		print()