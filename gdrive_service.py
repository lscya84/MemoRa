import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_gdrive_service():
    creds = None
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
            if not os.path.exists('credentials.json'):
                raise Exception("credentials.json file not found. Please place it in the root directory.")
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            # In a server environment, we might need a different flow. 
            # But for simple use, we'll try this.
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def sync_from_gdrive(folder_id, target_dir="data/temp"):
    if not folder_id:
        return "Folder ID is missing."
    
    try:
        service = get_gdrive_service()
        os.makedirs(target_dir, exist_ok=True)
        
        # List files in the folder
        query = f"'{folder_id}' in parents and (mimeType contains 'audio/' or name contains '.mp3' or name contains '.wav' or name contains '.m4a')"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            return "No audio files found in the specified folder."

        count = 0
        for item in items:
            file_id = item['id']
            file_name = item['name']
            file_path = os.path.join(target_dir, file_name)
            
            if os.path.exists(file_path):
                continue # Skip already downloaded files
                
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            with open(file_path, "wb") as f:
                f.write(fh.getvalue())
            count += 1

        return f"Successfully synced {count} new files to {target_dir}."
    
    except Exception as e:
        return f"Error: {str(e)}"
