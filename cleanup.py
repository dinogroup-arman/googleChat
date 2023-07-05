import os
import shutil
import subprocess
import sys

subprocess.run(["python", "unzip.py"])
subprocess.run(["python", "unzip.py"])


# Get the current working directory
cwd = os.getcwd()
d = os.listdir(cwd)
# d=os.listdir("Daily/")

files=[]
groups=[]

target=""
if len(sys.argv)>1:
	target=sys.argv[1]
if target!="":
	print(target)

for x in d:
	if x.endswith(".eml"):
		files.append(x)

dateSub=False
date1=""
date2=""
sub1=""
sub2=""

for x in range(0,len(files)):
	if files[x] in groups:
		continue
	for y in range(x,len(files)):
		dateSub=False
		dateSub=False
		date1=""
		date2=""
		sub1=""
		sub2=""
		if files[y]==target:
			print("Comparing File to "+files[x])
		if files[y] in groups:
			continue
		if x==y:
			continue
		f1=open("Daily/"+files[x]).readlines()
		f2=open("Daily/"+files[y]).readlines()
		count=0
		if abs(len(f1)-len(f2))>2:
			continue
		for z in range(0, len(f1)):
			if f1[z][0:6] == "Date: ":
				date1 = f1[z]
			if f1[z][0:9] == "Subject: ":
				sub1 = f1[z]
			if f2[z][0:6] == "Date: ":
				date2 = f2[z]
			if f2[z][0:9] == "Subject: ":
				sub2 = f2[z]
			if f1[z] != f2[z]:
				count += 1
			if count > 5:
				break
		if date1==date2 and sub1==sub2:
			dateSub=True
		if files[y]==target:
			print("Compared to "+files[x]+": count-"+str(count)+" dateSub-"+str(dateSub))
		if count<=8 and dateSub:
			if files[y]==target:
				print(target+" matched with "+files[x])
			groups.append(files[y])

print(len(groups))

for x in groups:
        shutil.move("Daily/"+x,"Daily/Group/"+x)
