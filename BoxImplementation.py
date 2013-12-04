from flask import Flask, render_template
from flask import request,redirect,Response,url_for
from urllib2 import urlopen, URLError, HTTPError,Request
#from werkzeug import 
import CloudUtils
import json
import logging
import urllib
import urllib2
import requests
import os
import subprocess
import Encrypt
from CloudUtils import LOG
from CloudUtils import splitsvilla
from CloudUtils import marriage
from Encrypt import encrypt_file
from Encrypt import getHashKey
from subprocess import call
from subprocess import check_call
from OpenSSL import SSL
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('./certs2/server.key')
context.use_certificate_file('./certs2/server.crt')



app = Flask(__name__)

file_handler = logging.FileHandler("logs", mode='a', encoding=None, delay=False)
file_handler.setLevel(logging.WARNING)
app.logger.addHandler(file_handler)
client_id = 'nfgvqw2i0twl9fxirk0vdcn5ymcpe8qg'
client_secret = 'nTruuZXxpqVoOKoMrbc0r4hmvwtHxIL7'
access_token = ''
refresh_token = ''
expires_in = ''
baseBoxURL = 'https://api.box.com'
UPLOAD_FOLDER = '/Users/snehakulkarni/Documents/CMPE273/myproject/final_demo/Box/useruploads'
DOWNLOAD_FOLDER = '/Users/snehakulkarni/Documents/CMPE273/myproject/final_demo/Box/userdownloads'

@app.route("/")
def hello():
	LOG('User flow initiated')
	return render_template('boxAuth.html')

#Give an option to the user to login to BOX
@app.route('/useBox/', methods=['GET'])
def useBox():
	return render_template('boxAuth.html')


@app.route('/boxResponse/')
def boxResponse():
	code  = request.args.get('code','')
	state = request.args.get('state','')
	error = request.args.get('error','')
	global access_token
	global refresh_token

	if error:
		return "code : "+code+"state : "+state+"error : "+error
	else:
		url = 'https://www.box.com/api/oauth2/token'
		values = {  'grant_type' : 'authorization_code',
					'code' : code,
					'client_id' : client_id,
					'client_secret' : client_secret }
		data = urllib.urlencode(values)
		req = urllib2.Request(url, data)
		#Send the request to BOX
		response = urllib2.urlopen(req)
		#this is how to get the httpresponse, for future use.
		response.getcode()
		#jsonResponse = response.read()
		#Parse the authentication response returned by BOX
		tokens = json.load(response)
		access_token = tokens['access_token']
		refresh_token = tokens['refresh_token']
		# We also need to set a timer for the expiry time and refresh the auth token every one hour.
		expires_in = tokens['expires_in']
		return getFolderList(0)


#This is called when the user clicks the file download link.		
@app.route('/boxDownload')
def boxDownload():
	fileID = request.args.get('fileID','')
	url = baseBoxURL + '/2.0/files/'+ fileID +'/content'
	req = urllib2.Request(url)
	req.add_header('Authorization','Bearer ' + access_token)
	response = urllib2.urlopen(req)
	redirectLocation = ''
	fileData = response.read()
	LOG(response.info())
	LOG(fileData)
	if response.code == 302 :
		redirectLocation = response.info()['location']
		req = urllib2.Request(redirectLocation)
		response = urllib2.open(req)	
		return Response(response.read(),mimetype="text/plain",headers={"Content-Disposition":
			"attachment;filename=test.txt"})
	else:
		fileInfo = response.info()['Content-Disposition'];
		mimeType = response.info()['Content-Type'];
		return Response(fileData,mimetype=mimeType,headers={"Content-Disposition":fileInfo})

