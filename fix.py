from __future__ import print_function
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

CLIENT_SECRET_FILE = 'client_secret.json'


def main():
    """Shows basic usage of the Vault API.
    Prints the names and IDs of the first 10 matters in Vault.
    """
    creds = None
    creds2 = None

    # If there are no (valid) credentials available, let the user log in.
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"Error: {CLIENT_SECRET_FILE} not found.")
        return

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

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

    service2 = build('storage', 'v1', credentials=creds)

    req = service2.objects().get_media(bucket=bucket_name, object=object_name)

    out_file = io.FileIO('exported_file.zip', 'wb')
    downloader = googleapiclient.http.MediaIoBaseDownload(out_file, req)

    done = False
    while done is False:
        status, done = downloader.next_chunk()

    print("File downloaded successfully.")

if __name__ == '__main__':
    main()
