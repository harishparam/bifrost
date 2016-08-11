import json
from flask import Flask 
import httplib2
import base64
import email
import re
import requests

from apiclient import discovery, errors
from oauth2client import client
from oauth2client import tools
from flask.json import jsonify


app = Flask(__name__)


@app.route('/')
def index():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        gmail_service = discovery.build('gmail', 'v1', http_auth)
        threads = gmail_service.users().threads().list(userId='me').execute()
        return json.dumps(threads)


@app.route('/oauth2callback')
def oauth2callback():
    flow = client.flow_from_clientsecrets(
        'client_secret.json',
        scope='https://mail.google.com/',
        redirect_uri=flask.url_for('oauth2callback', _external=True)
    )
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        return flask.redirect(flask.url_for('openmail'))

@app.route('/getmail')
def getmail():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        gmail_service = discovery.build('gmail', 'v1', http_auth)
        query = 'is:inbox'
        """List all Messages of the user's mailbox matching the query.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        query: String used to filter messages returned.
        Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

        Returns:
        List of Messages that match the criteria of the query. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate ID to get the details of a Message.
        """
        try:
            response = gmail_service.users().messages().list(userId='me', q=query).execute()
            messages = []
            if 'messages' in response:
                print ('test %s' % response)
                messages.extend(response['messages'])
            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = gmail_service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
                messages.extend(response['messages'])

            #   return messages
            return jsonify({'data': messages}) 
        except errors.HttpError as error:
            print ('An error occurred: %s' % error)
@app.route('/openmail')
def openmail():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        gmail_service = discovery.build('gmail', 'v1', http_auth)
        query = 'from:hparameswaran.demo@marketo.com is:unread'

        """List all Messages of the user's mailbox matching the query.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        query: String used to filter messages returned.
        Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

        Returns:
        List of Messages that match the criteria of the query. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate ID to get the details of a Message.
        """
        try:
                messageList = gmail_service.users().messages().list(q=query, userId='me').execute()
                print('%s Emails Found' % str(messageList['resultSizeEstimate']))
     
                if 'messages' not in messageList:
                    sys.exit()
                messages = messageList['messages']
                pagecount = 1
                while 'nextPageToken' in messageList:
                    pagecount+=1
                    print('Getting page %s of results...' % str(pagecount))
                    npt = messageList['nextPageToken']
                    messageList = gmail_service.users().messages().list(q=query,
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
                    emailraw = gmail_service.users().messages().get(userId='me', id=mid, format='raw').execute()
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
                opencount = 1 
                for link in tlinks:
                    print(link)
                    #f.write(link+os.linesep)
                    h.request(link, "GET", headers={'User-Agent':ipad} )
                    
                    #--print(resp['status'])
                    print(opencount)
                    opencount+=1
                    
                return 'Task Complete'  

        except errors.HttpError as error:
            print ('An error occurred: %s' % error)        

if __name__ == '__main__':
    import uuid
    app.secret_key = str(uuid.uuid4())
    # app.debug = False
    app.run(debug=True)