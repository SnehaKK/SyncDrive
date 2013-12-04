#!/usr/bin/python

# A python script connecting to a MongoDB given a MongoDB Connection URI.

import sys
import pymongo
import hashlib
import json
import os
import boto.ses

### Standard URI format: mongodb://[dbuser:dbpassword@]host:port/dbname
client = None

def db_open():
	global client
	MONGODB_URI = 'mongodb://synergy:synergy@ds049558.mongolab.com:49558/synergy' 
	client = pymongo.MongoClient(MONGODB_URI)
	db = client.get_default_database()
	return db['users']	

def db_close():
	global client
	client.close()

def verify_email(email):
    script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    aws = json.load(open(os.path.join(script_dir, "aws-keys.txt"),"r"))
    conn = boto.ses.connect_to_region('us-east-1', aws_access_key_id=aws['access'], aws_secret_access_key=aws['secret'])
    conn.verify_email_address(email)

def send_welcome_email(email):
    script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    aws = json.load(open(os.path.join(script_dir, "aws-keys.txt"),"r"))
    conn = boto.ses.connect_to_region('us-east-1', aws_access_key_id=aws['access'], aws_secret_access_key=aws['secret'])
    conn.send_email('SyncDrive <synergy.sjsu@gmail.com>', 'Welcome to SyncDrive!', 'Welcome to SyncDrive, a one stop shop to manage all your cloud files. You can login to www.syncdrive.com with your registered password to manage all your cloud files in SyncDrive.', [email])

def user_signup(email,password):
    users = db_open()
    query = users.find_one({'email': email})
    if(query == None):
        send_welcome_email(email)
        users.insert({ "email": email ,"password" : password })
    else:
        print "Record with Email ID Already present (%s) "% (query["email"])
    db_close()

def valid_user(email,password):
	users = db_open()
	query = users.find_one({'email': email})
	if query and password == query.get('password',None):
		return True
	else:
		return False


def get_key(label):
	script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
	return json.load(open(os.path.join(script_dir, "keys.txt"),"r"))[label]
	
def save_token(label,key,value,email):
	users = db_open()
	query = users.find_one({'email': email})
	if not query.has_key(label):
		query[label] = { key : value }
	else:
		query[label][key] = value
	users.save(query)
	db_close()

def fetch_token(email,label,key = "access_token"):
	users = db_open()
	query = users.find_one({'email': email})
	result = query.get(label,{}).get(key,None)
	db_close()
	return result if (result != None) else None

def has_token(email, label,key):
	return bool(fetch_token(email,label,key))

def email_exists(email):
	users = db_open()
	query = users.find_one({'email': email})
	db_close()
	return bool(query)

if __name__ == '__main__':
	#get_drive_details("google_drive")
	#user_signup('sujatha67@gmail.com','suji')
	#save_token('google_drive','access_token','hello','sujatha67@gmail.com')
	#save_token('google_drive','refresh_token','world','sujatha67@gmail.com')
	#fetch_token('sujatha67@gmail.com','google_drive','access_token')
    #main(sys.argv[1:])
    print email_exists('gaya.0408@gmail.com')
    print email_exists('vigneshv@gadg')
