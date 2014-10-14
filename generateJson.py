import json
import time
import numpy
import datetime

API_VERSIONS = ["11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30"]

def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

def unix_time_millis(dt):
    return unix_time(dt) * 1000.0


def writeFile(path, data):
	with open(path, "w") as outfile:
		json.dump(data, outfile)

def genData(numDays):
	apiData=[];
	for apiVersion in API_VERSIONS:
		apiRow={}
		apiRow["api_version"]=apiVersion
		avgRowsProcessedList=[]
		countList=[]
		startDay = datetime.datetime(2014,8,1)
		for i in range(0, numDays):
			d = startDay + datetime.timedelta(i)		
			avgRowsProcessed = 500 + i*100 +numpy.random.normal(100, 50)
			count = 10000+ i*1000 + round(numpy.random.normal(1000, 500))
			avgRowsProcessedList.append([unix_time_millis(d),avgRowsProcessed])
			countList.append([unix_time_millis(d),count])
		apiRow["avg_rows_processed"]=avgRowsProcessedList
		apiRow["count"]=countList
		apiData.append(apiRow)
	print apiData
	writeFile('apiData.json', apiData)

genData(30)
		
