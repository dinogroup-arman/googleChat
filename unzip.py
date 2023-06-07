import os
import zipfile
from datetime import datetime

datestr = datetime.today().strftime("%m-%d-%y")
mergestr = datestr + '-TRACE' + ".xlsx"

cwd = os.getcwd()
d = os.listdir(cwd)
extension = ".zip"

os.chdir(cwd) # change directory from working dir to dir with files

for item in os.listdir(cwd): # loop through items in dir
    if item.endswith(extension): # check for ".zip" extension
        file_name = os.path.abspath(item) # get full path of files
        zip_ref = zipfile.ZipFile(file_name) # create zipfile object
        zip_ref.extractall(cwd) # extract file to dir
        zip_ref.close() # close file
        os.remove(file_name) # delete zipped file 