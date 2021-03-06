#!/usr/bin/env python

# Copyright (c) 2008 Kristinn B. Gylfason <citeulike@askur.org>,

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2 of the License.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.

# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.


import sys, cgi, urlparse, urllib2
import socket, re

socket.setdefaulttimeout(15)

# "http://pubs.rsc.org/en/content/formatedresult?markedids=c2an15930a&downloadtype=article&managertype=endnote"
#CITATION_SERVER_ROOT = 'http://www.rsc.org/delivery/_ArticleLinking/refdownload.asp'
#REQ_STR = '?ManuscriptId=%(article_id)s&type=refman'
CITATION_SERVER_ROOT = "http://pubs.rsc.org/en/content/formatedresult"
REQ_STR = "?markedids=%(article_id)s&downloadtype=article&managertype=endnote"
QUERY=4;
REQ_DATA = {}

# error messages
ERR_STR_PREFIX = 'status\terr\t'
ERR_STR_FETCH = 'Unable to fetch the bibliographic data: '
ERR_STR_TRY_AGAIN = 'The server may be down.  Please try later.'
ERR_STR_NO_KEYS = 'Could not extract article details from the URL: '
ERR_STR_REPORT = 'Please report the error to plugins@citeulike.org.'

# read url from std input an get rid of the newline at the end
url = sys.stdin.readline().strip()

# parse the article details from the url
parsed_url = urlparse.urlparse(url)
src_query = cgi.parse_qs(parsed_url.query)
path = parsed_url.path

# new style http://pubs.rsc.org/en/Content/ArticleLanding/2002/CC/b204846a
# http://pubs.rsc.org/en/content/articlelanding/2011/lc/c1lc20128j
m = re.match(r'^/en/Content/ArticleLanding/[^/]+/[^/]+/([^/]+)', path, re.I)
if m:
    REQ_DATA['article_id'] = m.group(1)
elif src_query.has_key('doi'):
    # OLD STYLE
    REQ_DATA['article_id'] = src_query['doi'][0]
elif src_query.has_key('ManuscriptID'):
    # OLD STYLE
    REQ_DATA['article_id'] = src_query['ManuscriptID'][0]
else:
    print ERR_STR_PREFIX + ERR_STR_NO_KEYS + url + '.  ' + ERR_STR_REPORT
    sys.exit(0)

# fetch the bibligraphic data
try:
    f = urllib2.urlopen(CITATION_SERVER_ROOT + REQ_STR % REQ_DATA)
except:
    print ERR_STR_PREFIX + ERR_STR_FETCH + CITATION_SERVER_ROOT + '.  ' + ERR_STR_TRY_AGAIN
    sys.exit(0)

entry = f.read().strip()

# fix a bug in the RSCs RIS formating
entry = entry.replace('Y1 -  ','Y1  - ',1)

# print the results
print "begin_tsv"
print "linkout\tRSC\t\t%s\t\t" % (REQ_DATA['article_id'])
print "linkout\tDOI\t\t10.1039/%s\t\t" % (REQ_DATA['article_id'])
print "type\tJOUR"
print "end_tsv"
print "begin_ris"
print entry
print "end_ris"
print "status\tok"
