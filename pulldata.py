#Stats Tests from Telemetry
#Goods Test
#Chao Test
#Proper use: py pulldata.py [pathOfTelemetryFile] [thresholdForAccuracy]
#       e.g. py pulldata.py C:\Users\ZachS\Documents\telemetry-143795.log 60

import os, time, sys, datetime
import re, json

running = True

#set variables using command line parameters
try:
    telpath = sys.argv[1]
    threshold = sys.argv[2]
    runID = sys.argv[3]
except Exception as e:
    print(e)
    print("Please specifiy a path for the telemetry file and accuracy threshold in this format: py pulldata.py [pathname] [threshold] [runID]")
    exit()

#set up storage for unique reads, # of occurences of each tax_id, and low accuracy reads (and their accuracies)
reads = []
taxids = dict()
lowacc = dict()

#time to wait between reading the log file again, defaulted to 30 seconds
wait_time = 10

#set loop conditional
running = True

def timestamp():
    return str(datetime.datetime.now()).split('.')[0]
    
#This function reads through all lines of a file at a path, picks out data we want (unique read_id, tax_id, and accuracy)
#it then appends that data to our main memory storage sets(if they aren't already there)
def update(path, threshold):
    logdata = open(path, 'r')
    for read in logdata:
        tax_id = re.search('"taxid":"(.*?)"', read).group(1)
        read_id = re.search('"read_id":{"read_id":"(.*?)"', read).group(1)
        accuracy = re.search('"accuracy":(.*?)}', read).group(1)
        if read_id in reads or tax_id == "-1":
            continue
        reads.append(read_id)
        taxids[tax_id] = taxids.get(tax_id, 0) + 1
        if float(accuracy) < float(threshold):
            fileloc = re.search('"filename":"(.*?)"',read).group(1)
            dataForm = {"read_id" : read_id, "tax_id" : tax_id, "accuracy" : accuracy, "location" : fileloc}
            fileUpdate("lowaccreads" + identifier + ".txt", dataForm)
    logdata.close()    

def fileUpdate(fname, data):
    fhand = open(fname, 'a+')
    data_dumps = json.dumps(data)
    fhand.write(data_dumps+"\n")
    fhand.close()
    
#this function counts the number of singlets and doublets
#then calculates the value of chao's esitmator
def chao(ids):
    singlets = 0
    doublets = 0
    for id in ids:
        if ids[id] == 1:
            singlets += 1
        elif ids[id] == 2:
            doublets += 1
        else:
            continue
    #I'm not sure if this conditional has to be here, but I figured there would be cases where there were no singlets or doublets early in the process
    #Prevents the code from erroring out
    if doublets != 0 and singlets != 0:
        chaoest = (singlets^2)/(2*doublets)
    else:
        dataForm = {"singlets" : singlets, "doublets" : doublets, "chaoest" : "Insufficient Data", "timestamp" : timestamp()}
        fileUpdate("chaoest" + identifier + ".txt", dataForm)
        return "Insufficient Data"
    #Not sure how close you want this to 0
    if chaoest <= .1:
        dataForm = {"singlets" : singlets, "doublets" : doublets, "chaoest" : chaoest, "timestamp" : timestamp()}
        fileUpdate("chaoest" + identifier + ".txt", dataForm)
        return True
    else:
        dataForm = {"singlets" : singlets, "doublets" : doublets, "chaoest" : chaoest, "timestamp" : timestamp()}
        fileUpdate("chaoest" + identifier + ".txt", dataForm)
        return chaoest
        
init_timestamp = timestamp().replace('-','').replace(' ','_').replace(':', '-')
identifier = "~" + runID + "~" + init_timestamp

#main running block
while running:
    update(telpath, threshold)
    chaoest = chao(taxids)
    if chaoest == True:
        print("Chao estimator is close to 0, the run can be stopped")
        running = False
    else:
        print("Chao Estimator:" + str(chaoest))     
        time.sleep(wait_time)
       
#Things to be added:
#   Goods estimator function
#   Autostopping the read (theres an epi2me agent for commandline, i wonder if it is compatible with the GUI?)
#   Code that saves low accuracy read locations in a file (?)

       
#ideas for the code that may be useful:
#   adding code that will check for a minimum number of correct reads before performing chao's estimator
#       might help with inaccurate stops on the read
#   

