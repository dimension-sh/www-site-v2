#!/usr/bin/env python3
# Updates the user page on the website with the current user list
import sys
import json


def main(output=sys.stdout):
    output.write('Content-Type: text/html\n\n<ul class="user-list">\n')

    with open('../tilde.json', 'r') as fobj:
        data = json.loads(fobj.read())
    for user in data['users']:
        output.write(
            '<li><a href="/~{username}">~{username}</a></li>\n'.format(**user))

    output.write("</ul>\n")
    output.write("<p>Total Users: <b>%d</b></p>" % len(data['users']))


if __name__ == '__main__':
    main()
