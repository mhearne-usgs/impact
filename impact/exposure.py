#!/usr/bin/env python

#stdlib imports
import json
from datetime import datetime

#local
from neicio import tag

EVENTREQFIELDS = ['lat','lon','depth','time','id','mag']
TIMEFMT = '%Y-%m-%dT%H:%M:%S%Z'

class ExposureObject(object):
    def __init__(self,eventdict,aggexp,countrydict):
        #first, verify that we have the appropriate fields in the event dictionary
        if set(eventdict.keys()) != EVENTREQFIELDS:
            raise Exception,"Input event dictionary does not have all required fields: %s" % (','.join(EVENTREQFIELDS))
        self.expdict = {}
        try:
            datetime.strptime(eventdict['time'],TIMEFMT)
        except:
            raise Exception,'event time: must have the format "%s"' % TIMEFMT
        aggtuple = [('mmi%i' % (i+1),aggexp[i]) for i in range(0,len(aggexp))]
        self.expdict['event'] = eventdict
        self.expdict['aggregatedExposures'] = aggtuple
        self.expdict['countryExposures'] = countrydict

    def renderToJSON(self,filename):
        jstring = json.dumps(self.expdict)
        f = open(filename,'wt')
        f.write(jstring)
        f.close()

    def makePDLPackage(self,folder):
        if not os.path.isdir(folder):
            os.path.makedirs(folder)
        jsonfile = os.path.join(folder,'exposure.json')
        self.renderToJSON(jsonfile)
        xmlfile = os.path.join(folder,'contents.xml')
        formattag = tag.Tag('format',attributes={'href':'exposure.json','type':'application/json'})
        desc = '<![CDATA[PAGER Exposure Data (JSON format)]]>'
        captiontag = tag.Tag('caption',data=desc)
        filetag = tag.Tag('file',attributes={'title':'PAGER Exposure Data','id':'expopager'})
        filetag.addChild(captiontag)
        filetag.addChild(formattag)
        contentstag = tag.Tag('contents')
        contentstag.addChild(filetag)
        xmlstr = contentstag.renderTag(0)
        xmlstr = xmlstr.replace('\t','')
        xmlstr = xmlstr.replace('\n','')
        f = open(xmlfile,'wt')
        f.write(xmlstr)
        f.close()
        
        
        
