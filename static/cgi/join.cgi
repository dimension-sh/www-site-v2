#!/usr/bin/env python3

import sys
import cgi
import re
import struct
import binascii
import base64
import pwd
import os.path
import smtplib
from email.message import EmailMessage
from datetime import datetime

from jinja2 import Template
import ipaddress
import dns.resolver

DATA_FOLDER = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data'))
REQUEST_DESTINATION_EMAIL = 'signup@dimension.sh'

VALID_SSH_KEYTYPES = [
    'sk-ecdsa-sha2-nistp256@openssh.com',
    'ecdsa-sha2-nistp256',
    'ecdsa-sha2-nistp384',
    'ecdsa-sha2-nistp521',
    'sk-ssh-ed25519@openssh.com',
    'ssh-ed25519',
]

def validate_ip_dnsbl(ip):
    """Validate a IP against DroneBL"""
    resolv = dns.resolver.Resolver()

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
    except dns.resolver.NXDOMAIN:
        pass
    return True


def validate_username(username):
    if re.match(r"^[a-z][-a-z0-9]*$", username) is None:
        return False
    if os.path.exists(os.path.join(DATA_FOLDER, 'banned_usernames.txt')):
        with open(os.path.join(DATA_FOLDER, 'banned_usernames.txt'), 'r') as fobj:
            if username in [x.strip() for x in fobj.readlines() if x.strip() != '']:
                return False
    return True


def validate_sshkey(keystring):
    """ Validates that SSH pubkey string is valid """
    # do we have 3 fields?
    fields = len(keystring.split(' '))
    if fields < 2:
        return 'SSH key has a incorrect number of fields (%d, expected 2)' % fields
    else:
        fsplit = keystring.split(' ')
        keytype = fsplit[0]
        pubkey = fsplit[1]

    if keytype == 'ssh-rsa':
        return 'Please generate a ED25519 key rather than a RSA key'

    # Check it is a valid type
    if not keytype in VALID_SSH_KEYTYPES:
        return 'SSH key is a invalid keytype'

    # Decode the key data from Base64
    try:
        data = base64.decodebytes(pubkey.encode())
    except binascii.Error:
        return 'Error decoding the SSH pubkey'

    # Get the length from the data
    try:
        str_len = struct.unpack('>I', data[:4])[0]
    except struct.error:
        return 'Error decoding SSH key length'

    # Keytype is encoded and must match
    if not data[4:4+str_len].decode('ascii') == keytype:
        return 'Embedded SSH keytype does not match declared keytype (%s vs %s)' % (data[4:4+str_len].decode('ascii'), keytype)
    return True


def validate_email(address):
    """ QUickly validates a email address, nowhere near perfect, but good enough """
    return re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", address) != None


def error(msg):
    sys.stdout.write('\n')
    sys.stdout.write('<meta http-equiv="refresh" content="3; URL=\'http://dimension.sh/join/\'"/>\n')
    sys.stdout.write('<p>An error was encountered: %s</p>\n' % msg)


def main():
    sys.stdout.write('Content-Type: text/html\n')

    # Get the form and extract the values
    form = cgi.FieldStorage()
    username = form.getvalue('username')
    email = form.getvalue('email')
    ssh_key = form.getvalue('ssh_key')
    why = form.getvalue('why')
    rules = form.getvalue('rules')

    # Validate all the things
    if not validate_ip_dnsbl(os.environ["REMOTE_ADDR"]):
        error('Sorry, Your IP no bueno.')
        return

    if rules != '1':
        error('You have to accept the rules.')
        return

    if not username or not email or not ssh_key or not why:
        error('All fields must be provided.')
        return

    if not validate_username(username) is True:
        error('Invalid username')
        return

    ret = validate_sshkey(ssh_key) 
    if ret is not True:
        error('%s - Please check your SSH Key' % ret)
        return

    if not validate_email(email):
        error('Invalid email address provided')
        return

    try:
        if pwd.getpwnam(username):
            error('Username %s is already took' % username)
            return
    except KeyError:
        pass

    # Build Email
    with open(os.path.join(DATA_FOLDER, 'email_template.j2'), 'r') as fobj:
        template = Template(fobj.read())
    content = template.render({
        'date': datetime.now(),
        'username': username,
        'email': email,
        'ssh_key': ssh_key,
        'why': why,
    })

    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = f'[DIMENSION.SH] New User Request - {username}'
    msg['From'] = 'nobody@dimension.sh'
    msg['To'] = REQUEST_DESTINATION_EMAIL

    # Send email
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()

    sys.stdout.write('Location: http://dimension.sh/join/submitted/\n\n')


if __name__ == '__main__':
    main()
