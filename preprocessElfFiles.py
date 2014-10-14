#!/usr/bin/python

import os
import argparse
import csv
import re
import datetime
import json
import sys
import numpy

parser = argparse.ArgumentParser(description='Script to process API ELF files and convert them to a json for d3 visualization')
parser.add_argument('-i','--inputDir', help='input directory containing ELF files', required=True)
parser.add_argument('-o','--outputFile', help='output json filename', required=True)
args = vars(parser.parse_args())

outputFile=args['outputFile'];
inputDir=args['inputDir'];

csv.field_size_limit(sys.maxsize)

# converts datetime to unix epoch
def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds() * 1000.0

#converts string to int that handes empty/null strings
def parse_int(s):
    s = s.strip()
    return int(s) if s else 0

#creates file with json data
def writeFile(path, data):
	with open(path, "w") as outfile:
		json.dump(data, outfile)

#process event log files in inputDir to creates a map from apiVersion to <timestamp,count of api calls,avg rows processed>
def getApiVersionToData(inputDir):
	#map from apiVersion to (map from timestamp to [count, rows processed])
	apiVersionToDataList={}
	#iterate over files in input directory
	for dirpath, dirnames, filenames in os.walk(inputDir):
		# sort the files so that the files are processed ordered by timestamp
		for filename in sorted(filenames):
			# generate filename
			filename = os.path.join(dirpath, filename)
			if filename.endswith('.csv'):
				print filename
				#parses the date of the elf log file eg. API-2014-09-17.csv
				m = re.search('.*(\d{4})-(\d{2})-(\d{2})\.csv', filename) 
				year=int(m.group(1))
				month=int(m.group(2))
				day=int(m.group(3))
				timestamp = datetime.datetime(year, month, day)
				apiVersionToData={}
				with open(filename, 'rb') as csvfile:
					csvreader = csv.reader(csvfile)
					headers = csvreader.next()
					apiVersionIndex = headers.index('API_VERSION')
					rowsProcessedIndex = headers.index('ROWS_PROCESSED')
					for tokens in csvreader:
						apiVersion = tokens[apiVersionIndex]
						rowsProcessed = parse_int(tokens[rowsProcessedIndex])
						if apiVersion not in apiVersionToData:
							apiVersionToData[apiVersion]=[1,rowsProcessed]
						else:
							apiVersionToData[apiVersion][0]+=1
							apiVersionToData[apiVersion][1]+=rowsProcessed
					for apiVersion, data in apiVersionToData.iteritems():
						if apiVersion not in apiVersionToDataList:
							apiVersionToDataList[apiVersion]=[]
						apiVersionToDataList[apiVersion].append([timestamp,data[0],data[1]])
	return apiVersionToDataList

def createJsonFile(apiVersionToDataList, outputFile):
	# create json that will be used for d3 
	jsonData=[]	
	xmin=sys.maxint	
	xmax=-1
	ymin=sys.maxint	
	ymax=-1
	for apiVersion, dataList in apiVersionToDataList.iteritems():
		dataRow={}
		dataRow["api_version"]=apiVersion
		countList=[]
		avgRowsProcessedList=[]
		xdata=[]
		ydata=[]
		for data in dataList:
			timestamp=data[0]
			count=data[1]
			avg_rows_processed=data[2]/count
			countList.append([unix_time(timestamp),count])
			avgRowsProcessedList.append([unix_time(timestamp),avg_rows_processed])
			xdata.append(count)
			ydata.append(avg_rows_processed)
			xmin=min(xmin,count)
			xmax=max(xmax,count)
			ymin=min(ymin,avg_rows_processed)
			ymax=max(ymax,avg_rows_processed)
		dataRow["avg_rows_processed"]=avgRowsProcessedList
		dataRow["count"]=countList
		jsonData.append(dataRow)
	writeFile(outputFile, jsonData)
	# print the min and max count and avg_rows_processed (useful for setting scale of x and y axis)
	print "xmin "+str(xmin)+" xmax "+str(xmax)
	print "ymin "+str(ymin)+" ymax "+str(ymax)

def processDir(inputDir, outputFile):
	apiVersionToDataList=getApiVersionToData(inputDir)
	createJsonFile(apiVersionToDataList, outputFile)

processDir(inputDir, outputFile)		


