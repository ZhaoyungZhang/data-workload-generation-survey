'''
Author: ZhaoyangZhang
Date: 2024-10-20 21:11:18
LastEditors: Do not edit
LastEditTime: 2024-10-22 17:32:36
FilePath: /findPapers/springer_search.py
'''
import requests 
from bs4 import BeautifulSoup
import csv
import argparse
import os

def get_abstract(url):
	r = requests.get(url) 
	soup = BeautifulSoup(r.content, 'html5lib')
	abstract = soup.find('section', attrs	= {'id':'Abs1'})
	return abstract.p.text.replace('\n','')

if __name__ == "__main__":
	count = 0
	parser = argparse.ArgumentParser()
	parser.add_argument("infile", help="location of CSV search file") # input file CSV
	parser.add_argument("outfile", help="where should output be saved?")
	args = parser.parse_args()
	assert(args.infile != args.outfile)
	errors = []
	with open(args.infile) as csvfile:
		flag = False
		if os.path.exists(args.outfile):
			flag = True
			count+=1
			with open(args.outfile) as outfile:
				countfile = csv.DictReader(outfile)
				for row in countfile:
					count+=1
			print("upto row ", count, " processed already.")

		with open(args.outfile, 'a') as outfile:
			fieldnames = ['title', 'author', 'abstract', 'year', 'publication', 'link']
			reader = csv.DictReader(csvfile)
			writer = csv.DictWriter(outfile, fieldnames=fieldnames)
			if not flag:
				writer.writeheader()
			row_count = 1
			for row in reader:
				if row_count >= count:
					publication = {}
					for field in fieldnames:
						if field != 'abstract':
							publication[field] = row[field]
					try:
						publication['abstract'] = get_abstract(row['link'])
					except AttributeError:
						publication['abstract'] = "ABSTRACT NOT FOUND ERROR"
						print("Error at row ", row_count+1)
						errors.append(row_count+1)
					writer.writerow(publication)
					print("Processed row #", row_count+1)
				row_count += 1
	print("Errors occured at ", len(errors), "places: ", errors)