#!/usr/bin/env python

import time
import requests
from requests.exceptions import ConnectionError
import urllib, urllib2
import json

CLIENT_ID = "<YOUR CLIENT ID>"
BASE_URL = "https://api.imageindxr.com"
API_PROCESS = "process"
API_RESULTS = "sync"
TEST_IMAGE_URL= "https://s3-us-west-2.amazonaws.com/imgincoming/54a76dfb1bc4e8.55642918.jpg"
MAX_API_TIMEOUT = 15    # seconds
IMAGE_IDENTIFIER = "test-image-id-1"    # unique id per image sent to API

def alert( message ):
    print( "Alert: {}".format( message ) )

def do_web_call( url ):
    try:
        response = requests.get( url, stream = True, timeout = MAX_API_TIMEOUT )
    except Exception as e:
        alert( "Error calling API URL: {}".format( e ) )
        return None

    return data

def send_image_GET( ):

    image_id = IMAGE_IDENTIFIER
    data =  {
        image_id : {
        "url" : TEST_IMAGE_URL
        },
    }

    # encode for GET
    new_data = json.dumps( data, encoding = 'ascii' )
    encoded_data = urllib.quote_plus( new_data.replace(" ", "") )

    url = "{}/{}?client-id={}&data={}".format( BASE_URL, API_PROCESS, CLIENT_ID, encoded_data )

    data = do_web_call( url )
    if data is None:
        raise Exception( 'API call failed' )

    if "error" in str( data ):
        # get the error string
        try:
            errstr = data[ 'error' ]
        except:
            errstrlist = [ data[ d ][ 'error' ] for i,d in enumerate( data ) if "error" in data[ d ] ]
            for error in errstrlist:
                alert( error )

        raise Exception( 'Error message returned' )

    return data[ image_id ][ 'process-id' ]

#https://api.imageindxr.com/sync?client-id=54a76e2bafb165.33320945
def get_response( process_id ):
    url = "{}/{}?client-id={}".format( BASE_URL, API_RESULTS, CLIENT_ID )

    # loop through until empty set or process_id matches
    while True:
        data = do_web_call( url )

        if len( data ) == 0:
            break

        try:
            if data[ IMAGE_IDENTIFIER ][ "process-id" ] == process_id:
                break
        except Exception:
            pass

        time.sleep( BETWEEN_CHECKS_DELAY )

    if "error" in str( data ):
        # get the error string
        try:
            errstr = data[ 'error' ]
        except:
            errstrlist = [ data[ d ][ 'error' ] for i,d in enumerate( data ) if "error" in data[ d ] ]
            if len( errstrlist ) > 0:
                errstr = errstrlist[ 0 ]    # HACK: Will ignore all but the 1st error

        raise Exception( 'Error message returned: {}'.format( errstr ) )

    retval = None
    if len( data ) > 0:
        try:
            retval = data[ IMAGE_IDENTIFIER ][ 'receipt-id' ]
        except:
            retval = data[ IMAGE_IDENTIFIER ]

    return retval


if __name__ == "__main__":

    try:
        process_id = send_image_GET()
    except Exception as e:
        errmsg = "Got exception while submitting image: {}".format( e )
        alert( errmsg )
    else:
        time.sleep( WAIT_BETWEEN_PROCESS_AND_RESULTS )

        receipt_id = None
        try:
            receipt_id = get_response( process_id )

        except Exception as e:
            errmsg = "Got exception while getting response: {}".format( e )
            alert( errmsg )

        if receipt_id == None:
            errmsg = "ERROR: No results returned for process_id {}".format( process_id )
            alert( errmsg )
        else:
            alert( "... Success!" )

