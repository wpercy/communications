#! /usr/bin/python
import boto3

def get_recipients(filename):
    with open(filename, 'rb') as f:
        reader = csv.DictReader(f)
        return [ r for r in reader ]

def send_mass_email(**kwargs):
    aws_key = kwargs['aws_access_key_id']
    secret_key = kwargs['aws_secret_access_key']
    region = kwargs['region_name']
    sender = kwargs['sender']
    recipients = get_recipients(kwargs['csv_filename'])

    # basically token replacement 
    html_content = kwargs['html_text'] % tuple(kwargs['html_placeholders'])

    client = boto3.client(
                          'ses',
                          aws_access_key_id=aws_key,
                          aws_secret_access_key=secret_key,
                          region_name=region
                        )

    # send a unique email to each recipient because the name and url param will change every time
    for r in recipients:
        response = client.send_email(
                        Source=sender,
                        Destination={
                            'ToAddresses':[ r['Email'] ] # again, just the one recipient
                        },
                        Message={
                            'Subject': {
                                'Data': 'SUBJECT LINE'
                            },
                            'Body': {
                                'Html': {
                                    'Data': html_content,
                                    'Charset': 'UTF-8'
                                }
                            }
                        }
                    )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            # log the error somewhere

