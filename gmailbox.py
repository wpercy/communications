import email
import getpass
import imaplib
import datetime

def gmail_imap_login(email, password=None):
    """ Log in to the gmail imap server. Returns None if something went wrong in
        imaplib otherwise it will return the mailbox object or error out if the
        error isn't in imaplib.

        If you're uncomfortable saving your password in a file, you can leave
        that parameter empty and you'll be asked for your password via the
        command line (thank you getpass)
    """
    try:
        M = imaplib.IMAP4_SSL('imap.gmail.com')
    except imaplib.IMAP4.error:
        print "unable to connect to imap server"
        return

    try:
        M.login(email, password or getpass.getpass())

        print "logged in"
        return M

    except imaplib.IMAP4.error:
        print "Something went wrong"
        return



def process_mailbox(M):
    messages = []

    rv, data = M.search(None, "ALL")
    if rv != 'OK':
        print "No messages found!"
        return

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print "ERROR getting message: ", num
            continue

        msg = email.message_from_string(data[0][1])

        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            msg_date =  local_date.strftime("%a, %d %b %Y %H:%M:%S")
        else:
            msg_date = msg['Date']

        message = dict(
                        subject=msg['Subject'],
                        sender_name=' '.join(msg['From'].split()[:-1]).strip('"'),
                        email=msg['From'].split()[-1].strip("<>"),
                        date=msg_date
                    )

        # print 'Message %s: %s' % (num, msg['Subject'])
        # print 'From', msg['From'].split()[-1].strip("<>")
        # print 'Raw Date:', msg['Date']

        # print message
        messages.append(message)

    return messages

