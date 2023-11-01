from __future__ import print_function
import os.path
import json
import base64
import re
from requests_futures.sessions import FuturesSession
import aiohttp
import asyncio
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#Terminal colors class
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#Google OAuth scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

async def main():
    creds = None
    linkIndex = 0
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    #If no label_id file is found, returns an error
    if not os.path.exists('label_id'):
        print("No label_id file found. Please create a file called 'label_id' and paste the ID of the label you want to use.")
        exit()
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        session = FuturesSession()
        
        #Fetch all messages
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me').execute()
        messages = results.get('messages', [])

        #Get label id and name from file
        with open('label_id', 'r') as label_id_file:
            labelId = label_id_file.read().replace('\n', '')
        labelResults = service.users().labels().list(userId='me').execute()
        allLabels = labelResults.get('labels', [])
        labelName = ""
        for label in allLabels:
            if(label['id'] == labelId):
                labelName = label['name']
        if(labelName == ""):
            print("No label found with ID: " + labelId)
            exit()

        if not messages:
            print('No messages found.')
            return
        print("   _____                       _   _                        _                      _____                       _               ")
        print('  / ____|                     (_) | |       /\             | |                    |  __ \                     | |              ')
        print(' | |  __   _ __ ___     __ _   _  | |      /  \     _   _  | |_    ___    ______  | |__) |   ___    __ _    __| |   ___   _ __')
        print(" | | |_ | | '_ ` _ \   / _` | | | | |     / /\ \   | | | | | __|  / _ \  |______| |  _  /   / _ \  / _` |  / _` |  / _ \ | '__|")
        print(' | |__| | | | | | | | | (_| | | | | |    / ____ \  | |_| | | |_  | (_) |          | | \ \  |  __/ | (_| | | (_| | |  __/ | |   ')
        print('  \_____| |_| |_| |_|  \__,_| |_| |_|   /_/    \_\  \__,_|  \__|  \___/           |_|  \_\  \___|  \__,_|  \__,_|  \___| |_|   ')
        print('')

        print("Using label: " + labelName)
        print('Downloading ' + str(len(messages)) + ' most recent messages:')

        #filter out messages that have already been read
        allMessages = messages.copy()
        for message in messages[:]:
            messageContents = service.users().messages().get(userId='me', id=message['id']).execute()
            messageTags = messageContents['labelIds']
            if labelId in messageTags:
                messages.remove(message)
        print(str(len(messages))+  ' un-AutoRead messages found')

        #Allow user to select to use only unread or all messages
        proceed = input(bcolors.WARNING + 'Use only unread (U) or all (A) messages? ' + bcolors.ENDC)
        if(proceed == 'a' or proceed == 'A'):
            messages = allMessages
        print('')
        messageIndex = 1
        try:
            #Attempt to get the contents of the message
            for message in messages:
                messageContents = service.users().messages().get(userId='me', id=message['id']).execute()
                try:
                    messagePayload = base64.b64decode(messageContents['payload']['parts'][1]['body']['data'], '-_').decode(encoding='utf-8')
                except:
                    try:
                        messagePayload = base64.b64decode(messageContents['payload']['parts'][0]['body']['data'], '-_').decode(encoding='utf-8')
                    except:
                        messageHeaders = messageContents['payload']['headers']
                        fromEmail = ""
                        for header in messageHeaders:
                            if header['name'] == 'From':
                                fromEmail = header['value']
                        print(bcolors.FAIL + "Error reading message " + str(messageIndex) + " of " + str(len(messages)) + " from " + fromEmail + bcolors.ENDC)
                        print('')
                        messageIndex = messageIndex + 1
                        continue
                    
                #Get and output message headers
                messageHeaders = messageContents['payload']['headers']
                subject = ""
                fromEmail = ""
                date = ""
                for header in messageHeaders:
                    if header['name'] == 'Subject':
                        subject = header['value']
                    if header['name'] == 'From':
                        fromEmail = header['value']
                    if header['name'] == 'Date':
                        date = header['value']
                print(bcolors.OKGREEN + "Reading message " + str(messageIndex) + " of " + str(len(messages)) + ":" + bcolors.ENDC)
                print(" "*5 + "Subject: " + subject)
                print(" "*5 + "From: " + fromEmail)
                print(" "*5 + "Date: " + date)

                #Retrieve all image URLs from the email body
                linkPositions = [m.start() for m in re.finditer('src="', messagePayload)]
                links = []
                for linkPos in linkPositions:
                    start = linkPos + 5
                    end = messagePayload.find('"', start)
                    link = messagePayload[start:end]
                    links.append(link)

                #Download all images and print status to console
                print('')
                print(" "*5 + 'Downloading ' + str(len(links)) + ' Images:')
                async with aiohttp.ClientSession() as session:
                    for link in links:
                        payload = {}
                        headers = {}
                        try:
                            async with session.get(link) as resp:
                                if(resp.status == 200):
                                    await resp.read()
                                    if(len(link) > 97):
                                        print(" "*10 + "-" + link[0:97] + "..." + " "*20 + str(resp.content_length) + " bytes")
                                    else:  
                                        contentLengthPos = 120 - len(link)
                                        print(" "*10 + "-" + link + " "*(contentLengthPos) + str(resp.content_length) + " bytes")
                                else:
                                    if(len(link) > 97):
                                        print(bcolors.FAIL + " "*10 + "-" + link[0:97] + "..." + bcolors.ENDC)
                                    else:  
                                        print(bcolors.FAIL + " "*10 + "-" + link + bcolors.ENDC)
                                    linkIndex = linkIndex + 1
                        except KeyboardInterrupt:
                            print("Quitting...")
                            exit();
                        except aiohttp.client_exceptions.ClientConnectorSSLError:
                            print(bcolors.FAIL + " "*10 + "-SSL Error: " + link + bcolors.ENDC)
                            linkIndex = linkIndex + 1
                            continue

                #Tag completed emails with specified label
                tagJSON =  '{"addLabelIds":["' + labelId + '"]}'
                tagObject = json.loads(tagJSON)
                service.users().messages().modify(userId='me', id=message['id'], body=tagObject).execute()
                print("\n" + " "*5 + "Message tagged as '" + labelName + "")
                messageIndex = messageIndex + 1
                print('')
                print('')

        except KeyboardInterrupt:
            print("Quitting...")
            exit()

    except KeyboardInterrupt:
        print("Quitting...")
        exit()
    except EOFError:
        print("Quitting...")
        exit()

    except HttpError as error:
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Quitting...")
        exit()
