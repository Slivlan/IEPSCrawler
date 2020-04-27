"""
	Class that implements mode B - xpath extraction.
	https://3583bytesready.net/2016/08/17/scraping-data-python-xpath/
"""
from lxml import html
import json

class XPath:
	def __init__(self, overstock_sample_one, overstock_sample_two, rtv_sample_one, rtv_sample_two):#, selected_sample_one, selected_sample_two:
		self.overstock_sample_one = overstock_sample_one
		self.overstock_sample_two = overstock_sample_two
		self.rtv_sample_one = rtv_sample_one
		self.rtv_sample_two = rtv_sample_two
		"""self.selected_sample_one = selected_sample_one
		self.selected_sample_two = selected_sample_two"""
		self.extract_overstock(self.overstock_sample_one)
		self.extract_overstock(self.overstock_sample_two)
		self.extract_rtvslo(self.rtv_sample_one)
		self.extract_rtvslo(self.rtv_sample_two)
		self.extract_selected(self.selected_sample_one)
		self.extract_selected(self.selected_sample_two)

	def extract_overstock(self, sample):
		tree = html.fromstring(sample)
		# Title
		titles = tree.xpath('/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/a/b/text()')
		# Content
		contents = tree.xpath('/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td[2]/span/text()')
		# ListPrice
		listprices = tree.xpath('/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/s/text()')
		# Price
		prices = tree.xpath('/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td[1]/table/tbody/tr[2]/td[2]/span/b/text()')
		# Saving
		savings = tree.xpath('/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span/text()')
		dict_list = []
		for i in range(len(titles)):
			data = {
				'Title': titles[i],
				'Content': contents[i].replace('\n', ' '),
				'ListPrice': listprices[i],
				'Price': prices[i],
				'Saving': savings[i].split(' (')[0],
				'SavingPercent': savings[i].split(' (')[1].strip(')')
			}
			dict_list.append(data)
		print(json.dumps(dict_list, indent=4))
		print()

	def extract_rtvslo(self, sample):
		tree = html.fromstring(sample)
		# Author
		author = tree.xpath('//*[@id="main-container"]/div[3]/div/div[1]/div[1]/div/text()')[0]
		# PublishedTime
		publishedtime = tree.xpath('//*[@id="main-container"]/div[3]/div/div[1]/div[2]/text()[1]')[0].strip()
		# Title
		title = tree.xpath('//*[@id="main-container"]/div[3]/div/header/h1/text()')[0]
		# SubTitle
		subtitle = tree.xpath('//*[@id="main-container"]/div[3]/div/header/div[2]/text()')[0]
		# Lead
		lead = tree.xpath('//*[@id="main-container"]/div[3]/div/header/p/text()')[0]
		# Content
		content_header = ' '.join(tree.xpath('//*[@id="main-container"]/div[3]/div/div[2]/div/figure/figcaption/text()')).strip()
		content_article = ' '.join(tree.xpath('//article[@class="article"]/p/text()')).strip()
		content = content_header + '. ' + content_article
		data = {
			'Author': author,
			'PublishedTime': publishedtime,
			'Title': title,
			'SubTitle': subtitle,
			'Lead': lead,
			'Content': content
		}
		print(json.dumps(data, indent=4, ensure_ascii=False))
		print()
	def extract_selected(self, sample): # TODO replace selected_one with actual webpage name
		pass