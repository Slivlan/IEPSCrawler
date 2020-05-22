from preprocessing import *
import time
start_time = time.time()
import sys

def search_words(words):

    data = get_words_from_all_files()
    result = []
    for word in words:

        for dict in data:
            words = dict["words"]
            documentName = dict["documentName"]

            indexes= [i for i, x in enumerate(words) if x == word]
            frequency = len(indexes)
            if frequency == 0:
                continue

            neighbourhood_words = [words[i-3:i+4] for i in indexes]
            fin_s = ""

            for neighbourhood in neighbourhood_words:
                fin_s += "..."
                for i, word_n in enumerate(neighbourhood):
                    if word_n in {"[","]","'", '"', "\n", "\t"}:
                        continue
                    if word_n not in {",", ".", ")"} or i == 0 :
                        fin_s +=  " " + word_n
                    else:
                        fin_s += word_n
                fin_s += " "

            result.append((frequency,"  {:<12}{:<59}{}".format(frequency, documentName, fin_s)))

    result = sorted(result, key= lambda x: x[0], reverse=True)
    return result


w = sys.argv[1:]
w = str(w)
w.lower()
w = text_to_tokens_without_stopwords(w)

print('Searching for a query: "{}"'.format(" ".join(w)))
results = search_words(w)
print('Results for a query: "{}"'.format(" ".join(w)))
print("\n  Results found in %s seconds" % (time.time() - start_time))
print ("""
  Frequencies Document                                                   Snippet
  ----------- ---------------------------------------------------------- ----------------------------------------------------------------------------------------
""")


for freq, s in results:
    print(s)
