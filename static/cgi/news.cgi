#!/usr/bin/env python3

import sys
import os
import cgi
import glob
import math
from datetime import datetime

from jinja2 import Template
from markdown.extensions.wikilinks import WikiLinkExtension
import markdown
import frontmatter


DATA_FOLDER = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data'))
NEWS_ROOT = '/srv/news/'
MAX_NEWS_ARTICLES = 5


def get_template(template_name):
    with open(os.path.join(DATA_FOLDER, template_name + '.j2'), 'r') as fobj:
        return Template(fobj.read())


def parse_markdown(page_data):
    extensions = [
        'tables',
        'fenced_code',
    ]
    return markdown.markdown(page_data, extensions=extensions)


def main(output=sys.stdout):
    output.write('Content-Type: text/html\n\n')

    qs = cgi.parse()
    try:
        if 'page' in qs and len(qs['page']):
            page = int(qs['page'][0])
            if page < 0:
                page = 1
        else:
            page = 1
    except:
        page = 1

    # Get the news files, and paginate
    filenames = glob.glob(os.path.join(NEWS_ROOT, '*.md'))
    filenames.sort(reverse=True)
    start = (page - 1) * MAX_NEWS_ARTICLES
    max_page = math.ceil(len(filenames) / MAX_NEWS_ARTICLES)

    html = ''
    news_template = get_template('news_template')
    for filename in filenames[start:start + MAX_NEWS_ARTICLES]:
        with open(filename, 'r') as fobj:
            post = frontmatter.load(fobj)
        html += news_template.render(post=post, rendered_post=parse_markdown(post.content))

    output.write(html)


if __name__ == '__main__':
    main()
