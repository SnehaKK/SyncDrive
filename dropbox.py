#! /usr/bin/python

import json
import requests
import os
import db_util

label = 'dropbox'
display_label = 'Dropbox'
oauth_url = 'https://www.dropbox.com/1/oauth2/authorize?client_id=2u32491x5z496am&response_type=token&redirect_uri=https://googledrive.com/host/0B2xo1MFqnLo5VzVhWjlFamF4cEk/callback_dropbox.html'

def upload_file(filename, email):
	access_token = db_util.fetch_access_token(email,label)
	val = open(filename, 'rb').read()
	basename = os.path.basename(filename)
	url = 'https://api-content.dropbox.com/1/files_put/dropbox/%(basename)s?access_token=%(access_token)s' % locals()
	r = requests.put(url, data = open(filename, 'rb').read())
	print r.text

def download_file(file_id, email):
	access_token = db_util.fetch_access_token(email,label)
	raw_data = requests.get("https://api-content.dropbox.com/1/files/dropbox%(file_id)s?access_token=%(access_token)s" % locals())
	filename = os.path.join('/tmp', os.path.basename(file_id))
	f = open(filename, 'w')
	f.write(raw_data.content)
	f.close()
	return filename

def list_files(email,folder):
	access_token = db_util.fetch_access_token(email,label)
	url = "https://api.dropbox.com/1/metadata/dropbox/%(folder)s?access_token=%(access_token)s" % locals()
	response = requests.get(url).json()
	listFiles = []
	for record in response["contents"]:
		fileRecord = {}
		fileRecord["id"]=record["path"]
		fileRecord["name"]=os.path.basename(record["path"])
		fileRecord["link"]=""
		fileRecord["size"]=record["size"]
		fileRecord["is_folder"] = record["is_dir"]
		listFiles.append(fileRecord)
	return listFiles

if __name__ == '__main__':
	print upload_file('/tmp/aws-sjsu-key.pem', 'gaya.0408@gmail.com')
	#sd_download_file('file.5d1d0df0479ac5c9.5D1D0DF0479AC5C9!250','EwAwAq1DBAAUGCCXc8wU/zFu9QnLdZXy+YnElFkAAcLvq3EQeMCRAIx5zKMNY0DGK2I6P8vBDknDU61fE9lHvNRLTh01fVJ5v8d6MlYjsUOdd9iKs/wTwSlvy+mfhOYQ3IoBGpcYEJPaIrnQRMC9oRCJR3iWwXUqYdvsbS+5fl5t0qsyie397D1P9GbEkI2H1nqHWEBBVO7IcTMrP1Gb0mO5aS4osoqQ/mTKTa5015hNwDyK1VTcsJ9sj9oBYJNA3K7BYmb9wxmIrBVXBFdNZ2AP1dTxZ0qZmjUppD5dltA+VIr+77MZdIQpDGjbE9x1mRRyCFyoTw0tXLEouJhYjru6enY2P68qEDSbgqFBywecrfkgm4tBKAYGNZkgn50DZgAACKe4tSkAEtApAAG6FvWB7ijA190ANcBl27YUc6uN5/ulvZUDoNPrY5zvKwGHZCY4uhTi4sYG63loo/k0cXHy6lPqjPNf4e9U4rOdMxPY5eXPVDD0gBHO9DbdeLmukf1YuHKrK9koYL05X/CD8dLq3aN9CQEyRFoviDj9DggAJ+RB+zaIDZ2mOZgXDWrgRUNh704ykjQ7Y5PhH3T9Zj7XSHcRSrZzCgJYp0UFzNJEpblyqarSd/ftk2mXMaid3h8STXXX6rabVi9mXLvbVdTHyjOLipfmydzjss0y6w6q5mp+cecgv8JZkp4cWU0cMRHDKSisPdpMW0tezpCKr3Q8N0nrwWYMiS9W5khpAAA=')
	#sd_upload_file('/tmp/aws-sjsu-key.pem', 'EwAwAq1DBAAUGCCXc8wU/zFu9QnLdZXy+YnElFkAAdyvyBb7dUPxcs+A1eORq0kZnQIgSUTNNRYRjw/qIiE7we3Wav687rdfgopEaXnhAvtLflwrpm7hucVvIyVgJx7ODJqrLEDPyyrnLpUE0HO2iQvDlF5DSwHw7a57xGEomEV81W0m8HsbynxtThpBNXnR6q9i1FD+tjSM7oyiPl/J9Ofm1nKOp6UtZs8qSkHRm1Bc4bFHsjLCCPy+/hsUnl4IocvVdy6FUf96NuK7//K2+vXkFEAagbi0OLQN+WtSOGhCmvAbb942dQCD4ohBjp67XCydwH5TOnw46/EuEkke5zD3k5b1CfN0/+BBT8xidUx6uaSVZGyI+Tn2EarlBhADZgAACBYCLb9tTOrAAAHDfT3nq5PVIetO7cOoGCd+jXTM0qlcpvmUECG84a4veXM+95BExZviaVFbeTv4ASyfh9MI/iD5pAWwVhy9M0nbcGa27bP3rgtpg2Wc2ussBATPEQ8w9UxZrQdiE0WGhHwIdLnHSdYXzfYl8jGGDtJ/FbXqW1FXgjzV7PUginbj9GrAbwYda4CszDg98DRKlJWW3nBd8l6ycbdcx2xH/WnSu4v6M1jgRrd55sLUj4FwELXrVOgqVl0zE3JRchvyWFuVD+doFWwIPW4lWPaBsqJZ1Ax4rQ5QuVzBK8wSqFBKSP7zx+/1RmMF3zT6TX14AugMmTITSyS4FTctQ9nfQ/eOAAA=')