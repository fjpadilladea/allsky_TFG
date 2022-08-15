import requests
# import os

def upload(path):
    """
    Uploads a file to a Slack channel.
    IMPORTANT: modify this script with the actual values
    of the token and the channel.
    """
    with open(path, 'rb') as file: 
        my_file = {
        'file': file
        }
        
        headers = {
        "Authorization":"Bearer #BOT TOKEN#"
        }

        payload = { 
	# To get the last element of the path for the filename:
	# "filename": path.split(os.path.sep)[-1],
        "filename": #FILENAME#,
        "channels": '#CHANNEL#',
        "initial_comment": 'New detection!',
        }
        
        r = requests.post("https://slack.com/api/files.upload", params=payload, files=my_file, headers=headers)
        print(r.text)
