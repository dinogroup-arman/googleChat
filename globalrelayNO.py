import smtplib
import ssl
import os
import shutil
import sys
import subprocess


# # Run the tryout.py script
# subprocess.run(["python", "tryout.py"])

if len(sys.argv)>1:
	path=sys.argv[1]
else:
	path="Daily/"

#month=sys.argv[2]

files=[]

for x in os.listdir(path):
        if x.endswith(".eml"):
                files.append(x)

#message = open("test3.eml").read()
#print(message)
user="ZGlub2dyb3VwLmNvbUBtYWlsYXJjaGl2ZXNwb29sMS5nbG9iYWxyZWxheS5jb20="
password="VWRXNlZIN0VPUWFFNGgzNlFxR1A="

user1="dinogroup.com@mailarchivespool1.globalrelay.com"
password1="UdW6VH7EOQaE4H36QqGP"
password2="UdW6VH7EOQaE4h36QqGP"
context = ssl.create_default_context()
#smtpObj = smtplib.SMTP('mailarchivespool1.globalrelay.com',25)
smtpObj = smtplib.SMTP('208.81.212.70',25)
#smtpObj.set_debuglevel(1)
smtpObj.starttls()
smtpObj.ehlo()
smtpObj.login(user1,password2)

# for x in files:
# 	print(x)
# 	f=open(path+x,"r")
# 	message=f.read()
# 	f.close()
# 	smtpObj.sendmail('asantos@dinogroup.com', 'dinogroup.com+GHC@mailarchivespool1.globalrelay.com', message)
# 	print("Successfully sent email")


for x in files:
	print(x)
	f=open(path+x,"r")
	message=f.read()
	f.close()
	smtpObj.sendmail('atokgoz@dinogroup.com', 'dinogroup.com+GHC@mailarchivespool1.globalrelay.com', message)
	print("Successfully sent email")

smtpObj.close()

for x in files:
        shutil.move(path+x,path+"processed/"+x)
