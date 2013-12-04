#! /usr/bin/python

from flask import *

import json
import os
import requests
import urllib
import urllib2

import google_drive
import skydrive
import db_util
import dropbox
import box

NUM_PROVIDERS = 4
SECRET_KEY = 'synergy'
app = Flask(__name__)
app.config.from_object(__name__)
UPLOAD_DIR = '/tmp/syncdrive'

def get_provider(index):
	mapping = {
				0 : google_drive,
				1 : skydrive,
				2 : dropbox,
				3 : box
			  }
	return mapping[index]


@app.route('/')
def welcome_page():
    error = request.args.get('error', '')
    return render_template('welcome.html', error = error == 'true')

@app.route('/verify')
def verify_email():
    email = request.args.get('email', '')
    db_util.verify_email(urllib2.unquote(email))
    return "verification email sent. approve and then register."

@app.route('/sign_up')
def signup_page():
    return render_template('sign_up.html')

@app.route('/transfer.js')
def transfer_js():
    return render_template('transfer.js',
                           pane1 = session.get('pane1', None),
                           pane2 = session.get('pane2', None))

@app.route('/login', methods = ['POST', 'GET'])
def login_page():
    if request.method == "GET":
        return render_template('login.html', print_error = False)
    email = request.form['email']
    password = request.form['password']
    if not db_util.valid_user(email,password):
        return redirect("/?error=true")
    session["email"] = email
    return redirect('/transfer')
   
@app.route('/new_user',methods = ['POST'] )
def process_new_user():
	email = request.form['email']
	password = request.form['password']
	db_util.user_signup(email,password)
	session["email"] = email
	return redirect('/transfer')

@app.route('/check_email')
def check_email():
    email = request.args.get('email','')
    return str(db_util.email_exists(email)).lower()

@app.route('/callback_skydrive')
def callback_skydrive():
	key = db_util.get_key('skydrive')
	url = 'https://login.live.com/oauth20_token.srf'

	values = {
		'client_id' :key['client_id'] ,
		'redirect_uri' : key['redirect_uri'] ,
		'client_secret' : key['client_secret'] ,
		'grant_type' : 'authorization_code' ,
		'code' :request.args.get('code','')
	}
	
	response = requests.post(url,data = values).json()

	db_util.save_token('skydrive',"access_token",response['access_token'],session['email'])
	db_util.save_token('skydrive',"refresh_token",response['refresh_token'],session['email'])
	return redirect('/transfer')

@app.route('/callback_google')
def callback_google():
	key = db_util.get_key('google_drive')
	url = "https://accounts.google.com/o/oauth2/token"

	values = {
            'code':request.args.get('code'),
            'client_id': key['client_id'] ,
            'client_secret': key['client_secret'],
            'redirect_uri': key['redirect_uri'],
            'grant_type':'authorization_code'
    }

	response = requests.post(url,data = values).json()
	db_util.save_token('google_drive',"access_token",response['access_token'],session['email'])
	if(response.get('refresh_token',None) != None):
		 db_util.save_token('google_drive',"refresh_token",response['refresh_token'],session['email'])
	return redirect('/transfer')

@app.route('/callback_box')
def callback_box():
	key = db_util.get_key('box')
	url = "https://www.box.com/api/oauth2/token"

	values = {
            'code':request.args.get('code',None),
        	'client_id': key['client_id'] ,
        	'client_secret': key['client_secret'],	
            'grant_type':'authorization_code'
        }

	response = requests.post(url,data = values).json()

	db_util.save_token('box',"access_token",response['access_token'],session['email'])
	db_util.save_token('box',"refresh_token",response['refresh_token'],session['email'])
	return redirect('/transfer')

@app.route('/callback_dropbox')
def callback_dropbox():
	key = db_util.get_key('dropbox')
	url = "https://api.dropbox.com/1/oauth2/token"
	app_key = key['client_id'] 
	app_secret = key['client_secret']

	values = {
            'code':request.args.get('code'),
            'redirect_uri': key['redirect_uri'],
            'grant_type':'authorization_code'
    }

	response = requests.post(url,auth = (app_key,app_secret),data = values).json()
	db_util.save_token('dropbox',"access_token",response['access_token'],session['email'])
	return redirect('/transfer')

@app.route('/transfer')
def transfer_page():
	return render_template('transfer.html',
                           email = session['email'],
                           upload_prompt = request.args.get('upload', '') == 'success')

@app.route('/transfer_file')
def transfer_file():
	source_drive = get_provider(int(request.args.get('src', '0')))
	destination_drive = get_provider(int(request.args.get('dst', '1')))
	filename = source_drive.download_file(request.args.get('file_id', ''), session['email'])
	uploaded_file = destination_drive.upload_file(filename, session['email'])
	return render_template('list_files.html',
                           listFiles=[uploaded_file],
                           user=session['email'],
                           quota='100',
                           label=destination_drive.display_label,
                           pane=request.args.get('dst_pane','1'),
                           drive=request.args.get('dst','0'))

@app.route('/upload', methods = ['POST'])
def upload_file():
    file_to_upload = request.files['file']
    print "## drive %s" % request.form.get('drive', '0')
    drive = get_provider(int(request.form.get('drive', '0')))
    if file_to_upload:
        filename = os.path.join(UPLOAD_DIR, file_to_upload.filename)
        file_to_upload.save(filename)
        drive.upload_file(filename, session['email'])
        os.unlink(filename)
    return redirect('/transfer?upload=success')

@app.route('/list_files')
def list_files():
    drive = get_provider(int(request.args.get('drive','0')))
    session['pane%s' % request.args.get('pane','1')] = int(request.args.get('drive','0'))
    # check if access token already exists
    if db_util.has_token(session['email'], drive.label,'access_token'):
        files = drive.list_files(session['email'],request.args.get('folder',''))
        return render_template('list_files.html',
                                listFiles=files,
                                user=session['email'],
                                quota='100',
                                label=drive.display_label,
                                pane=request.args.get('pane','1'),
                                drive=request.args.get('drive','0'))
    else:
        return render_template('oauth.html',
                               label = drive.label,
                               display_label = drive.display_label,
                               oauth_url = drive.get_oauth_url())

def list_files1():
	token = session["token"]
	try:
		folder = request.args.get('folder')
	except KeyError:
		print "no folder variable"

	if(folder == None):
		pass
	else:
		raw_data = urllib2.urlopen("https://apis.live.net/v5.0/%s/files?access_token=%s" % (folder,token)).read()
	
	raw_data1 = urllib2.urlopen("https://apis.live.net/v5.0/me/skydrive/quota?access_token=%s" % token).read()
	quota = json.loads(raw_data1)
	quota_mb = sizeof_fmt(int(quota["available"]))
	#return render_template('page.html',response=response,quota=quota_mb)
	return render_template('list_files.html',listFiles=listFiles,user=response["data"][0]["from"]["name"],quota=quota_mb)

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
