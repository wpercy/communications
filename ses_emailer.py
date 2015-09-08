#! /usr/bin/python
import boto3
import datetime

def get_recipients_from_csv(filename):
    with open(filename, 'rb') as f:
        reader = csv.DictReader(f)
        return [ r for r in reader ]

def send_mass_email(**kwargs):
    # ses client params -- if they exist, pass directly to client constructor
    if 'aws_access_key_id' in kwargs:
        client = boto3.client(
                              'ses',
                              aws_access_key_id=kwargs['aws_access_key_id'],
                              aws_secret_access_key=kwargs['aws_secret_access_key'],
                              region_name=kwargs['region_name']
                            )
    # else, we're getting them from our aws config on the local machine
    else:
        client = boto3.client('ses')

    # email data
    sender = kwargs['sender']
    subject = kwargs['subject']
    # can contain tokens for replacement like this: {token_name}
    # 'token_name' must be a key in the recipient dicts below (r)
    html = kwargs['html_text']

    # one-liners are fun -- if we have a filename, get recipients from there, else from kwargs
    recipient_data = get_recipients_from_csv(kwargs['csv']) if 'csv' in kwargs else kwargs['recipient_data']

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


