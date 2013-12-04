#! /usr/bin/python

import json
import os
import requests
import db_util
import urllib

label = 'google_drive'
display_label = 'Google Drive'

def get_oauth_url():
	key = db_util.get_key(label)
	client_id = key['client_id']
	redirect_uri = key['redirect_uri'] 
	scope = key['scope']
	access_type = 'offline'
	response_type = 'code'
	return 'https://accounts.google.com/o/oauth2/auth?scope=%(scope)s&redirect_uri=%(redirect_uri)s&client_id=%(client_id)s&access_type=%(access_type)s&response_type=%(response_type)s' % locals()

def download_file(file_id,email):
	access_token = db_util.fetch_token(email,label)
	raw_data = requests.get("https://www.googleapis.com/drive/v2/files/%(file_id)s?access_token=%(access_token)s" % locals()).json()
	filename = os.path.join('/tmp', raw_data.get('title', 'file'))
	f = open(filename, 'w')
	data = requests.get('%s&access_token=%s' % (raw_data['downloadUrl'], access_token))
	f.write(data.content)
	f.close()
	return filename

def upload_file(filename,email):
	access_token = db_util.fetch_token(email,label)
	url = 'https://www.googleapis.com/upload/drive/v2/files?uploadType=media&access_token=%(access_token)s' % locals()
	r = requests.post(url, data = open(filename, 'rb').read())
	file_id = json.loads(r.text)['id']
	url = "https://www.googleapis.com/drive/v2/files/%(file_id)s?access_token=%(access_token)s" % locals()
	r = requests.put(url, 
				     data = json.dumps({'title': os.path.basename(filename)}),
				     headers = {'Content-Type': "application/json"}).json()
	return construct_file_record(r)

def construct_file_record(record):
	fileRecord = {}
	fileRecord["id"]=record["id"]
	fileRecord["name"]=record["title"]
	fileRecord["link"]=record.get("webContentLink","")
	fileRecord["size"]=record.get("fileSize","0")
	fileRecord["is_folder"] = (record.get("mimeType", '') == 'application/vnd.google-apps.folder')
	return fileRecord

def list_files(email,folder):
	access_token = db_util.fetch_token(email,label)
	folder = folder if folder else 'root'
	query = urllib.quote("\'%(folder)s\' in parents" % locals())
	url = "https://www.googleapis.com/drive/v2/files?access_token=%(access_token)s&q=%(query)s" % locals()
	response = requests.get(url).json()
	files = []
	for record in response["items"]:
		files.append(construct_file_record(record))
	return files

def refresh_token(email):
    key = db_util.get_key(label)
    url = 'https://accounts.google.com/o/oauth2/token'
    values = {
            'client_id' :key['client_id'] ,
            'client_secret' : key['client_secret'] ,
            'grant_type' : 'refresh_token' ,
            'refresh_token' : db_util.fetch_token(email,label,"refresh_token")
    }
    response = requests.post(url,data = values).json()
    db_util.save_token(label,'access_token',response['access_token'], email)

if __name__ == "__main__":
	#print list_files('gaya.0408@gmail.com')
	#print gd_download_file('0B2xo1MFqnLo5dUtfRHVMbExvZWc','ya29.AHES6ZTZz8XGWDowjsgQs8InH5BKFxuFCaBDcr2JCkLbFjQ7Ww')
	#gd_upload_file('templates/hello.html','ya29.AHES6ZQIKpE9Cbypa1jLXGtlmJAZqFMYz5cvlpFwfn5zpq7kMFUDcVnj')
	upload_file('/tmp/test.txt', 'gaya.0408@gmail.com')
	print 'done :)'
