#Stats Tests from Telemetry
#Goods Test
#Chao Test

import os, time, sys, datetime
import re, json, argparse
from telparser import argumentGet
import subprocess

args = argumentGet()

running = True

#set variables using command line parameters
try:
    telpath = args.location
    threshold = args.percent
    runID = args.runID
    autooff = args.auto
    wait_time = args.time
    verbose = args.verbose
    input = args.input
    num_barcodes = args.barcode
except Exception as e:
    print(e)
    exit()

#set up storage for unique reads, # of occurences of each tax_id, and low accuracy reads (and their accuracies)
reads = []
taxids = dict()
lowacc = dict()

def timestamp():
    return str(datetime.datetime.now()).split('.')[0]

init_timestamp = timestamp().replace('-','').replace(' ','_').replace(':', '-')
identifier = "~" + runID + "~" + init_timestamp
dirname = identifier.strip("~")

if not os.path.exists(dirname):
    os.makedirs(dirname)
    

  
#This function reads through all lines of a file at a path, picks out data we want (unique read_id, tax_id, and accuracy)
#it then appends that data to our main memory storage sets(if they aren't already there)
def epi2me(input, process):
    upfol = os.path.join(input, "\uploads")
    downfol = os.path.join(input, "\downloads")
    subprocess.call('epi2me-cli-win-2.50.1003371.exe -a "9bf87815842e9623e77438142d8e80eace2d4fe2" -w ' + process + '-r ' + input + '-i ' + upfol + ' -o ' + downfol, shell=True)

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
    fhand = open(dirname + "\\" + fname, 'a+')
    data_dumps = json.dumps(data)
    fhand.write(data_dumps+"\n")
    fhand.close()

def goods(species):
    if not len(species) == 0:
        n_organisms = 0
        for id in species:
            n_organisms += species[id]
        goods_est = 1 - (len(species)/n_organisms)
    else:
        goods_est = "Undefined"
    return goods_est
           
#this function counts the number of singlets and doublets
#then calculates the value of chao's esitmator
#also calls goods estimate to put it into data
def tests(ids):
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
        chao_est = (singlets**2)/(2*doublets)
    else:
        chao_est = "Insufficient Data"
    goods_est = goods(ids)
    dataForm = {"singlets" : singlets, "doublets" : doublets, "chao_est" : chao_est, "goods" : goods_est, "timestamp" : timestamp()}
    fileUpdate("chao_est" + identifier + ".txt", dataForm)
    return [chao_est, goods_est]

def testCheck(telpath, threshold, taxids, verbose):
    update(telpath, threshold)
    results = tests(taxids)
    if results[0] <= .1 and results[1] == >= 99.9:
        print("Chao estimator is close to 0, the run can be stopped")
        return True
    else:
        if verbose:
            print("Chao Estimator:" + str(results[0]))
            print("Goods:" + str(results[1]))
        return False

def getImmediateSubdirectories(a_dir):
    return [name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))]

def stopRuns(dirs):

def telFinder(dir):
    if os.path.isdir(os.path.join(dir, "\downloads\pass")):
        
        


print("Runnning " + __file__ + " with parameters:")
print(str(args).lstrip('Namespace'))

#Checks to see if the user specified an input, indicating they want to start a run to start a run
if not input == None:
    epi2me(input, 1490)
    barcoded_dir = os.path.join(input, "\downloads\pass")
    sub_dir = getImmediateSubdirectories(barcoded_dir)
    run_dir = []
    running = True
    unread_dir = True
    while running:
        if unread_dir == True:                
            for subdir in sub_dir:
                if subdir not in run_dir:
                    epi2me(os.path.join(barcoded_dir, subdir), 1568)
                    run_dir.append(subdir)
                    if len(run_dir) == num_barcodes:
                        unread_dir = False
        for dir in run_dir:
            telemetry = telFinder(os.path.join(barcoded_dir, dir))
            results = testCheck(telemetry, threshold, taxids, verbose)
            if results == True and autooff == True:
                stopRuns()
                running = False
            time.sleep(wait_time)
            
                
    
    





#Things to be added:



       
#ideas for the code that may be useful:
#   adding code that will check for a minimum number of correct reads before performing chao's estimator
#       might help with inaccurate stops on the read

    # barout_folder = input + "\downloads"
    # barup = input + "\uploads"
    # stsout_folder = input + "\downloads"
    # stsup = input + "\uploads"
    # barcodedReads = []
    # subprocess.call('epi2me-cli-win-2.50.1003370.exe -a "9bf87815842e9623e77438142d8e80eace2d4fe2" -w 1490 -r ' + input + '-i ' + stsup + ' -o ' + barout_folder, shell=True)
    
    # subprocess.call('epi2me-cli-win-2.50.1003370.exe -a "9bf87815842e9623e77438142d8e80eace2d4fe2" -w 1490 -r ' + barout_folder + '-i ' + stsup + ' -o ' + stsout_folder, shell=True)

