from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
from google.oauth2 import service_account
import googleapiclient.http
from time import sleep
import datetime

# If modifying these scopes, delete the file token.pickle.
# Scopes required for Google Vault API and Google Cloud Storage API
SCOPES = ['https://www.googleapis.com/auth/ediscovery']
SCOPES2 = ['https://www.googleapis.com/auth/devstorage.full_control']

# Get yesterday's date in the format 'YYYY-MM-DD'
t1 = datetime.datetime.today() - datetime.timedelta(days=1)
t1 = t1.strftime('%Y-%m-%d')
t2 = datetime.datetime.today() - datetime.timedelta(days=1)
t2 = t2.strftime('%Y-%m-%d')
t2 = t1  # Setting t2 to the same value as t1

# Uncomment the following lines if you want to specify a custom date range
# t1 = "2021-02-26"
# t2 = "2021-02-12"

print(t1)
print(t2)

def main():
    """Shows basic usage of the Vault API.
    Prints the names and IDs of the first 10 matters in Vault.
    """

    creds = None
    creds2 = None

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'creds1.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    if os.path.exists('token.pickle2'):
        with open('token.pickle2', 'rb') as token:
            creds2 = pickle.load(token)

    if not creds2 or not creds2.valid:
        if creds2 and creds2.expired and creds2.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'creds1.json', SCOPES2)
            creds2 = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle2', 'wb') as token:
            pickle.dump(creds2, token)

    # Build a service object for the Google Vault API
    service = build('vault', 'v1', credentials=creds)

    # Call the Vault API to list the first 10 matters
    results = service.matters().list(pageSize=10).execute()
    matters = results.get('matters', [])
    if not matters:
        print('No matters found.')
    else:
        print('Matters:')
        for matter in matters:
            print(u'{} ({})'.format(matter.get('name'), matter.get('id')))

    matter_id = '3876c97f-d2ae-4644-bdcb-22b1e787f858'

    mail_query = {
        "corpus": "HANGOUTS_CHAT",
        "dataScope": "ALL_DATA",
        "searchMethod": "ORG_UNIT",
        "startTime": t1 + "T00:00:00Z",
        "endTime": t2 + "T00:00:00Z",
        "method": "ORG_UNIT",
        "timeZone": "Etc/GMT",
        "orgUnitInfo": {
            "orgUnitId": "id:048g8hr82v93cca"
        },
        "hangoutsChatOptions": {
            "includeRooms": "true"
        }
    }

    wanted_export = {
        'name': 'Output-' + t2,
        'query': mail_query,
        'exportOptions': {
            "hangoutsChatOptions": {
                "exportFormat": "MBOX"
            }
        }
    }

    # Create an export in the specified matter
    ret = service.matters().exports().create(matterId=matter_id, body=wanted_export).execute()
    export_id = ret['id']
    object_name = ''
    bucket_name = ''

    while True:
        # Check the status of the export periodically
        status = service.matters().exports().get(matterId=matter_id, exportId=export_id).execute()
        if status['status'] == 'IN_PROGRESS':
            sleep(15)
            continue
        files = status['cloudStorageSink']['files']
        for x in files:
            if x['objectName'][len(x['objectName']) - 4:len(x['objectName'])] == '.zip':
                print("success")
                object_name = x['objectName']
                bucket_name = x['bucketName']
                break
            print(x['objectName'])
        break

    # Build a service object for the Google Cloud Storage API
    service = build('storage', 'v1', credentials=creds2)

    # Initialize a media request to download the exported file
    req = service.objects().get_media(bucket=bucket_name, object=object_name)

    out_file = io.BytesIO()
    downloader = googleapiclient.http.MediaIoBaseDownload(out_file, req)

    done = False
    while done is False:
        # Download the file in chunks
        status, done = downloader.next_chunk()
        # print("Download {}%.".format(int(status.progress() * 100)))

    file_name = 'new_file.zip'
    open(file_name, "wb").write(out_file.getvalue())


if __name__ == '__main__':
    main()
