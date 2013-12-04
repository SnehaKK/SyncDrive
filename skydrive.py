#! /usr/bin/python

import json
import requests
import os
import db_util
import urllib

label = 'skydrive'
display_label = 'Skydrive'

def get_oauth_url():
	key = db_util.get_key(label)
	client_id = key['client_id']
	redirect_uri = key['redirect_uri'] 
	scope = key['scope'] 
	response_type = 'code'
	return 'https://login.live.com/oauth20_authorize.srf?scope=%(scope)s&redirect_uri=%(redirect_uri)s&client_id=%(client_id)s&response_type=%(response_type)s' % locals()

def upload_file(filename, email):
	access_token = db_util.fetch_token(email,label)
	url = 'https://apis.live.net/v5.0/me/skydrive/files?access_token=%(access_token)s' % locals()
	uploaded_file = requests.post(url, files={'file': open(filename, 'rb')}).json()['id']
	r = requests.get("https://apis.live.net/v5.0/%(uploaded_file)s?access_token=%(access_token)s)" % locals()).json()
	return construct_file_record(r)

def download_file(file_id, email):
    access_token = db_util.fetch_token(email,label)
    file_id = urllib.unquote_plus(file_id.replace('ZZZZZ', '%'))
    raw_data = requests.get("https://apis.live.net/v5.0/%(file_id)s?access_token=%(access_token)s)" % locals()).json()
    filename = os.path.join('/tmp', raw_data.get('name', 'file'))
    data = requests.get('%s&access_token=%s' % (raw_data['source'], access_token))
    f = open(filename, 'w')
    f.write(data.content)
    f.close()
    return filename

def construct_file_record(record):
	fileRecord = {}
	fileRecord["id"]=urllib.quote_plus(record["id"]).replace('%', 'ZZZZZ')
	fileid = record["id"]
	fileRecord["name"]=record["name"]
	fileRecord["link"]=record.get("source","")
	fileRecord["size"]=record["size"]
	fileRecord["is_folder"] = (record['id'].split('.')[0] == "folder")
	return fileRecord

def list_files(email,folder):
	access_token = db_util.fetch_token(email,label)
	url = "https://apis.live.net/v5.0/me/skydrive/files?access_token=%(access_token)s" % locals()
	if folder:
		url = "https://apis.live.net/v5.0/%(folder)s/files?access_token=%(access_token)s" % locals()
	response = requests.get(url).json()
	listFiles = []
	for record in response["data"]:
		listFiles.append(construct_file_record(record))
	return listFiles

def refresh_token(email):
	key = db_util.get_key(label)
	url = 'https://login.live.com/oauth20_token.srf'
	values = {
		'client_id' :key['client_id'] ,
		'redirect_uri' : key['redirect_uri'] ,
		'client_secret' : key['client_secret'] ,
		'grant_type' : 'refresh_token' ,
		'refresh_token' : db_util.fetch_token(email,label,'refresh_token')
	}
	response = requests.post(url,data = values).json()
	db_util.save_token(label,'access_token',response['access_token'], email)
	db_util.save_token(label,'refresh_token',response['refresh_token'], email)

if __name__ == '__main__':
	upload_file('/tmp/test.txt', 'gaya.0408@gmail.com')
	#download_file('file.5d1d0df0479ac5c9.5D1D0DF0479AC5C9!250', 'gaya.0408@gmail.com')
	#print list_files('gaya.0408@gmail.com','folder.5d1d0df0479ac5c9.5D1D0DF0479AC5C9!154')
	#sd_download_file('file.5d1d0df0479ac5c9.5D1D0DF0479AC5C9!250','EwAwAq1DBAAUGCCXc8wU/zFu9QnLdZXy+YnElFkAAcLvq3EQeMCRAIx5zKMNY0DGK2I6P8vBDknDU61fE9lHvNRLTh01fVJ5v8d6MlYjsUOdd9iKs/wTwSlvy+mfhOYQ3IoBGpcYEJPaIrnQRMC9oRCJR3iWwXUqYdvsbS+5fl5t0qsyie397D1P9GbEkI2H1nqHWEBBVO7IcTMrP1Gb0mO5aS4osoqQ/mTKTa5015hNwDyK1VTcsJ9sj9oBYJNA3K7BYmb9wxmIrBVXBFdNZ2AP1dTxZ0qZmjUppD5dltA+VIr+77MZdIQpDGjbE9x1mRRyCFyoTw0tXLEouJhYjru6enY2P68qEDSbgqFBywecrfkgm4tBKAYGNZkgn50DZgAACKe4tSkAEtApAAG6FvWB7ijA190ANcBl27YUc6uN5/ulvZUDoNPrY5zvKwGHZCY4uhTi4sYG63loo/k0cXHy6lPqjPNf4e9U4rOdMxPY5eXPVDD0gBHO9DbdeLmukf1YuHKrK9koYL05X/CD8dLq3aN9CQEyRFoviDj9DggAJ+RB+zaIDZ2mOZgXDWrgRUNh704ykjQ7Y5PhH3T9Zj7XSHcRSrZzCgJYp0UFzNJEpblyqarSd/ftk2mXMaid3h8STXXX6rabVi9mXLvbVdTHyjOLipfmydzjss0y6w6q5mp+cecgv8JZkp4cWU0cMRHDKSisPdpMW0tezpCKr3Q8N0nrwWYMiS9W5khpAAA=')
	#sd_upload_file('/tmp/aws-sjsu-key.pem', 'EwAwAq1DBAAUGCCXc8wU/zFu9QnLdZXy+YnElFkAAdyvyBb7dUPxcs+A1eORq0kZnQIgSUTNNRYRjw/qIiE7we3Wav687rdfgopEaXnhAvtLflwrpm7hucVvIyVgJx7ODJqrLEDPyyrnLpUE0HO2iQvDlF5DSwHw7a57xGEomEV81W0m8HsbynxtThpBNXnR6q9i1FD+tjSM7oyiPl/J9Ofm1nKOp6UtZs8qSkHRm1Bc4bFHsjLCCPy+/hsUnl4IocvVdy6FUf96NuK7//K2+vXkFEAagbi0OLQN+WtSOGhCmvAbb942dQCD4ohBjp67XCydwH5TOnw46/EuEkke5zD3k5b1CfN0/+BBT8xidUx6uaSVZGyI+Tn2EarlBhADZgAACBYCLb9tTOrAAAHDfT3nq5PVIetO7cOoGCd+jXTM0qlcpvmUECG84a4veXM+95BExZviaVFbeTv4ASyfh9MI/iD5pAWwVhy9M0nbcGa27bP3rgtpg2Wc2ussBATPEQ8w9UxZrQdiE0WGhHwIdLnHSdYXzfYl8jGGDtJ/FbXqW1FXgjzV7PUginbj9GrAbwYda4CszDg98DRKlJWW3nBd8l6ycbdcx2xH/WnSu4v6M1jgRrd55sLUj4FwELXrVOgqVl0zE3JRchvyWFuVD+doFWwIPW4lWPaBsqJZ1Ax4rQ5QuVzBK8wSqFBKSP7zx+/1RmMF3zT6TX14AugMmTITSyS4FTctQ9nfQ/eOAAA=')
