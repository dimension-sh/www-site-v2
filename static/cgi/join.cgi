#!/usr/bin/env python3

import cgi
import ipaddress
import os
import pwd
import re
import smtplib
import sys
from datetime import datetime
from email.message import EmailMessage

from dns import resolver
from jinja2 import Template
from mkuser.ssh import validate_sshkey

DATA_FOLDER = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data'))
REQUEST_DESTINATION_EMAIL = 'signup@dimension.sh'


def validate_ip(ip: str):
    return True


def validate_ip_dnsbl(ip: str):
    """Validate a IP against DroneBL."""
    resolv = resolver.Resolver()

    # Check the IP address
    try:
        ipobj = ipaddress.ip_address(ip)
    except ValueError:
        return False

    # Generate the query
    if isinstance(ipobj, ipaddress.IPv4Address):
        query = ipobj.reverse_pointer.replace('.in-addr.arpa', '.dnsbl.dronebl.org.')
        query_type = 'A'
    elif isinstance(ipobj, ipaddress.IPv6Address):
        query = ipobj.reverse_pointer.replace('.ip6.arpa', '.dnsbl.dronebl.org.')
        query_type = 'AAAA'
    else:
        return False

    # Query
    try:
        resolv.query(query, query_type)
        return False
    except resolver.NXDOMAIN:
        return True
    return False


def file_to_list(filename: str):
    if os.path.exists(os.path.join(DATA_FOLDER, filename)):
        with open(os.path.join(DATA_FOLDER, filename), 'r') as fobj:
            return [line.strip() for line in fobj.readlines() if line.strip() != '']
    return []


def validate_username(username: str):
    """Validate the provided username that its valid and isn't in any restricted list."""
    if re.match("^[a-z][-a-z0-9]*$", username) is None:
        return 'Invalid username, Please try another one.'
    if username in file_to_list('banned_usernames.txt'):
        return 'Sorry, an error has occurred, please try again later.'
    if username in file_to_list('reserved_usernames.txt'):
        return 'This username is reserved, if you are the rightful owner of this username, then email {0} with your SSH key.'.format(REQUEST_DESTINATION_EMAIL)
    if username in [user.pw_name for user in pwd.getpwall()]:
        return 'This username is already took, please try another one.'
    return True


def validate_email(address: str):
    """Quickly validates a email address, nowhere near perfect, but good enough."""
    if address in file_to_list('banned_emails.txt'):
        return 'Sorry, an error has occurred, please try again later.'
    if re.match(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', address) is None:
        return 'Invalid email address provided.'
    return True


def error(msg: str):
    sys.stdout.write('Content-Type: text/html\n\n')
    with open(os.path.join(DATA_FOLDER, 'wiki_template.j2')) as fobj:
        template = Template(fobj.read())
    html = '<meta http-equiv="refresh" content="10; URL=\'http://dimension.sh/join/\'"/>\n<h1>JOIN</h1><p>An error was encountered:</p><p>{0}</p><p>Redirecting you back to the form...</p>\n'.format(msg)
    sys.stdout.write(template.render(html=html))


def main():
    # Get the form and extract the values
    form = cgi.FieldStorage()
    username = form.getvalue('username')
    email = form.getvalue('email')
    ssh_key = form.getvalue('ssh_key')
    why = form.getvalue('why')
    rules = form.getvalue('rules')

    # Validate all the things
    if not validate_ip(os.environ["REMOTE_ADDR"]):
        error('Sorry, an error has occurred, please try again later.')

    if not validate_ip_dnsbl(os.environ["REMOTE_ADDR"]):
        error('Sorry, Your IP appears on DroneBL DNSBL - If this is an error, mail {0}'.format(REQUEST_DESTINATION_EMAIL))
        return

    if rules != '1':
        error('You have to accept the rules.')
        return

    if not username or not email or not ssh_key or not why:
        error('All fields must be provided.')
        return

    ret = validate_username(username)
    if ret is not True:
        error(str(ret))
        return

    ret = validate_sshkey(ssh_key)
    if ret is not True:
        error('{0} - Please check your SSH Key'.format(ret))
        return

    ret = validate_email(email)
    if ret is not True:
        error(ret)
        return

    try:
        if pwd.getpwnam(username):
            error('Username {0} is already took'.format(username))
            return
    except KeyError:
        pass

    # Build Email
    with open(os.path.join(DATA_FOLDER, 'email_template.j2'), 'r') as fobj:
        template = Template(fobj.read())
    content_values = template.render({
        'date': datetime.now(),
        'username': username,
        'email': email,
        'ssh_key': ssh_key,
        'why': why,
        'ip': os.environ["REMOTE_ADDR"],
    })

    msg = EmailMessage()
    msg.set_content(content_values)
    msg['Subject'] = '[DIMENSION.SH] New User Request - {0}'.format(username)
    msg['From'] = 'nobody@dimension.sh'
    msg['To'] = REQUEST_DESTINATION_EMAIL

    # Send email
    smtp_conn = smtplib.SMTP('localhost')
    smtp_conn.send_message(msg)
    smtp_conn.quit()

    sys.stdout.write('Location: http://dimension.sh/join/submitted/\n\n')


if __name__ == '__main__':
    main()