# Accepts the access_token and returns the list of folders    
def getFolderList(folderID):
	#Create a request to access the users folders. The root folder is denoted by 0
	global access_token
	LOG('access_token----------'+access_token)
	url = baseBoxURL + '/2.0/folders/'+str(folderID)
	req = urllib2.Request(url)
	req.add_header('Authorization','Bearer ' + access_token)
	#req = requests.get(url,headers=header)
	response = urllib2.urlopen(req)
	responseJson = json.load(response)
	LOG('ending getFolderList function')
	return displayLinks(responseJson)

#Constructs the HTML file for downloading the document. 
def displayLinks(responseJson):
	totalItems = responseJson['item_collection']['total_count']
	folderID = responseJson['id']
	folderName = responseJson['name']
	parentFolder = responseJson['path_collection']['entries']
	responseMsg = '<html><head>'+addJavaScript()+'</head><body>'
	if folderID == '0' : 
		responseMsg += 'There are '+str(totalItems)+' items in your root folder.' + "<br><br>"
		responseMsg += genrateBreadCrum(parentFolder,folderName)
	else:
		responseMsg += 'There are '+str(totalItems)+' items in your <b>'+ folderName + '</b> folder.' + "<br><br>"
		responseMsg += 	genrateBreadCrum(parentFolder,folderName)
	allEntries = responseJson['item_collection']['entries']
	for entries in allEntries:
		if entries['type'] == 'file' :
			responseMsg += "[-] <a href=/boxDownload?fileID=" + entries['id'] + ">" + entries['name'] + "</a><br>"
		else: 
			responseMsg += "[<a href=/openFolder?fileID=" + entries['id'] + ">+</a>] " + entries['name'] + "<br>"
	responseMsg += '<br><br>' + addFileUploadForm(folderID) + '</body></html>'

	LOG('ending display links : ' + responseMsg)
	return responseMsg

#Adding javascript for uploading the file via AJAX.
def addJavaScript():
	script = '<script>'
	script += 'function uploadFile() { alert("file uploaded"); }'
	script += '</script>'
	return script


#Adding html form for file upload
def addFileUploadForm(folderID):
	formString = '<form method="post" enctype="multipart/form-data"  action="/uploadFile">\
	<input type="file" name="file" id="file" multiple />\
	<input type="hidden" name="folderID" id="folderID" value="'+ folderID +'" />\
	<input type="checkbox" name="Encrypt" value="Encrypt">Encrypt Files</input>\
	<input type="checkbox" name="Split" value="Split">Split Files</input>\
	<br> <br> Enter encryption password: <input type="text" name="Password" id="Password"/>\
	<button type="submit" id="btn">Upload Files!</button>\
	</form> '
	return formString

@app.route('/openFolder')
def openFolder():
	fileID = request.args.get('fileID','')
	return getFolderList(fileID)

def genrateBreadCrum(parentTree,currentFolder):
	# For the root folder there is no parent
	if not parentTree:
		return '[-Root-][<a id="myLink" href="#" onclick="uploadFile();">Upload</a>]<br><br>'              
	#Traverse the parent tree and generate the bread crum 
	responseMsg = '  [-'
	for entries in parentTree:
		if entries['name'] == 'All Files':
			name = 'Root'
			responseMsg +='<a href=/openFolder?fileID=' + entries['id'] + '>'+name+'-</a>'
		else:
			name = entries['name']
			responseMsg +=' <a href=/openFolder?fileID=' + entries['id'] + '>'+name+'-</a>'	
	#responseMsg = responseMsg.rstrip('-</a>')
	responseMsg += currentFolder + '-][<a id="myLink" href="#" onclick="uploadFile();">Upload</a>]<br><br>'
	return responseMsg

