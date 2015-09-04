#! /usr/bin/python
import boto3

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

    # one-liners are fun
    recipient_data = get_recipients_from_csv(kwargs['csv']) if 'csv' in kwargs else kwargs['recipient_data']

    format_string = False
    # if we get a key error with no args, it means it's dynamic content for each recipient
    try:
        html.format()
    except KeyError:
        format_string = True

    if format_string:
        # send a unique email to each recipient because things will change per recipient
        for r in recipient_data:
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
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                # log the error somewhere
    else:
        # EMAIL BLAST!!

# def send_email(**kwargs):


