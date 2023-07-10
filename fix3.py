from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
from time import sleep
import googleapiclient.http

SCOPES = ['https://www.googleapis.com/auth/ediscovery', 'https://www.googleapis.com/auth/devstorage.full_control', 'https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/devstorage.read_only']

t1 = datetime.datetime.today() - datetime.timedelta(days=1)
t1 = t1.strftime('%Y-%m-%d')
t2 = datetime.datetime.today() - datetime.timedelta(days=1)
t2 = t2.strftime('%Y-%m-%d')


def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('creds1.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('vault', 'v1', credentials=creds)

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
        # Get today's date
    today = datetime.date.today()

    # Calculate yesterday's date
    yesterday = today - datetime.timedelta(days=1)

    # Format yesterday's date as "YYYY-MM-DD"
    formatted_yesterday = yesterday.strftime('%Y-%m-%d')

    current_date = datetime.datetime.today().strftime('%Y-%m-%d')
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    export_name = f"Output-{formatted_yesterday}"

    wanted_export = {
        'name': export_name,
        'query': mail_query,
        'exportOptions': {
            'hangoutsChatOptions': {
                'exportFormat': 'MBOX'
            }
        }
    }

    print("[{}] Initiating export...".format(get_current_time()))
    ret = service.matters().exports().create(matterId=matter_id, body=wanted_export).execute()
    export_id = ret['id']
    object_name = ''
    bucket_name = ''

    print("[{}] Export in progress...".format(get_current_time()))
    while True:
        status = service.matters().exports().get(matterId=matter_id, exportId=export_id).execute()
        if status['status'] == 'IN_PROGRESS':
            sleep(15)
            continue
        files = status['cloudStorageSink']['files']
        for x in files:
            if x['objectName'].endswith('.zip'):
                print("[{}] Export completed successfully!".format(get_current_time()))
                object_name = x['objectName']
                bucket_name = x['bucketName']
                break
            print(x['objectName'])
        break

    service2 = build('storage', 'v1', credentials=creds)

    req = service2.objects().get_media(bucket=bucket_name, object=object_name)

    out_file = os.path.join(os.getcwd(), 'exported_file.zip')
    downloader = googleapiclient.http.MediaIoBaseDownload(open(out_file, 'wb'), req)

    done = False
    print("[{}] Downloading export file...".format(get_current_time()))
    while done is False:
        status, done = downloader.next_chunk()
        print("[{}] Download progress: {}%".format(get_current_time(), int(status.progress() * 100)))

    print("[{}] File downloaded successfully!".format(get_current_time()))


def get_current_time():
    return datetime.datetime.now().strftime("%H:%M:%S")


if __name__ == '__main__':
    main()
