from datetime import datetime
from datetime import timedelta
import os
import dateutil.parser

month = 0
day = 0

def processMessage(start, end, arr):
    global count
    if start == end:
        return
    sponge = False
    # print(start)
    # print(end)
    h = ""
    users = 0
    messages = 0
    time = 0
    for x in range(start, end):
        # print(x)
        if arr[x][0:3] == "To:":
            users = 1 + arr[x].count(",")
        if arr[x][0:6] == "<html>":
            sponge = True
        if sponge:
            h += arr[x][0:len(arr[x]) - 1]
        if "</html>" in arr[x]:
            sponge = False
    messages = h.count("</li>")
    sTime = ""
    eTime = ""
    # print(len(h))
    while (h != ""):
        if (h.find("</b>") == -1):
            break
        s = h.find("</b>")
        e = h[s:].find("</p>") + s
        if sTime == "":
            sTime = h[s + 5:e]
        eTime = h[s + 5:e]
        h = h[s + 5:]
    try:
        sTime = datetime.strptime(sTime, '%Y-%m-%d-%H:%M:%S')
        eTime = datetime.strptime(eTime, '%Y-%m-%d-%H:%M:%S')
        time = int(((eTime - sTime).total_seconds()) / 60)
    except ValueError:
        time = 0
    file = os.path.basename(arr[0])
    fileName = file.split("_")[0]
    try:
        month = int(fileName[5:7])
        day = int(fileName[8:10])
    except ValueError:
        month = 0
        day = 0
        if file.endswith('.mbox'):
            path = "Daily/0-0.eml"
        else:
            path = file
    else:
        if month > 0 and day > 0:
            path = "Daily/" + str(month) + "-" + str(day) + ".eml"
        else:
            path = "Daily/" + str(month) + "-" + str(day) + ".eml"
    if os.path.exists(path):
        out = open(path, "w")
        out.write("X-GlobalRelay-MsgType: Google-Hangout-Chat\n")
        for x in range(start, end):
            if arr[x][0:8] == "Subject:":
                if time == 1:
                    out.write("Subject: chat, " + str(users) + " Users, " + str(messages) + " Messages, " + str(time) + " Minute\n")
                else:
                    out.write("Subject: chat, " + str(users) + " Users, " + str(messages) + " Messages, " + str(time) + " Minutes\n")
            else:
                out.write(arr[x] + "\n")
        out.close()
    else:
        print("File " + path + " does not exist")

count = 0
message = 0
path = "Daily/"

for file in os.listdir('.'):
    if file.endswith('.mbox') or file.endswith('.eml'):
        content = open(file, 'r').read()
        content = content.split('\n')
        processMessage(message, len(content), content)