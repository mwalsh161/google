import Google
import re, datetime, sys
from pyquery import PyQuery as pq

def main():
    g = Google.Google()
    g.authenticate()

    l = -1
    at_least_one = False
    for msg in g.search(query):
        at_least_one = True
        if g.resultSizeEstimate != l:
            l = g.resultSizeEstimate
            print l

        content = g.GetMimeMessage(msg['id'])
        print content['subject']
    if not at_least_one:
        print 'No results'

if __name__ == '__main__':
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        print 'Searching: %s'%query
    else:
        print 'No query typed!'
        exit()
    main()
