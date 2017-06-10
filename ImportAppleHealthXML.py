
# coding: utf-8

# # Download,  Parse and Interrogate Apple Health Export Data
# 
# This file was created from a desire to get my hands on data collected by Apple Health, notably heart rate information collected by Apple Watch. For this to work, this file needs to be in a location accessible to Python code. A little bit of searching told me that iCloud file access is problematic and that there were already a number of ways of doing this with the Google API if the file was saved to Google Drive. I chose PyDrive. So for the end to end program to work with little user intervention, you will need to sign up for Google Drive, set up an application in the Google API and install Google Drive app to your iPhone. 
# 
# This may sound involved, and it is not necessary if you simply email the export file to yourself and copy it to a filesystem that Python can see. If you choose to do that, all of the Google Drive portion can be removed. I like the Google Drive process though as it enables a minimal manual work scenario.
# 
# This version requires the user to grant Google access, requiring some additional clicks, but it is not too much. I think it is possible to automate this to run without user intervention as well using security files.
# The first step to enabling this process is exporting the data from Apple Health. As of this writing, open Apple Health and click on your user icon or photo. Near the bottom of the next page in the app will be a button or link called Export Health Data. Clicking on this will generate a xml file, zipped up. THe next dialog will ask you where you want to save it. Options are to email, save to iCloud, message etc...  Select Google Drive. Google Drive allows multiple  files with the same name and this is accounted for by this program.

import xml.etree.ElementTree as et
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import re 

#get_ipython().magic(u'matplotlib inline')
plt.rcParams['figure.figsize'] = 16, 8


# ##  Authenticate with Google 
# This will open a browser to let you beging the process of authentication with an existing Google Drive account. This process will be separate from Python. For this to work, you will need to set up a Other Authentication OAuth credential at https://console.developers.google.com/apis/credentials, save the secret file in your root directory and a few other things that are detailed at https://pythonhosted.org/PyDrive/. The PyDrive instructions also show you how to set up your Google application. There are other methods for accessing the Google API from python, but this one seems pretty nice. 
# The first time through the process, regular sign in and two factor authentication is required (if you require two factor auth) but after that it is just a process of telling Google that it is ok for your Google application to access Drive.

# Authenticate into Google Drive
print("\n\nNOTE: You may receive an error message on MacOS about not knowing how to open a browser.\nIf this happens, cut and paste the url below into your browser and continue the authentication\n\n")
from pydrive.auth import GoogleAuth

gauth = GoogleAuth()
gauth.LocalWebserverAuth() 


# ### Download the most recent Apple Health export file
# Now that we are authenticated into Google Drive, use PyDrive to access the API and get to files stored.
# Google Drive allows multiple files with the same name, but it indexes them with the ID to keep them separate.
# In this block, we make one pass of the file list where the file name is called export.zip, and save the row that corresponds with the most recent date. We will use that  file id later to download the correct file that corresponds  with the most recent date. Apple Health export names the file export.zip, and at the time this was written, there is no other option.

from pydrive.drive import GoogleDrive
drive = GoogleDrive(gauth)

file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()

# Step through the file list and find the most current export.zip file id, then use 
#      that later to download the file to the local machine.
# This may look a little old school, but these file lists will never be massive and 
#     it is readable and easy one pass way to get the most current file using the 
#     least (or low) amount of resouces
selection_dt = datetime.strptime("2000-01-01T01:01:01.001Z","%Y-%m-%dT%H:%M:%S.%fZ")
print("Matching Files for most recent upload identification")
for file1 in file_list: 
    if re.search("^export.zip",file1['title']):
        dt = datetime.strptime(file1['createdDate'],"%Y-%m-%dT%H:%M:%S.%fZ")
        if dt > selection_dt:
            selection_id = file1['id']
            selection_dt = dt
        print('    title: %s, id: %s createDate: %s' % (file1['title'], file1['id'], file1['createdDate']))


# ## Download the file from Google Drive
# Ensure that the file downloaded is the latest file generated

for file1 in file_list:
        if file1['id'] == selection_id:
            print('Downloading this file: %s, id: %s createDate: %s' % (file1['title'], file1['id'], file1['createdDate']))
            file1.GetContentFile("healthextract/export.zip")


import zipfile
print('Unzipping into healthextract for use')
zip_ref = zipfile.ZipFile('healthextract/export.zip', 'r')
zip_ref.extractall('healthextract')
zip_ref.close()

# ## Parse Apple Health Export document

print('Parsing XML...')
path = "healthextract/apple_health_export/export.xml"
e = et.parse(path)


# ## List XML headers by element count
pd.Series([el.tag for el in e.iter()]).value_counts()


# ## List types for "Record" Header

pd.Series([atype.get('type') for atype in e.findall('Record')]).value_counts()

#Extract Values to Data Frame
#Extract the heartrate values, and get a timestamp from the xml
# there is likely a more efficient way, though this is very fast
def xmltodf(element,outvaluename):
    dt = []
    v = []
    for atype in e.findall('Record'):
        if atype.get('type') == element:
            dt.append(datetime.strptime(atype.get("startDate"),"%Y-%m-%d %H:%M:%S %z"))
            v.append(atype.get("value"))
    myd = pd.DataFrame({"Create":dt,outvaluename:v})
    myd['Month'] = myd['Create'].apply(lambda x: x.strftime('%Y-%m'))
    myd['Day'] = myd['Create'].apply(lambda x: x.strftime('%d'))
    myd['Hour'] = myd['Create'].apply(lambda x: x.strftime('%H'))

    myd[outvaluename] = myd[outvaluename].astype(float).astype(int)
    print('Extracting ' + outvaluename + ', type: ' + element)
    return(myd)

HR_df = xmltodf("HKQuantityTypeIdentifierHeartRate","HeartRate")
SC_df = xmltodf("HKQuantityTypeIdentifierStepCount","StepCount")

print("Plotting Month by Heartrate")
HR_df.boxplot(by='Month',column="HeartRate", return_type='axes')
plt.savefig('graphs/MonthbyHR.pdf')
plt.close()


monthlock='2017-05'
print("Plotting Day by Heartrate for " + monthlock)
HR_df[HR_df['Month']==monthlock].boxplot(by='Day',column="HeartRate", return_type='axes')
plt.savefig('graphs/DaybyHR' + monthlock + '.pdf')
plt.close()


print("Plotting Hour of Day by Heartrate for " + monthlock)
HR_df[HR_df['Month']==monthlock].boxplot(by='Hour',column="HeartRate")
plt.savefig('graphs/HourbyHR' + monthlock + '.pdf')
plt.close()


import numpy as np
import seaborn as sns
sns.set(style="ticks", palette="muted", color_codes=True)

print("Plotting Month by Heartrate using Seaborn")
sns.boxplot(x="Month", y="HeartRate", data=HR_df,whis=np.inf, color="c")
# Add in points to show each observation
snsplot = sns.stripplot(x="Month", y="HeartRate", data=HR_df,jitter=True, size=1, alpha=.25, color=".3", linewidth=0).get_figure()
snsplot.savefig('graphs/Seaborn_MonthbyHR.pdf') 
print("Done...")