from datetime import datetime, timedelta

t = datetime.now() - timedelta(days=1)
t = t.strftime('%Y-%m-%d')
content = open("Output-" + t + "_0.mbox").read()
# print(content[0:1000])
content = content.split("\n")
count = 0
message = 0
path = "Daily/"
path2 = "Daily/processed"

def processMessage(start, end, arr):
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


    # Get today's date
    today = datetime.today()

    # Calculate yesterday's date
    yesterday = today - timedelta(days=1)

    # Extract the day and month from yesterday's date
    yesterday_day = yesterday.day
    yesterday_month = yesterday.month

    if sTime and eTime:  # Check if sTime and eTime are not empty
        sTime = sTime.replace("T", "-")
        sTime = sTime[:sTime.find(".")]
        eTime = eTime.replace("T", "-")
        eTime = eTime[:eTime.find(".")]
        eTime = datetime.strptime(eTime, '%Y-%m-%d-%H:%M:%S')
        time = int(((eTime - datetime.strptime(sTime, '%Y-%m-%d-%H:%M:%S')).total_seconds()) / 60)

    out=open(path+str(yesterday_month)+"-"+str(yesterday_day)+"-"+str(count)+".eml","w")
    out.write("X-GlobalRelay-MsgType: Google-Hangout-Chat\n")

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

# Loop through each line in the content
for x in range(0, len(content)):
    if content[x][0:5] == "From " and (content[x][len(content[x]) - 4:len(content[x]) - 1]) == "202":
        print(content[x])
        processMessage(message, x, content)
        count += 1
        message = x + 1

# Process the last message
processMessage(message, len(content), content)
