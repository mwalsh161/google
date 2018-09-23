import Google
import httplib2, base64, email, re, datetime
from pyquery import PyQuery as pq
from apiclient import errors
from apiclient.discovery import build

def GetMessage(service, msg_id):
  """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
  try:
    message = service.users().messages().get(userId='me', id=msg_id).execute()
    return message
  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def GetMimeMessage(service, msg_id):
  """Get a Message and use it to create a MIME Message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A MIME Message, consisting of data from Message.
  """
  try:
    message = service.users().messages().get(userId='me', id=msg_id,format='raw').execute()

    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

    mime_msg = email.message_from_string(msg_str)

    return mime_msg
  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def search(service,query):
    try:
        response = service.users().messages().list(userId='me',q=query).execute()
        messages = []
        if 'messages' in response:
              messages.extend(response['messages'])

        while 'nextPageToken' in response:
              page_token = response['nextPageToken']
              response = service.users().messages().list(userId=user_id, q=query,
                                                 pageToken=page_token).execute()
              messages.extend(response['messages'])


        return messages
    except errors.HttpError, error:
        print 'An error occurred: %s' % error

if __name__ == '__main__':
    query = 'to:iquise-associates@mit.edu [IQUISE] Vuletic, Vladan'

    g = Google.Google()
    g.authenticate()
    http = g.credentials.authorize(httplib2.Http())
    service = build(serviceName='gmail', version='v1', http=http,cache_discovery=False)
    messages = service.search(query)
    date = []
    title = []
    abstract = []

    exp = re.compile('^\\*(.*)\\*',re.M)
    for msg in messages:
        try:
            content = GetMimeMessage(service,msg['id'])
            print content['subject']
            content_plain = content.get_payload()[0].get_payload().replace('\r\n','\n')
            content_html = content.get_payload()[1].get_payload()
            m = exp.findall(content_plain)
            print '  Got %i matches.'%len(m)
            if len(m) != 2:
                continue
            title.append(m[0])
            abstract.append(re.sub(r'(\w)\n(\w)',r'\1 \2',content_plain.split('\n\n')[-1].strip()))
            amended = re.sub('\d+(st|nd|rd|th)', lambda m: m.group()[:-2].zfill(2),m[1])
            date.append(datetime.datetime.strptime(amended,'%A, %B %m, %Y'))
        except:
            continue
        # d = pq(content_html)
        # for el in d('font'):
        #     if '3D"6"' == el.get('size'):
        #         print '  Found title'
        #         title.append(el.text_content())
        #         exit()

    print ''
    print 'Date(s):\n  %s'%'\n  '.join([d.strftime('%x') for d in date])
    print 'Title(s):\n  %s'%'\n  '.join(title)
    print 'Abstract(s):\n  %s'%'\n  '.join(abstract)
