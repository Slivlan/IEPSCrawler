from preprocessing import *
import time
start_time = time.time()

def search_word(word):

    data = get_words_from_all_files()
    result = []
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
    for freq, s in result:
        print(s)

print ("""
  Frequencies Document                                                   Snippet
  ----------- ---------------------------------------------------------- ----------------------------------------------------------------------------------------
""")
search_word("uporabo")
print("--- %s seconds ---" % (time.time() - start_time))