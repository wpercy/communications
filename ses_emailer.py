#! /usr/bin/python
import csv
from boto3.session import Session
import datetime

class SES_mailer:
    def __init__(self, credentials=None):
        if credentials:
            try:
                self.has_credentials = True
                self.aws_access_key_id = credentials['aws_access_key_id']
                self.aws_secret_access_key = credentials['aws_secret_access_key']
            except KeyError:
                self.has_credentials = False # if neither access key is there, use local aws config
        else:
            self.has_credentials = False

    def send_mass_email(self, **kwargs):
        # ses client params -- if they exist, pass directly to client constructor
        if self.has_credentials:
            session = Session(
                            aws_access_key_id=self.aws_access_key_id,
                            aws_secret_access_key=self.aws_secret_access_key,
                            region_name=kwargs['region_name']
                            )
            client = session.client('ses')
        # else, we're getting them from our aws config on the local machine
        else:
            session = Session()
            client = session.client('ses')

        # email data
        sender = kwargs['sender']
        subject = kwargs['subject']
        # html can contain tokens for replacement like this: {token_name}
        # 'token_name' must be a key in the recipient dicts below (r)
        if kwargs['html_file']:
            with open(kwargs['html_file'], 'rb') as f:
                html = f.read()
        else:
            html = kwargs['html_text']

        # one-liners are fun -- if we have a filename, get recipients from there, else from kwargs
        recipient_data = self.get_recipients_from_csv(kwargs['csv']) if 'csv' in kwargs else kwargs['recipient_data']

        sent_emails = []
        bad_emails = []
        for r in recipient_data:
            html_content = html.format(**r)
            r['timestamp'] = datetime.datetime.now().__str__()
            response = client.send_email(
                            Source=sender,
                            Destination={
                                'ToAddresses':[ r['Email'] ]
                            },
                            Message={
                                'Subject': {
                                    'Data': subject
                                },
                                'Body': {
                                    'Html': {
                                        'Data': html_content
                                    }
                                }
                            }
                        )
            sent_emails.append(r)
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                bad_emails.append(r)

        if 'logfile' in kwargs:
            with open(kwargs['logfile'], 'wb') as f:
                fieldnames = [ k for k in sent_emails[0].keys()]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for s in sent_emails:
                    writer.writerow(s)

        return sent_emails

    def get_recipients_from_csv(self, filename):
        with open(filename, 'rb') as f:
            reader = csv.DictReader(f)
            return [ r for r in reader if r['UserID'] != '']


