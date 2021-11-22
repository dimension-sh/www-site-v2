#!/usr/bin/env python3

import cgi
import glob
import os
import sys

import frontmatter
import markdown
from jinja2 import Template

DATA_FOLDER = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data'))
NEWS_ROOT = '/srv/news/'
MAX_NEWS_ARTICLES = 5


def get_template(template_name):
    template_filename = '{0}.j2'.format(template_name)
    with open(os.path.join(DATA_FOLDER, template_filename), 'r') as fobj:
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

    if 'page' in qs and len(qs['page']):
        try:
            page = int(qs['page'][0])
        except ValueError:
            page = 1
        else:
            if page < 0:
                page = 1
    else:
        page = 1

    # Get the news files, and paginate
    filenames = glob.glob(os.path.join(NEWS_ROOT, '*.md'))
    filenames.sort(reverse=True)
    start = (page - 1) * MAX_NEWS_ARTICLES

    html = ''
    news_template = get_template('news_template')
    for filename in filenames[start:start + MAX_NEWS_ARTICLES]:
        with open(filename, 'r') as fobj:
            post = frontmatter.load(fobj)
        html += news_template.render(post=post, rendered_post=parse_markdown(post.content))

    output.write(html)


if __name__ == '__main__':
    main()
