#!/usr/bin/env python3
import sys

from twtxt.parser import parse_tweets


def main(output=sys.stdout):
    output.write('Content-Type: text/html\n\n')

    with open('/srv/news/patchlog.txt', 'r') as fobj:
        tweets = parse_tweets(fobj.readlines(), 'patchlog')

    output.write("<div id='patchlog'>")

    sorted_tweets = sorted(tweets, key=lambda entry: entry.created_at, reverse=True)
    for tweet in sorted_tweets[:10]:
        output.write("<div class='patchentry'><b class='date'>{0}</b><p>{1}</p></div>".format(tweet.created_at.date(), tweet.text))
    output.write('</div>')


if __name__ == '__main__':
    main()
