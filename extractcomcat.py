#!/usr/bin/env python

import urllib2
import urllib
import json
import re
import datetime
from xml.dom import minidom

#local imports
from losspager.util import timeutil

URLBASE = 'http://comcat.cr.usgs.gov/earthquakes/feed/search.php?%s'

def parseComment(comment):
    m = re.search('[a-z]',comment)
    badblock = comment[0:m.start()]
    ridx = badblock.rfind('.')
    return comment[ridx+1:].strip()

def getComments():
    cdictlist = []
    startyear = 1976
    endyear = datetime.datetime.now().year+1
    istart = datetime.datetime(startyear,1,1,0,0,0)
    iend = datetime.datetime(startyear,12,31,23,59,59)
    while iend.year <= endyear:
        mintime = int(timeutil.toTimeStamp(istart))*1000
        maxtime = int(timeutil.toTimeStamp(iend))*1000
        pdict = {'eventSource':'pde','callback':'comsearch',
                 'minEventTime':mintime,'maxEventTime':maxtime}
        params = urllib.urlencode(pdict)
        searchurl = URLBASE % params
        fh = urllib2.urlopen(searchurl)
        data = fh.read()
        fh.close()
        data2 = data[len(pdict['callback'])+1:-2]
        datadict = json.loads(data2)
        features = datadict['features']
        for feature in features:
            eventurl = feature['properties']['url']+'.json'
            fh = urllib2.urlopen(eventurl)
            data = fh.read()
            fh.close()
            eventdict = json.loads(data)
            print 'Reading event %s' % eventdict['summary']['id']
            for origin in eventdict['products']['origin']:
                if origin['eventsource'] != 'pde':
                    continue
                quakeurl = origin['contents']['quakeml.xml']['url']
                fh = urllib2.urlopen(quakeurl)
                data = fh.read()
                dom = minidom.parseString(data)
                comments = dom.getElementsByTagName('comments')
                ncomments = len(comments)
                for comment in comments:
                    if comment.parentNode.nodeName != 'event':
                        continue
                    cdata = comment.getElementsByTagName('text')[0].firstChild.data
                    cdata2 = parseComment(cdata)
                dom.unlink()
                fh.close()
                
            
        istart = datetime.datetime(istart.year+1,1,1,0,0,0)
        iend = datetime.datetime(istart.year,12,31,23,59,59)
        
        
    
    return datadict

def main():
    pass

if __name__ == '__main__':
    comdicts = getComments()
