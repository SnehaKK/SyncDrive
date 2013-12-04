#! /usr/bin/python

import json
import os
import requests
import db_util
import urllib
import urllib2

label = 'box'
display_label = 'Box'

def get_oauth_url():
	key = db_util.get_key(label)
	client_id = key['client_id']
	state = key['state'] 
	response_type = 'code'
	return 'https://www.box.com/api/oauth2/authorize?client_id=%(client_id)s&response_type=%(response_type)s&state=%(state)s' % locals()

def download_file(file_id,email):
	access_token = db_util.fetch_token(email,label,)
	#Get the Raw file content
	response = requests.get("https://api.box.com/2.0/files/%(file_id)s/content?access_token=%(access_token)s" % locals())
	#Get the name of the file
	raw_data = requests.get("https://api.box.com/2.0/files/%(file_id)s?access_token=%(access_token)s" % locals()).json()
	filename = os.path.join('/tmp', raw_data.get('name', 'file'))
	f = open(filename, 'w')
	f.write(response.content)
	f.close()
	return filename

def upload_file(filename,email):
    access_token = db_util.fetch_token(email,label)
    url = 'https://upload.box.com/api/2.0/files/content?access_token=%(access_token)s' % locals()
    r = requests.post(url, files={'file': open(filename, 'rb') } ,data = { 'parent_id': '0' }).json()
    try:
        return construct_file_record(r['entries'][0])
    except:
        return {}

def construct_file_record(record):
    fileRecord = {}
    fileRecord["id"]=record["id"]
    fileRecord["name"]=record["name"]
    fileRecord["link"]=record.get("download_url","")
    fileRecord["size"]=record.get("fileSize","")
    fileRecord["is_folder"] = (record.get("type", '') == 'folder')
    return fileRecord

def list_files(email,folder):
	access_token = db_util.fetch_token(email,label)
	folder = folder if folder else '0'
	url = "https://api.box.com/2.0/folders/%(folder)s/items?access_token=%(access_token)s" % locals()
	response = requests.get(url).json()
	files = []
	for record in response["entries"]:
		files.append(construct_file_record(record))
	return files

def refresh_token(email):
    key = db_util.get_key(label)
    url = 'https://www.box.com/api/oauth2/token'
    values = {
            'client_id' :key['client_id'] ,
            'client_secret' : key['client_secret'] ,
            'grant_type' : 'refresh_token' ,
            'refresh_token' : db_util.fetch_token(email, label, 'refresh_token')
            }
    response = requests.post(url,data = values).json()
    db_util.save_token(label,'access_token',response['access_token'], email)
    db_util.save_token(label,'refresh_token',response['refresh_token'], email)

if __name__ == "__main__":
	#print list_files('gaya.0408@gmail.com')
	#print download_file('11673767837','gaya.0408@gmail.com')
	print upload_file('/tmp/test.txt','gaya.0408@gmail.com')
	print 'done :)'
