from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
import datetime
from time import sleep
import googleapiclient.http

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/ediscovery']
SCOPES2 = ['https://www.googleapis.com/auth/devstorage.full_control']

t1 = datetime.datetime.today() - datetime.timedelta(days=1)
t1 = t1.strftime('%Y-%m-%d')
t2 = datetime.datetime.today() - datetime.timedelta(days=1)
t2 = t2.strftime('%Y-%m-%d')

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
            creds2.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'creds2.json', SCOPES2)
            creds2 = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle2', 'wb') as token:
            pickle.dump(creds2, token)

    service = build('vault', 'v1', credentials=creds)

    # Call the Vault API
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

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    export_name = f"XOutput-1-{timestamp}"

    wanted_export = {
        'name': export_name,
        'query': mail_query,
        'exportOptions': {
            'hangoutsChatOptions': {
                'exportFormat': 'MBOX'
            }
        }
    }

    ret = service.matters().exports().create(matterId=matter_id, body=wanted_export).execute()
    export_id = ret['id']
    object_name = ''
    bucket_name = ''
    while True:
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

    service2 = build('storage', 'v1', credentials=creds2)

    req = service2.objects().get_media(bucket=bucket_name, object=object_name)

    out_file = io.FileIO('exported_file.zip', 'wb')
    downloader = googleapiclient.http.MediaIoBaseDownload(out_file, req)

    done = False
    while done is False:
        status, done = downloader.next_chunk()

    print("File downloaded successfully.")

if __name__ == '__main__':
    main()