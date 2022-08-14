import requests

def upload(path):
    with open(path, 'rb') as file: 
        my_file = {
        'file': file
        }
        
        headers = {
        "Authorization":"Bearer #BOT TOKEN#"
        }

        payload = { 
        "filename": #FILENAME#,
        "channels": '#CHANNEL#',
        }
        
        r = requests.post("https://slack.com/api/files.upload", params=payload, files=my_file, headers=headers)
        print(r.text)

