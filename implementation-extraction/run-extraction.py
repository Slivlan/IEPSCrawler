"""
	Main script of programming assignment 2, WIER. https://szitnik.github.io/wier-labs/PA2.html
"""
import sys

def regex_extraction(): # TODO A
	pass

def xpath_extraction(): # TODO B
	

def auto_extraction(): # TODO C
	pass

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