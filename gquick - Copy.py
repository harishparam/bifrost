from __future__ import print_function
import httplib2
import os
import sys
import base64
import re

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

#TODO:
#CLONE WORKSPACE
#OPEN LINKS WITH USER AGENT HEADERS
#OPEN LINKS IN EMAIL

#
# http://stackoverflow.com/questions/31967587/python-extract-the-body-from-a-mail-in-plain-text
# http://stackoverflow.com/questions/3302946/how-to-base64-url-decode-in-python


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
      print('Labels:')
      for label in labels:
        print(label['name'])


if __name__ == '__main__':
    #main()
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    print('Listing Emails from hparameswaran.demo@marketo.com...')

    #equery = 'from:hparameswaran.demo@marketo.com after:2016/06/21'
    #equery = 'from:hparameswaran.demo@marketo.com is:unread'
    equery = 'from:admin@mktodemoaccount345.com is:unread'
    messageList = service.users().messages().list(q=equery, userId='me').execute()
    print('%s Emails Found' % str(messageList['resultSizeEstimate']))
    
    if 'messages' not in messageList:
        sys.exit()
    messages = messageList['messages']
    pagecount = 1
    while 'nextPageToken' in messageList:
        pagecount+=1
        print('Getting page %s of results...' % str(pagecount))
        npt = messageList['nextPageToken']
        messageList = service.users().messages().list(q=equery,
                                                      userId='me', 
                                                      pageToken=npt).execute()
        print('%s Emails Found' % str(messageList['resultSizeEstimate']))
        if 'messages' in messageList:
            messages.extend(messageList['messages'])

    restrw = '.*(<img.*?trk\?t=.*?/>).*'
    progw = re.compile(restrw, re.DOTALL)
    tlinks = []

    print('Retrieving message bodies...')
    for message in messages:
        mid = message['id']
        #print('Getting: %s' % mid)
        emailraw = service.users().messages().get(userId='me', id=mid, format='raw').execute()
        body = base64.urlsafe_b64decode(emailraw['raw'].encode('ASCII')).decode('utf-8')
        matches = progw.match(body)
        if matches:
            tlink = matches.group(1).split('"')[1].replace('=\r\n','').replace('=3D','=')
            tlinks.append(tlink)

        #print(link)
    h = httplib2.Http()
    ipad = 'Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) CriOS/30.0.1599.12 Mobile/11A465 Safari/8536.25 (3B92C18B-D9DE-4CB7-A02A-22FD2AF17C8F)'
    win7 = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_7; en-us) AppleWebKit/533.4 (KHTML, like Gecko) Version/4.1 Safari/533.4'
    
    print('%s links found, opening all.' % str(len(tlinks)))
    f = open('links.txt', 'w+')
    for link in tlinks:
        f.write(link+os.linesep)
        resp, content = h.request(link, "GET", headers={'User-Agent':win7} )
        print(resp['status'])
    f.close()

    #print('Opening one with a galaxy nexus')
    # h = httplib2.Http(".cache")
    # galnexus = 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19'
    # ipad = 'Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) CriOS/30.0.1599.12 Mobile/11A465 Safari/8536.25 (3B92C18B-D9DE-4CB7-A02A-22FD2AF17C8F)'
    # resp, content = h.request(tlinks[len(tlinks)-2], "GET", headers={'User-Agent':ipad} )
    # print(resp['status'])
    #print(content)

    # testid = messageList['messages'][0]['id']
    # print('Testing: %s' % testid)
    # test = service.users().messages().get(userId='me', id=testid, format='raw').execute()
    # msg_str = base64.urlsafe_b64decode(test['raw'].encode('ASCII')).decode('utf-8')
    # matches = progw.match(msg_str)
    # link = matches.group(1).split('"')[1].replace('=\r\n','')
    # print(link)