#Accept a user uploaded file and push it to the users box folder. 
@app.route('/uploadFile', methods=['GET', 'POST'])
def upload_file():
	global UPLOAD_FOLDER
	if request.method == 'POST':
		folderID = None
		doEncrypt = None
		doSplit = None
		password = None
		LOG('in uploadFile Post Method')
		try :
			file = request.files['file']
		except KeyError, e :
			LOG('No File')
			return getErrorPage()
		folderID = request.form['folderID']
		try :
			doEncrypt = request.form['Encrypt']
		except KeyError, e :
			LOG('No Encrypt')
		try :
			doSplit = request.form['Split']
		except KeyError, e :
			LOG('No Split')
		if doEncrypt:
			try:
				password = request.form['Password']
			except KeyError, e :
				LOG('No Password')
		LOG('in uploadFile: folderID:' + folderID + ' Encrypt:' + str(doEncrypt) +' Split:' + str(doSplit))
		filename = file.filename
		#This saves the file to the defined upload folder.
		file.save(os.path.join(UPLOAD_FOLDER, filename))
		#Depending on what sessions the user has signed in (eg dropbox or box) 
		if doSplit == 'Split':
			SplitFileList = splitsvilla(UPLOAD_FOLDER,filename,2)
		else:
			SplitFileList = None
		if doEncrypt == 'Encrypt':
			key = getHashKey(password)
			if SplitFileList:
				for fileItem in SplitFileList:
					uploadToBox(os.path.join(UPLOAD_FOLDER, encrypt_file(os.path.join(UPLOAD_FOLDER,fileItem),key)),folderID)
			else:
				uploadToBox(os.path.join(UPLOAD_FOLDER,encrypt_file(os.path.join(UPLOAD_FOLDER,filename),key)),folderID)
		if doSplit == 'Split':
			if not doEncrypt:
				for fileItem in SplitFileList:
					uploadToBox(os.path.join(UPLOAD_FOLDER,fileItem),folderID)
		if not doSplit and not doEncrypt:
			uploadToBox(os.path.join(UPLOAD_FOLDER,filename,folderID))
		return getFolderList(folderID)
	return getErrorPage()

#Uplode the users file to box.
#Later : Implement a way to split files and merge files.
#Give a separate download list for files that have been split. 
def uploadToBox(filePath,folderID):
	global access_token
	global baseBoxURL
	url = baseBoxURL + '/2.0/files/content'
	#authHeader = 'Authorization: Bearer '+ access_token
	#fileURL = 'filename=@'+filePath
	#folderURL = 'folder_id='+folderID
	#Tried to upload files using curl. Could not do it. However the requests object works just fine.
	#req = urllib2.Request(url)
	#req.add_header('Authorization','Bearer ' + access_token)
	#proc = subprocess.Popen(["curl", url, "-H", authHeader, "-F", fileURL, "-F", folderURL])
	#(out, err) = proc.communicate()
	#ret = check_call(['C:\\Security\\Tools\\curl-7.33.0-win64-ssl-sspicurl\\curl.exe', '--insecure' , '-H', authHeader, '-F', fileURL, '-F', folderURL , url], shell = True)
	headers = {'Authorization': ' Bearer ' + access_token}
	files = {'file': open(filePath, 'rb') , 'folder_id' : ('' , folderID)}
	ret = requests.post(url, headers=headers, files=files, verify=False)
	if ret.status_code == 201:
		#refresh the file container page
		return 1
	else:
		return -1


#Upon any error show this error page. 
def getErrorPage(folderID):
	global access_token
	#Disabling the session.
	access_token = '';
	errorPage = '<html><h1>oops...you reached the error page.</h1>\
	<body>Your Box session is refreshed. Please sign in again.\
	<a href="https://www.box.com/api/oauth2/authorize?response_type=code&client_id=s6ggdcvbwg7yswvyaxstqc0eu2bnnuzb&state=authenticated"> Go to box</a></body>\
	</html>'

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True, port=8101, ssl_context=context) 


#This is not working. Figure out why. However the alternative code in function boxdownload is working. Hence ignore this. 
class SmartRedirectHandler(urllib2.HTTPRedirectHandler):

	def http_error_302(self, req, fp, code, msg, headers):
		result = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
		result.status = code
		print 'in the 302 handler'
		return result  

	def http_error_301(self, req, fp, code, msg, headers):
		result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)
		result.status = code
		return result		