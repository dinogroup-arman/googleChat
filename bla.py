import os

# Set the directory path to the current working directory (cwd)
directory = os.getcwd()

# Get a list of files in the directory
files = os.listdir(directory)

# Loop through each file
for file_name in files:
    # Check if the file is an mbox file
    if file_name.endswith(".mbox"):
        # Extract the day and month from the file name
        day, month = file_name.split("-")[3].split("_")[0].split(".")[0], file_name.split("-")[2]

        # Print the extracted day and month
        print("File:", file_name)
        print("Day:", day)
        print("Month:", month)
        print()
