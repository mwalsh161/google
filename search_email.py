import Google
import re, datetime, sys
from pyquery import PyQuery as pq

if len(sys.argv) > 1:
    query = ' '.join(sys.argv[1:])
    print 'Searching: %s'%query
else:
    print 'No query typed!'
    exit()

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

#         content_plain = content.get_payload()[0].get_payload().replace('\r\n','\n')
#         content_html = content.get_payload()[1].get_payload()
#         m = exp.findall(content_plain)
#         print '  Got %i matches.'%len(m)
#         if len(m) != 2:
#             continue
#         title.append(m[0])
#         abstract.append(re.sub(r'(\w)\n(\w)',r'\1 \2',content_plain.split('\n\n')[-1].strip()))
#         amended = re.sub('\d+(st|nd|rd|th)', lambda m: m.group()[:-2].zfill(2),m[1])
#         date.append(datetime.datetime.strptime(amended,'%A, %B %m, %Y'))
#     except:
#         continue
#     # d = pq(content_html)
#     # for el in d('font'):
#     #     if '3D"6"' == el.get('size'):
#     #         print '  Found title'
#     #         title.append(el.text_content())
#     #         exit()

# print ''
# print 'Date(s):\n  %s'%'\n  '.join([d.strftime('%x') for d in date])
# print 'Title(s):\n  %s'%'\n  '.join(title)
# print 'Abstract(s):\n  %s'%'\n  '.join(abstract)