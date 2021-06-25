#!/usr/bin/env python3
import sys
from twtxt.parser import parse_tweets


def main(output=sys.stdout):
    output.write('Content-Type: text/html\n\n')

    with open('/srv/news/patchlog.txt', 'r') as fobj:
        tweets = parse_tweets(fobj.readlines(), 'patchlog')

    output.write("<div id='patchlog'>")
    for tweet in sorted(tweets, key=lambda x: x.created_at, reverse=True)[:10]:
        output.write(f"<div class='patchentry'><b class='date'>{tweet.created_at.date()}</b><p>{tweet.text}</p></div>")
    output.write("</div>")


if __name__ == '__main__':
    main()
