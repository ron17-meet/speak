################################################
############ install these packages ############
################################################
import json
import requests
import sys
import csv
import pandas



colnames = ['Word', 'OccurTotal', 'OccurNum', 'Freq_pm', 'Rating.Mean',	'Rating.SD', 'Dunno', 'base_form', 'grade', 'synonyms', 'missing_data']

#these two lines below read all of the words from the csv and puts them into a list
data = pandas.read_csv('ListOfWords2.csv', names=colnames)
word_list = data.Word.tolist()


successful_words = []
unsuccessful_words = []

# analyze function takes a word and returns a json with its base form, grade, a synonyms list and a missing data flag
# input : word
# output : {word: {"base_form": base_form, "grade": grade, "synonyms": syn, "missing_data": missing_data}} 
def analyze(word):
	url = "https://api.twinword.com/api/v5/score/word/"
	url1 = "https://wordsapiv1.p.mashape.com/words/"+word
	headers1={
    "X-Mashape-Key": "0KnI3kxcVfmshgyqFJgJP63iY77Cp12mqwijsnYmNvVtlAqoBP",
    "Accept": "application/json"
  	}
	headers={
	    "X-Mashape-Key": "6GtkdIJwQsmshJ8PJL7mRk70eLfhp1OQDWnjsnWvkprZ7J1pCg",
	    "Accept": "application/json"
	  }
	params={
	    "entry": word
	  }
	print(word)
	r = requests.get(url, headers=headers, params = params)
	r1 = requests.get(url1, headers = headers1)
	data = json.loads(r.text)
	data1 = json.loads(r1.text)
	base_form = ""
	grade = 0
	syn = []
	missing_data = 1
	global unsuccessful_words
	if (data["result_code"]!='200'):
		unsuccessful_words.append(word)
		base_form = word
		missing_data = 0
		print(data)
	else:
		base_form = data["response"]
		grade = data["ten_degree"]
	if ('results' not in data1):
		unsuccessful_words.append(word)
		missing_data = 0
	else:
		if 'synonyms' in data1['results'][0]:
			syn = data1['results'][0]['synonyms']
		else:
			syn = []
			missing_data = 0
	if (missing_data ==1):
		successful_words.append(word)
	else:
		unsuccessful_words.append(word)
	info2 = {word: {"base_form": base_form, "grade": grade, "synonyms": syn, "missing_data": missing_data}}
	return info2
# analyze(word_list[3])

# with open('ListOfWords.csv','a') as csv_file:
# 	newFileWriter = csv.writer(csv_file)
# 	newFileWriter.writerow(["word", "base_form", "grade", "synonyms", "missing_data"])

count=0
dict1 = {}

# a flow that creates a csv file with the fields - word, base form, grade, synonyms, missing data (flag)
for word in word_list:
	if (check(word)==False):
		info = analyze(word)
		print(info)
		print ("added " + word + " to dictionary")
		with open('ListOfWords.csv','a') as csv_file:
			newFileWriter = csv.writer(csv_file)
			syn = ', '.join(info[word]['synonyms'])
			newFileWriter.writerow([word, info[word]['base_form'], info[word]['grade'], syn, info[word]["missing_data"]])
		dict1[word] = info[word]
		count=count+1
		if (count%10==0):
			print("---------------------------------")
			print(str(count) + " words added to the list")
			print("---------------------------------")
			# print(dict1)
			print(unsuccessful_words)

#Changes main csv to base formatted csv
# input : csv file (the one that the flow above created)
# output : a formated csv file that is based on base form (word families)
def shift_csv(file):
	new_csv = {}
	with open (file, 'r') as csv_file:
		reader = csv.reader(csv_file)
		data = list(reader)
		for row in data:
			if row[0]!="Word":
				if row[1] in new_csv:
					new_csv[row[1]][4].append(row[0])
					new_csv[row[1]][4] = list(set(new_csv[row[1]][4]))
				else:
					new_csv[row[1]] = [row[1], row[2], row[3], row[4] , [] ]

	with open('ListOfWords3.csv', 'w') as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow(["base_form", "grade", "synonyms", "missing_data", "other_words"])
		values = list(new_csv.values())
		for val in values:
			print(val)
			other_words = ', '.join(val[4])
			writer.writerow([val[0], val[1], val[2], val[3], other_words])
	return new_csv

def check (word):
	colnames = ['Word', 'base_form', 'grade', 'synonyms', 'missing_data']
	data = pandas.read_csv('ListOfWords.csv', names=colnames)
	word_list = data.Word.tolist()
	if (word in word_list):
		return True
	else:
		return False
