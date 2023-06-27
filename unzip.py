import os
import zipfile
from datetime import datetime

# Get the current date as a string
datestr = datetime.today().strftime("%m-%d-%y")

# Construct the target filename
mergestr = datestr + '-TRACE' + ".xlsx"

# Get the current working directory
cwd = os.getcwd()

# Specify the file extension to search for
extension = ".zip"

# Iterate over items in the current directory
for item in os.listdir(cwd):
    if item.endswith(extension):  # Check if the item has the specified extension
        file_name = os.path.abspath(item)  # Get the absolute path of the file
        try:
            # Create a ZipFile object
            zip_ref = zipfile.ZipFile(file_name)

            # Extract the contents of the ZIP file to the current directory
            zip_ref.extractall(cwd)

            # Close the ZipFile object
            zip_ref.close()

            # Remove the original ZIP file
            os.remove(file_name)

            # Print a success message
            print(f"Successfully extracted and deleted: {file_name}")
        except zipfile.BadZipFile:
            # Handle the case when the file is not a valid ZIP file
            print(f"Invalid ZIP file: {file_name}")
        except Exception as e:
            # Handle any other exceptions that may occur
            print(f"An error occurred while extracting {file_name}: {e}")
