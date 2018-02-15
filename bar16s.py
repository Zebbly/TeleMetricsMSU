#16sbar

import subprocess

def bar16s(input):
    barout_folder = input + "\barcoded"
    stsout_folder = input + "\ouput"
    subprocess.call('epi2me-cli-win-2.50.1003370.exe -a "9bf87815842e9623e77438142d8e80eace2d4fe2" -w 1490 -i ' + input + ' -o ' + barout_folder, shell=True)
    subprocess.call('epi2me-cli-win-2.50.1003370.exe -a "9bf87815842e9623e77438142d8e80eace2d4fe2" -w 1490 -i ' + barout_folder + ' -o ' + stsout_folder, shell=True)
    