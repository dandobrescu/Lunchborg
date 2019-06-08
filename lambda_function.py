import boto3
import json
import logging
import os
import hmac
import hashlib
import urllib.parse as urlparse
import gspread
import datetime
from oauth2client.service_account import ServiceAccountCredentials
import food


logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3 = boto3.resource('s3')



def verify_slack_request(slack_signature=None, slack_request_timestamp=None, request_body=None):

    basestring = f"v0:{slack_request_timestamp}:{request_body}".encode('utf-8')


    slack_signing_secret = bytes(os.environ['SLACK_SIGNIN_SECRET'], 'utf-8')


    my_signature = 'v0=' + hmac.new(slack_signing_secret, basestring, hashlib.sha256).hexdigest()

    if hmac.compare_digest(my_signature, slack_signature):
        return True
    else:
        logger.warning(f"Verification failed. my_signature: {my_signature}")
        return False


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def help():
    return {
        "response_type": "ephemeral",
        "text": "How to use /lunchborg",
        "attachments":[
            {
                "text":"`/lunchborg menu` to see today's menu \n You can try variations like `/lunchborg menu yestarday|today|tomorrow`. \n \nFirst time only you should register your preferences:\n `/lunchborg settings name YOUR_NAME` \n ...and afterwards choose one of the following:\n`/lunchborg settings vegetarian` or `/lunchborg settings carnivore` \n\n `/lunchborg settings alert ON/OFF` will enable/disable daily alerts.\n\n You've already learned how to get help with `/lunchborg help`."
            }
        ]
        }

def set_name(user_id, name):
    object = s3.Object(os.environ['LUNCHBORG_BUCKET'], "{}/name".format(user_id))
    object.put(Body=name)
    return {
        "response_type": "ephemeral",
            "text": "Name setting succesfully saved",
        }

def read_name(user_id):
    object = s3.Object(os.environ['LUNCHBORG_BUCKET'], "{}/name".format(user_id))
    return object.get()['Body'].read().decode('utf-8')
    
def set_preference(user_id, preference):
    object = s3.Object(os.environ['LUNCHBORG_BUCKET'], "{}/preference".format(user_id))
    object.put(Body=preference)
    return {
        "response_type": "ephemeral",
            "text": "Food preference setting succesfully saved",
        }    


def set_alert(user_id, alert):
    object = s3.Object(os.environ['LUNCHBORG_BUCKET'], "{}/alert".format(user_id))
    object.put(Body=alert)
    return {
        "response_type": "ephemeral",
            "text": "Alert preference setting succesfully saved",
        }    


def read_preference(user_id):
    object = s3.Object(os.environ['LUNCHBORG_BUCKET'], "{}/preference".format(user_id))
    return object.get()['Body'].read().decode('utf-8')        


def show_menu(sheet,date):
    return sheet.get_menu(date)
    

def lambda_handler(event, context):
    print("Beaming received event")
    print(event)
    print("End event")

    try:
        slack_signature = event['headers']['X-Slack-Signature']
        slack_request_timestamp = event['headers']['X-Slack-Request-Timestamp']
        
        parsed = urlparse.urlparse(("?"+event['body']))
        
        # if not verify_slack_request(slack_signature, slack_request_timestamp, event['body']):
        #     logger.info('Bad request.')
        #     response = {
        #         "statusCode": 400,
        #         "body": ''
        #     }
        #     return response
        
        user_id = urlparse.parse_qs(parsed.query)['user_id'][0]
        command = urlparse.parse_qs(parsed.query)['text'][0].split(" ")
        response_url = urlparse.parse_qs(parsed.query)['response_url'][0]
        if (command[0] == 'help'):           
            return help()
        
        if command[0].lower() == 'settings':
            if command[1].lower() == 'name':
                del command[0]
                del command[0]
                return set_name(user_id," ".join(command))
                
        if command[0].lower() == 'settings':
            if command[1].lower() == 'vegetarian' or command[1].lower() == 'carnivore':
                del command[0]
                return set_preference(user_id,command[0])
          

        if command[0].lower() == 'settings':
            if command[1].lower() == 'alert':
                del command[0]
                del command[0]
                return set_alert(user_id,command[0])
                
        
        if command[0].lower() == 'alert_eat':
            return {
    "text": "*You are scheduled to eat today*",
    "attachments": [
        {
            "text": "Do you want to keep your choice?",
            "fallback": "You are unable to choose something",
            "callback_id": "wopr_game",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "game",
                    "text": "Yes, eat today",
                    "type": "button",
                    "style": "primary",
                    "value": "chess"
                },
                {
                    "name": "game",
                    "text": "Unsubcribe me!",
                    "type": "button",
                    "style": "danger",
                    "value": "maze"
                }                
            ]
        }
    ]
}

        
        if command[0].lower() == 'alert_skip':
            return {
    "text": "*You are NOT scheduled to eat today*",
    "attachments": [
        {
            "text": "Do you want to keep your choice?",
            "fallback": "You are unable to choose something",
            "callback_id": "wopr_game",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "game",
                    "text": "Yes, I won't eat today",
                    "type": "button",
                    "style": "danger",
                    "value": "chess"
                },
                {
                    "name": "game",
                    "text": "Subscribe me!",
                    "type": "button",
                    "style": "primary",
                    "value": "maze"
                }                
            ]
        }
    ]
}
        if command[0].lower() == 'menu' or command[0].lower() == 'subscribe' or command[0].lower() == 'unsubscribe':
            print("should show menu...yep")
            client = boto3.client('lambda')
            payload = {
                "user_id": user_id,
                "command": command,
                "user_name": read_name(user_id),
                "user_preference": read_preference(user_id),
                "response_url": response_url
            }
            
            client.invoke(FunctionName="lunchborg-worker",InvocationType='Event',Payload=json.dumps(payload))
            return {
                "response_type": "ephemeral",
                "text": "Working on it... ",
            }    
            

            #return show_menu(sheet,datetime.datetime.now())
                




        response = {
            "statusCode": 200,
            "body": 'hello'
        }
        return response

    except Exception as e:
        ''' Just a stub. Please make this better in real use :) '''
        logger.error(f"ERROR: {e}")
        response = {
            "statusCode": 200,
            "body": ''
        }
        return response
