#! /usr/bin/python

import db_util
import json
import requests
from server import get_provider
from server import NUM_PROVIDERS
import box
import skydrive
import dropbox
import google_drive

if __name__ == '__main__':
    email = "gaya.0408@gmail.com"
    for i in range(NUM_PROVIDERS):
        if i == 2: # no refresh token for dropbox
            continue
        get_provider(i).refresh_token(email)
        print "refreshed", get_provider(i).label,"for",email