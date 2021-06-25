#!/usr/bin/env python3

from jinja2 import Template
from markdown.extensions.wikilinks import WikiLinkExtension
import markdown
import sys
import os
import cgi


DATA_FOLDER = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data'))
WIKI_ROOT = '/srv/wiki/'
BAD_CHARACTERS = ['.', '/', '\\', ' ']

with open(os.path.join(DATA_FOLDER, 'wiki_template.j2')) as fobj:
    template = Template(fobj.read())

sys.stdout.write('Content-Type: text/html\n\n')

# Get page name
qs = cgi.parse()
if 'p' in qs and len(qs['p']):
    page = qs['p'][0].lower()
else:
    page = 'index'

# Sanitize for bad filenames
for char in BAD_CHARACTERS:
    page = page.replace(char, '_')

# Sanitize path and check if the page exists
page_path = os.path.abspath(os.path.join(WIKI_ROOT, '%s.md' % page))
if not page_path.startswith(WIKI_ROOT) or not os.path.exists(page_path):
    page_path = os.path.join(WIKI_ROOT, '404.md')

# Open and format the page
with open(page_path, 'r') as fobj:
    page_data = fobj.read()

    extensions = [
        'tables',
        'fenced_code',
        WikiLinkExtension(base_url='/cgi/wiki.cgi?p=', end_url=''),
    ]
    html = markdown.markdown(page_data, extensions=extensions)

# Render the output
sys.stdout.write(template.render(html=html))
