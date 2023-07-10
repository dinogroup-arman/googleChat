from datetime import datetime, timedelta
import subprocess
import glob
import os
import shutil

# Run the cleanup.py script
subprocess.run(["python", "cleanup.py"])

t = datetime.now() - timedelta(days=1)
t = t.strftime('%Y-%m-%d')
path = "Daily/"
processed_path = os.path.join(path, "processed")
mbox_path = os.path.join(path, "mbox")

# Create the "processed" and "mbox" directories if they don't exist
os.makedirs(processed_path, exist_ok=True)
os.makedirs(mbox_path, exist_ok=True)

# Set the directory path to the current working directory (cwd)
directory = os.getcwd()

# Get a list of mbox files in the directory
mbox_files = glob.glob("*.mbox")

for mbox_file in mbox_files:
    # Extract the day and month from the file name
    day, month = mbox_file.split("-")[3].split("_")[0].split(".")[0], mbox_file.split("-")[2]

    # Print the extracted day and month
    print("File:", mbox_file)
    print("Day:", day)
    print("Month:", month)
    print()

    # Read the content of the mbox file
    content = open(mbox_file).read()

    content = content.split("\n")
    count = 0
    message = 0

    def processMessage(start, end, arr, month, day):
        global count
        if start == end:
            return
        sponge = False
        h = ""
        users = 0
        messages = 0
        time = 0
        sTime = ""
        eTime = ""

        for x in range(start, end):
            if arr[x][0:3] == "To:":
                users = 1 + arr[x].count(",")
            if arr[x][0:6] == "<html>":
                sponge = True
            if sponge:
                h += arr[x][0:len(arr[x]) - 1]
            if "</html>" in arr[x]:
                sponge = False
        messages = h.count("</li>")
        while h != "":
            if h.find("</b>") == -1:
                break
            s = h.find("</b>")
            e = h[s:].find("</p>") + s
            if sTime == "":
                sTime = h[s + 5:e]
            eTime = h[s + 5:e]
            h = h[s + 5:]

        print("sTime:", sTime)
        print("eTime:", eTime)

        if sTime and eTime:  # Check if sTime and eTime are not empty
            sTime = sTime.replace("T", "-")
            sTime = sTime[:sTime.find(".")]
            eTime = eTime.replace("T", "-")
            eTime = eTime[:eTime.find(".")]
            eTime = datetime.strptime(eTime, '%Y-%m-%d-%H:%M:%S')
            time = int(((eTime - datetime.strptime(sTime, '%Y-%m-%d-%H:%M:%S')).total_seconds()) / 60)

        out = open(os.path.join(processed_path, "{}-{}-{}.eml".format(month, day, count)), "w")
        out.write("X-GlobalRelay-MsgType: Google-Hangout-Chat\n")
        out.write("Date: {}-{}-{}\n".format(month, day, datetime.now().year))  # Add the date to the eml file

        print("sTime:", sTime)
        print("eTime:", eTime)

        for x in range(start, end):
            if arr[x][0:8] == "Subject:":
                if time == 1:
                    out.write("Subject: chat, " + str(users) + " Users, " + str(messages) + " Messages, " + str(
                        time) + " Minute\n")
                else:
                    out.write("Subject: chat, " + str(users) + " Users, " + str(messages) + " Messages, " + str(
                        time) + " Minutes\n")
            else:
                out.write(arr[x] + "\n")
        out.close()

        count += 1

    # Loop through each line in the content
    for x in range(0, len(content)):
        if content[x][0:5] == "From " and (content[x][len(content[x]) - 4:len(content[x]) - 1]) == "202":
            print(content[x])
            processMessage(message, x, content, month, day)
            message = x + 1

    # Process the last message
    processMessage(message, len(content), content, month, day)

    # # Move the mbox file to the "mbox" directory
    # shutil.move(mbox_file, os.path.join(mbox_path, mbox_file))
