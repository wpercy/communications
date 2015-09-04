#! /usr/bin/python
import boto3

def get_recipients_from_csv(filename):
    with open(filename, 'rb') as f:
        reader = csv.DictReader(f)
        return [ r for r in reader ]

def send_mass_email(**kwargs):
    # ses client params -- if they exist, pass directly to client constructor
    if 'aws_access_key_id' in kwargs:
        aws_key = kwargs['aws_access_key_id']
        secret_key = kwargs['aws_secret_access_key']
        region = kwargs['region_name']
        client = boto3.client(
                              'ses',
                              aws_access_key_id=aws_key,
                              aws_secret_access_key=secret_key,
                              region_name=region
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

    if 'csv' in kwargs:
        recipient_data = get_recipients_from_csv(kwargs['csv'])
    else:
        recipient_data = kwargs['recipient_data']

    # send a unique email to each recipient because things will change per recipient
    for r in recipient_data:
        response = client.send_email(
                        Source=sender,
                        Destination={
                            'ToAddresses':[ r['Email'] ] # again, just the one recipient
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
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            # log the error somewhere

def send_email(**kwargs):


