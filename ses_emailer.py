#! /usr/bin/python
import boto3

def get_recipients_from_csv(filename):
    with open(filename, 'rb') as f:
        reader = csv.DictReader(f)
        return [ r for r in reader ]

def send_mass_email(**kwargs):
    aws_key = kwargs['aws_access_key_id']
    secret_key = kwargs['aws_secret_access_key']
    region = kwargs['region_name']
    sender = kwargs['sender']
    subject = kwargs['subject']
    recipient_data = get_recipients_from_csv(kwargs['csv'])

    # basically token replacement 
    html = kwargs['html_text']

    client = boto3.client(
                          'ses',
                          aws_access_key_id=aws_key,
                          aws_secret_access_key=secret_key,
                          region_name=region
                        )

    # send a unique email to each recipient because things will change per recipient
    for r in recipients:
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
                                    'Data': html.format(**r['html_placeholders']),
                                    'Charset': 'UTF-8'
                                }
                            }
                        }
                    )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            # log the error somewhere

