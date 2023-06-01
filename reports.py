from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sys
import os

ids={"dino":"id:048g8hr82v93cca","dmc":"id:048g8hr82htxgd9","rmr":"id:048g8hr81ioznhn","dcm2":"id:048g8hr83dst3cs","park":"id:048g8hr80wz7ql2","mdm":"id:048g8hr84cxqw8e","rmr2":"id:048g8hr81sy3dkl","dghllc":"id:03ph8a2z1z8ygal","dinoeu":"id:048g8hr833jpd9u"}
events={}
missing=[]
optionAll=False
name="reportsOutput.csv"
SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly']

def pull(idNum):
    creds = None
    if os.path.exists('token3.pickle'):
        with open('token3.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'creds1.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token3.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('admin', 'reports_v1', credentials=creds)
    results=None
    if idNum=="all":
        results = service.activities().list(userKey='all', applicationName='admin').execute()
    else:
        results = service.activities().list(orgUnitID=idNum,userKey='all', applicationName='admin').execute()
    activities = results.get('items', [])
    print(idNum+": "+str(len(activities)))
    return activities

class Event:
    event=""
    string=""
    parameters=[]
    desc=""
    admin=""
    date=""
    ip=""

def getEvents():
    f=open("events.txt").read()
    f=f.split("\n")
    f.remove('')
    for x in f:
        y=x.split(",")
        if len(y)<2:
            print(f)
            print("Bad Format: "+x)
            exit()
        retStr=""
        for g in y[1:]:
            retStr+=g
        events[y[0]]=g

def parseDesc(s,arr):
    for x in arr:
        if "{"+x["name"]+"}" in s:
            s=s.replace("{"+x["name"]+"}",x["value"])
    return s

for x in range(1,len(sys.argv)):
    if sys.argv[x]=="-a":
        optionAll=True
        print("Pulling all logs")
    if sys.argv[x]=="-f":
        if len(sys.argv)<=x+1:
            print("Bad format. Usage: python reportPull.py [-a] [-f fileName]")
            exit()
        name=sys.argv[x+1]
        print("Using filename: "+name)

getEvents()
f=None
if os.path.isfile(name):
    f=open(name,"a")
else:
    f=open(name,'w')
    f.write("Event Name,Event Description,Admin,Date,IP Address\n")
ret=[]

data=[]
data2=[]
data3=[]
data=pull("all")
if not optionAll:
    for x in ids:
        if x=="dinoeu" or x=="dghllc":
            data2.extend(pull(ids[x]))
        else:
            data3.extend(pull(ids[x]))
    for x in data2:
        if x in data:
            data.remove(x)
    for x in data3:
        if not x in data:
            data.append(x)

print("Activity count: "+str(len(data)))

for x in data:
    e=Event()
    e.event=x["events"][0]["type"]
    e.string=x["events"][0]["name"]
    e.date=x["id"]["time"]
    if "ipAddress" in x:
        e.ip=x["ipAddress"]
    else:
        e.ip=""
    if "actor" in x and "email" in x["actor"]:
        e.admin=x["actor"]["email"]
    if e.string in events:
        e.string=events[e.string]
    else:
        if not e.string in missing:
            missing.append(e.string)
        if "parameters" in x["events"][0]:
            for y in x["events"][0]["parameters"]:
                e.desc+=y["name"]+": "+y["value"]+" "
                e.desc=e.desc.replace(","," ")
        ret.append(e)
        continue
    if "parameters" in x["events"][0]:
        e.parameters=x["events"][0]["parameters"]
        e.desc=parseDesc(e.string,e.parameters)
    else:
        #print("No params: "+x["events"][0]["name"])
        e.desc=e.string
    e.desc=e.desc.replace(","," ")
    e.desc=e.desc.replace("\n"," ")
    ret.append(e)

toWrite=[]
already=[]
if os.path.isfile(name):
    g=open(name,"r")
    already=g.readlines()
    g.close()
    
for x in ret:
    string=x.event+","+x.desc+","+x.admin+","+x.date+","+x.ip+"\n"
    if not string in already:
        toWrite.append(string)

print("Previously in file: "+str(len(already)))
print("Adding to file: "+str(len(toWrite)))

for x in toWrite:
    f.write(x)
f.close()

if len(missing)>0:
    print("Missing event tags:")
for x in missing:
    print(x)

