#Stats Tests from Telemetry
#Goods Test
#Chao Test

import os, time, sys, datetime
import re, json, argparse
from telparser import argumentGet
import subprocess
import requests
from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
import urllib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing import Process
import csv

args = argumentGet()
user = "zebbl"

#set up credentials to login to epi2me
usernameID = "paul.lepp@minotstateu.edu"
passwordID = "PWL1minot"


running = True

#set variables using command line parameters
try:
    runID = args.runID
    autooff = args.auto
    wait_time = args.time
    verbose = args.verbose
    telnum = args.input
    csv_get = args.csv_get
    validbar = args.barcodes
except Exception as e:
    print(e)
    exit()

#set up storage for unique reads, # of occurences of each tax_id
reads = []
taxids = dict()

validbars = validbar.split(',')
for bar in validbars:
    taxids[bar] = dict()

print(taxids)

def timestamp():
    return str(datetime.datetime.now()).split('.')[0]

init_timestamp = timestamp().replace('-','').replace(' ','_').replace(':', '-')
identifier = "~" + runID + "~" + init_timestamp
dirname = identifier.strip("~")

def make_dir_if_not_exist(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    
make_dir_if_not_exist(dirname)
    
#This function reads through all lines of a file at a path, picks out data we want (unique read_id, tax_id, and accuracy)
#it then appends that data to our main memory storage sets(if they aren't already there)
def epi2me(input, process):
    process = 'epi2me-cli-win-2.52.1246070.exe -w ' + str(process) + ' -i "' + input + '" -a "9bf87815842e9623e77438142d8e80eace2d4fe2" --notHuman'
    subprocess.call(process, shell=True)
    #I have been unable to get this to work, therefore this is my best guess.
    #epi2me-cli-win-2.52.1246070.exe -a "9bf87815842e9623e77438142d8e80eace2d4fe2" --notHuman -w 1490 -i "C:\Users\zebbl\Documents\bioinformatics"
    
def update(telemetry):
    filename = telemetry + "_classification_16s_barcode-v1.csv"
    path = "C:\\Users\\" + user + "\\Downloads\\" + filename
    try:
        data = open(path, 'r')
    except:
        return
    reader = csv.reader(data)
    for line in reader:
        tax_id = line[4]
        read_id = line[1]
        accuracy = line[6]
        barcode = line[5]
        if read_id in reads or tax_id == "-1" or barcode not in validbars:
            continue
        reads.append(read_id)
        taxids[barcode][tax_id] = taxids[barcode].get(tax_id, 0) + 1
    data.close()
    os.remove(path)

def fileUpdate(fname, data):
    fhand = open(dirname + "\\" + fname, 'a+')
    data_dumps = json.dumps(data)
    fhand.write(data_dumps+"\n")
    fhand.close()

def goods(bar, species):
    if not len(species) == 0:
        n_organisms = 0
        for id in species[bar]:
            n_organisms += int(species[bar][id])
        if n_organisms != 0:
            goods_est = 1 - (len(species)/n_organisms)
        else:
            goods_est = "Undefined"
    else:
        goods_est = "Undefined"
    return float(goods_est)
           
#this function counts the number of singlets and doublets
#then calculates the value of chao's esitmator
#also calls goods estimate to put it into data
def tests(ids):
    results = dict()
    for bar in ids:
        results[bar] = dict()
        singlets = 0
        doublets = 0
        for id in ids[bar]:
            if ids[bar][id] == 1:
                singlets += 1
            elif ids[bar][id] == 2:
                doublets += 1
            else:
                continue
        #I'm not sure if this conditional has to be here, but I figured there would be cases where there were no singlets or doublets early in the process
        #Prevents the code from erroring out
        if doublets != 0 and singlets != 0:
            chao_est = float((singlets**2)/(2*doublets))
        else:
            chao_est = "Insufficient Data"
        goods_est = goods(bar, ids)
        dataForm = {"barcode" : bar, "singlets" : singlets, "doublets" : doublets, "chao_est" : chao_est, "goods" : goods_est, "timestamp" : timestamp()}
        fileUpdate("tests" + identifier + ".txt", dataForm)
        results[bar] = [chao_est, goods_est]
    return results
    
    
def testCheck(tel, taxids, verbose):
    try:
        getCSV(tel)
    except:
        dataForm = "Get CSV failed. Timestamp: " + timestamp()
        fileUpdate("tests" + identifier + ".txt", dataForm)
        time.sleep(30)
        return False
    update(tel)
    results = tests(taxids)
    for bar in results:
        if not (isinstance(results[bar][0], str) or isinstance(results[bar][1], str)) and (float(results[bar][0]) <= .1 and float(results[bar][1]) >= .990):
            if verbose:
                print("The run can be stopped!")
                print("Chao Estimator: " + bar + " " + str(results[bar][0]))
                print("Goods: " + bar + " " + str(results[bar][1]))
            break
    else:
        if verbose:
            for bar in results:
                print("Chao Estimator: " + bar + " " + str(results[bar][0]))
                print("Goods: " + bar + " " + str(results[bar][1]))
        return False
    return True

def getImmediateSubdirectories(a_dir):
    return [name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))]

def stopRuns(dirs):
    pass
    #This function has to stop both epi2me runs AND interact with the minIon run and stop it
    #MinIon doesnt appear to have an API


def telFinder(dir):
    print("telfindercalled")
    if os.path.isdir(dir):
        for file in os.listdir(dir):
            if 'telemetry' in file:
                return re.search('telemetry-(.*?).log', file).group(1)

print("Runnning " + __file__ + " with parameters:")
print(str(args).lstrip('Namespace'))

def getCSV(telemetry):
    driver = webdriver.Chrome(executable_path = "C:\\Users\\zebbl\\chromedriver.exe")
    driver.implicitly_wait(30)
    driver.get("https://epi2me.nanoporetech.com/workflow_instance/"+str(telemetry))
    username = driver.find_element_by_id("username")
    password = driver.find_element_by_id("password")
    username.send_keys(usernameID)
    password.send_keys(passwordID)
    driver.find_element_by_xpath('//a[@title="Log in"]').click()
    time.sleep(wait_time)
    print('starting download')
    driver.find_element_by_xpath('//a[@class="glyphicon glyphicon-file download-link"]').click()
    print('waiting 5 for dl')
    time.sleep(10)
    driver.close()
  

#Checks to see if the user specified an input, indicating they want to start a run
while running:
    results = testCheck(telnum, taxids, verbose)
    if results == True and autooff == True:
        if csv_get == True:
            getCSV(telemetry)
        running = False

    
                
    
    




       
#ideas for the code that may be useful:
#   adding code that will check for a minimum number of correct reads before performing chao's estimator
#       might help with inaccurate stops on the read


#CSV Parsing (Divided by barcodes and tests for each barcode)
#checking all paths for viability on all machines
#getting it operational through testing



