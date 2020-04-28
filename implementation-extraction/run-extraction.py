"""
	Main script of programming assignment 2, WIER. https://szitnik.github.io/wier-labs/PA2.html
"""
import sys
from Regex import Regex
from XPath import XPath
from Auto import Auto

# Load given htmls from input-extraction folder. They will be given to ectractor classes as input.
overstock_sample_one = open('../input-extraction/overstock.com/jewelry01.html', 'r').read()
overstock_sample_two = open('../input-extraction/overstock.com/jewelry02.html', 'r').read()

rtv_sample_one = open('../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html', 'r', encoding='utf-8').read()
rtv_sample_two = open('../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html', 'r', encoding='utf-8').read()

# TODO Select and load other two samples per two webpages
selected_sample_one = open('../input-extraction/imdb.com/Boter (1972) - IMDb.html', 'r').read()
selected_sample_two = open('../input-extraction/Kaznilnica odrešitve (1994) - IMDb.html', 'r').read()

def regex_extraction(): # TODO A
	regex = Regex(overstock_sample_one, overstock_sample_two, rtv_sample_one, rtv_sample_two, selected_sample_one, selectedsample_two)

def xpath_extraction(): # TODO B
	xpath = XPath(overstock_sample_one, overstock_sample_two, rtv_sample_one, rtv_sample_two, selected_sample_one, selectedsample_two)

def auto_extraction(): # TODO C
	auto = Auto(overstock_sample_one, overstock_sample_two, rtv_sample_one, rtv_sample_two, selected_sample_one, selectedsample_two)

def execute():
	args = sys.argv
	if len(args) != 2:
		print("[EXECUTE EXTRACTION] Missing mode argument (A, B, C) or given too many arguments. Input should be 'python run-exctraction.py <mode>', e.g. 'python run-exctraction.py A")
		sys.exit()
	mode = args[1]
	if mode == 'A':
		print("[EXECUTE EXTRACTION] Entering exctraction by regex.")
		regex_extraction()
	elif mode == 'B':
		print("[EXECUTE EXTRACTION] Entering extraction by xpath.")
		xpath_extraction()
	elif mode == 'C':
		print("[EXECUTE EXTRACTION] Entering automatic extraction.")
		auto_extraction()
	else:
		print("[EXECUTE EXTRACTION] Incorrect mode argument. Can only be one of A, B or C.")
		sys.exit()

execute()