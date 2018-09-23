import httplib2, base64
from email.MIMEText import MIMEText
from apiclient.discovery import build
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
import logging

class GoogleError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(ValidationError, self).__init__(message)

class Google:
    def __init__(self,scopes=None):
        # Need to have Drive API and Gmail API enabled
        if scopes is None:
            scopes = ['https://spreadsheets.google.com/feeds',            # Read google docs
                      'https://www.googleapis.com/auth/gmail.readonly',
                      'https://www.googleapis.com/auth/gmail.compose',    # Send emails
                      'https://www.googleapis.com/auth/userinfo.email']   # Get users email address
        self.scopes = scopes

        self.authenticated = False
        self.user_info = None
        self.credentials = None

    def authenticate(self):
        flow = flow_from_clientsecrets('client_secret.json', scope=' '.join(self.scopes))
        storage = Storage('creds.data')
        self.credentials = storage.get()
        # If no credentials are found or the credentials are invalid due to
        # expiration, new credentials need to be obtained from the authorization
        # server. The oauth2client.tools.run_flow() function attempts to open an
        # authorization server page in your default web browser. The server
        # asks the user to grant your application access to the user's data.
        # If the user grants access, the run_flow() function returns new credentials.
        # The new credentials are also stored in the supplied Storage object,
        # which updates the credentials.dat file.
        if self.credentials is None or self.credentials.invalid:
            flow.params['access_type'] = 'offline'
            flow.params['approval_prompt'] = 'force'  # Force oauth server to return refresh token
            self.credentials = tools.run_flow(flow,storage,tools.argparser.parse_args())
            logging.debug('Ran flow')
        if self.credentials is not None and self.credentials.access_token_expired:
            self.credentials.refresh(httplib2.Http())
            logging.debug('Refreshed token')

        self.user_info = self._get_user_info()
        self.authenticated = True
        logging.info('%s (%s) authenticated.'%(self.user_info['name'],self.user_info['email']))

    def _get_user_info(self):
        """Send a request to the UserInfo API to retrieve the user's information.

        Args:
          credentials: oauth2client.client.OAuth2Credentials instance to authorize the
                     request.
        Returns:
          User information as a dict.
        """
        user_info_service = build(serviceName='oauth2', version='v2', http=self.credentials.authorize(httplib2.Http()),cache_discovery=False)
        user_info = user_info_service.userinfo().get().execute()
        if user_info and user_info.get('id'):
            return user_info
        else:
            raise GoogleError('No user ID.')

    def get_spreadsheet(self,fileName=None,fileId=None,fileURL=None):
        import gspread
        gc = gspread.authorize(self.credentials)
        if fileName is not None:
            sh = gc.open(fileName)
        elif fileId is not None:
            sh = gc.open_by_key(fileId)
        elif fileURL is not None:
            sh = gc.open_by_url(fileURL)
        return sh

    def email(self,to,msg,subject,cc=None):
        # Send mail from current user's gmail default address (can't seem to change that)
        http = self.credentials.authorize(httplib2.Http())
        email_service = build(serviceName='gmail', version='v1', http=http,cache_discovery=False)
        if type(to)==list or type(to)==tuple:
            to = ', '.join(to)
        message = MIMEText(msg)
        message['to'] = to
        if cc:
            if type(cc)==list or type(cc)==tuple:
                cc = ', '.join(cc)
            message['cc'] = cc
        message['subject'] = subject
        message = {'raw':base64.urlsafe_b64encode(message.as_string())}
        message = (email_service.users().messages().send(userId="me", body=message).execute())
        return message

if __name__ == '__main__':
    g = Google()
    g.authenticate()
    print 'Google() authenticated in instance "g"'
