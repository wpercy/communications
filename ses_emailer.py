#! /usr/bin/python
import boto3
import datetime

class ses_mailer:

    def __init__(self, credentials=None):
        if credentials:
            try:
                self.has_credentials = True
                self.aws_access_key_id = credentials['aws_access_key_id'],
                self.aws_secret_access_key = credentials['aws_secret_access_key']
            except KeyError:
                # if either of the access keys aren't there, use local aws config
                self.has_credentials = False

    def send_mass_email(self, **kwargs):
        # ses client params -- if they exist, pass directly to client constructor
        if self.has_credentials:
            client = boto3.client(
                                  'ses',
                                  aws_access_key_id=self.aws_access_key_id,
                                  aws_secret_access_key=self.aws_secret_access_key,
                                  region_name=kwargs['region_name']
                                )
        # else, we're getting them from our aws config on the local machine
        else:
            client = boto3.client('ses')

        # email data
        sender = kwargs['sender']
        subject = kwargs['subject']
        # html can contain tokens for replacement like this: {token_name}
        # 'token_name' must be a key in the recipient dicts below (r)
        html = kwargs['html_text']

        # one-liners are fun -- if we have a filename, get recipients from there, else from kwargs
        recipient_data = self.get_recipients_from_csv(kwargs['csv']) if 'csv' in kwargs else kwargs['recipient_data']

        sent_emails = []
        for r in recipient_data:
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
                                        'Data': html.format(**r),
                                        'Charset': 'UTF-8'
                                    }
                                }
                            }
                        )
            sent_emails.append(r)
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                # log the error somewhere
                pass

    # def send_email(**kwargs):

    @classmethod
    def get_recipients_from_csv(filename):
        with open(filename, 'rb') as f:
            reader = csv.DictReader(f)
            return [ r for r in reader ]


