import io
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from datetime import date, timedelta
import glob
import pandas as pd
import threading

today = date.today() - timedelta(days=1)
today = today.strftime("%Y%m%d")
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    file = open("nomeArquivo.txt", "r")
    timer = threading.Timer(600.0, main)

    for line in file:
        fields = line.split(";")
        arquivo = fields[0]
        pastaAtualizacao = fields[1].replace('\n', '')
        pastaCopilado = fields[2].replace('\n', '')
        # Call the Drive v3 API
        results = service.files().list(
            pageSize=10,fields="nextPageToken, files(id, name, kind, mimeType)", q="name contains '"+arquivo + " "+today+ "'").execute()
        items = results.get('files', [])

        if items == '' or items == []:
            print('No files found.')
            timer.start()
        else:
            timer.cancel()
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))
                file_id = item['id']
                request = service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print("Download %d%%." % int(status.progress() * 100))
                dirName = pastaAtualizacao
                print(os.path.exists(dirName))
                if os.path.exists(dirName) == False:
                    print("Directory não existesss")
                else:
                    print("Directory ", dirName, " already exists")
                    with io.open(dirName + '/' + item['name'], 'wb') as f:
                        fh.seek(0)
                        f.write(fh.read())
                    extension = 'csv'
                    all_filenames = [i for i in glob.glob(pastaAtualizacao + '/'+arquivo+' '+today+'*.{}'.format(extension))]
                    combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])
                    if os.path.exists(pastaCopilado) == False:
                        print('pasta não existe')
                    else:
                        if os.path.exists(pastaCopilado + '/Consolidado '+arquivo+'.csv') == False:
                            combined_csv.to_csv(pastaCopilado + '/Consolidado '+arquivo+'.csv', index=False, mode='a', encoding='utf-8-sig')
                        else:
                            combined_csv.to_csv(pastaCopilado + '/Consolidado ' + arquivo + '.csv', index=False, mode='a', header=None, encoding='utf-8-sig')

if __name__ == '__main__':
   main()