#!/usr/bin/env python

#stdlib imports
from datetime import datetime
import xml.dom.minidom

#local imports
from neicio.tag import Tag


TIMEFMT = '%Y-%m-%dT%H:%M:%S'

#types
PEOPLE = 'people'
BUILDINGS = 'buildings'
DOLLARS = 'dollars'

#extents
KILLED = 'killed'
INJURED = 'injured'
DISPLACED = 'displaced'
DAMAGED = 'damaged'
DESTROYED = 'destroyed'
DAMAGED_OR_DESTROYED = "damaged or destroyed"
MISSING = 'missing'

#causes
SHAKING = 'shaking'
TSUNAMI = 'tsunami'

LOSSES = {'shakingDeaths':{'type':PEOPLE,'cause':SHAKING,'extent':KILLED},
          'tsunamiDeaths':{'type':PEOPLE,'cause':TSUNAMI,'extent':KILLED},
          'totalDeaths':{'type':PEOPLE,'extent':KILLED},
          'injured':{'type':PEOPLE,'extent':INJURED},
          'displaced':{'type':PEOPLE,'extent':DISPLACED},
          'missing':{'type':PEOPLE,'extent':MISSING},
          'buildingsDamaged':{'type':BUILDINGS,'cause':SHAKING,'extent':DAMAGED},
          'buildingsDestroyed':{'type':BUILDINGS,'cause':SHAKING,'extent':DESTROYED},
          'buildingsDamagedOrDestroyed':{'type':BUILDINGS,'cause':SHAKING,'extent':DAMAGED_OR_DESTROYED},
          'tsunamiBuildingsDamaged':{'type':BUILDINGS,'cause':TSUNAMI,'extent':DAMAGED},
          'tsunamiBuildingsDestroyed':{'type':BUILDINGS,'cause':TSUNAMI,'extent':DESTROYED},
          'tsunamiBuildingsDamagedOrDestroyed':{'type':BUILDINGS,'cause':TSUNAMI,'extent':DAMAGED_OR_DESTROYED},
          'economicLoss':{'type':DOLLARS}}

#loss qualifiers
FEW = "few"
SOME = "some"
MANY = "many"
NEARLY = "nearly"
ATLEAST = "at least"
UNCONFIRMED = "unconfirmed"
ESTIMATE = "estimate"
EXACT = "exact"
RANGE = "range"



class ImpactTag(object):
    def __init__(self,eventdict):
        self.quaketag = self.createEventTag(eventdict)

    def createEventTag(self,event):
        quaketag = Tag('q:quakeml',attributes={'xmlns':'http://quakeml.org/xmlns/bed/1.2',
                                               'xmlns:q':'http://quakeml.org/xmlns/quakeml/1.2',
                                               'xmlns:catalog':'http://anss.org/xmlns/catalog/0.1',
                                               'xmlns:impact':'http://anss.org/xmlns/impact/0.1'})
        pubid = 'quakeml:us.anss.org/eventparameters/%s/%i' % (event['id'],int(datetime.utcnow().strftime('%s')))
        pubeventid = 'quakeml:us.anss.org/event/%s/%i' % (event['id'],int(datetime.utcnow().strftime('%s')))
        paramtag = Tag('eventParameters',attributes={'xmlns':'http://quakeml.org/xmlns/bed/1.2',
                                                     'publicID':pubid})
        eventtag = Tag('event',attributes={'catalog:dataid':'us%s' % event['id'],
                                           'catalog:datasource':'us',
                                           'catalog:eventid':'%s' % event['id'],
                                           'publicID':pubeventid,
                                           'catalog:eventsource':'us'})
        if event.has_key('magnitude'):
            magtag = self.createMagTag(event)
            eventtag.addChild(magtag)
        hypotag = self.createOriginTag(event)
        eventtag.addChild(hypotag)
        
        for impact in event['impacts']:
            losstag,preftag = self.createLossTag(impact)
            if preftag:
                eventtag.addChild(preftag)
            eventtag.addChild(losstag)

        paramtag.addChild(eventtag)
        quaketag.addChild(paramtag)

        return quaketag


    def createValueTag(self,value,valuetype):
        subvaluetag = None
        lowertag = None
        uppertag = None
        valuetag = Tag('impact:value')
        vstr = '%i' % value
        if valuetype == ATLEAST:
            lowertag = Tag('lowerUncertainty',data=vstr)
        if valuetype == NEARLY:
            uppertag = Tag('upperUncertainty',data=vstr)
        if valuetype == RANGE:
            lower = value[0]
            upper = value[1]
            dmean = int((lower+upper)/2.0)
            subvaluetag = Tag('value',data='%i' % dmean)
            lowertag = Tag('lowerUncertainty',data='%i' % lower)
            uppertag = Tag('upperUncertainty',data='%i' % upper)
        else:
            subvaluetag = Tag('value',data=vstr)
        valuetag.addChild(subvaluetag)
        if lowertag:
            valuetag.addChild(lowertag)
        if uppertag:
            valuetag.addChild(uppertag)

        return valuetag

    def createSourceTag(self,source):
        authortag = Tag('author',data=source)
        sourcetag = Tag('impact:creationInfo')
        sourcetag.addChild(authortag)
        return sourcetag
    
    def createLossTag(self,impact):
        #impact['comment'] = "101 deaths from shaking"
        #impact['value'] = 101 (or two element tuple, for range)
        #impact['losstype'] = "shakingDeaths"
        #impact['source'] = "Centre for Research on the Epidemiology of Disasters (CRED)"
        #impact['valuetype'] = "exact" (exact,at least,estimated,unconfirmed,range,at most,some)
        #101 shaking deaths 
        impactid = impact['source']+impact['losstype']
        preftag = None
        if impact['preferred']:
            preftag = Tag('impact:preferredImpactEstimateID',
                          data='quakeml:expocat.anss.org/impactEstimate/%s' % impactid)
        lossdict = LOSSES[impact['losstype']]
        typetag = Tag('impact:type',data=lossdict['type'])
        causetag = None
        if lossdict.has_key('cause'):
            causetag = Tag('impact:cause',data=lossdict['cause'])
        extenttag = None
        if lossdict.has_key('extent'):
            extenttag = Tag('impact:extent',data=lossdict['extent'])
        qualifiertag = Tag('impact:qualifier',data=impact['valuetype'])

        valuetag = self.createValueTag(impact['value'],impact['valuetype'])
        sourcetag = self.createSourceTag(impact['source'])
        commenttag = Tag('impact:comment',data=impact['comment'])
        losstag = Tag('impact:loss',attributes={'impact:publicID':impactid})
        losstag.addChild(typetag)
        losstag.addChild(valuetag)
        losstag.addChild(commenttag)
        if extenttag:
            losstag.addChild(extenttag)
        if causetag:
            losstag.addChild(causetag)
        losstag.addChild(qualifiertag)
        losstag.addChild(sourcetag)

        return (losstag,preftag)
        
    def createMagTag(self,event):
        pubid = 'quakeml:us.anss.org/magnitude/%s' % event['id'][2:]
        valuetag = Tag('value',data='%.1f' % (event['magnitude']))
        magtag = Tag('mag')
        magtag.addChild(valuetag)
        magnitudetag = Tag('magnitude',attributes={'publicID':pubid})
        magnitudetag.addChild(magtag)
        return magnitudetag

    def createOriginTag(self,event):
        eventcode = event['id']
        origintag = Tag('origin',attributes={'catalog:dataid':'us'+eventcode,
                                             'catalog:datasource':'us',
                                             'catalog:eventid':eventcode,
                                             'publicID':'quakeml:us.anss.org/origin/%s' % eventcode})
        #time
        timetag = Tag('time')
        tvaluetag = Tag('value',data = event['time'].strftime(TIMEFMT))
        timetag.addChild(tvaluetag)

        #lat
        lattag = Tag('latitude')
        latvaluetag = Tag('value',data='%.4f' % (event['lat']))
        lattag.addChild(latvaluetag)

        #lon
        lontag = Tag('longitude')
        lonvaluetag = Tag('value',data='%.4f' % (event['lon']))
        lontag.addChild(lonvaluetag)

        #depth
        depthtag = Tag('depth')
        depthvaluetag = Tag('value',data='%i' % (int(event['depth']*1000)))
        depthtag.addChild(depthvaluetag)

        #creation info
        origincreationtag = Tag('creationInfo')
        originauthortag = Tag('author',data='NEIC')
        origincreationtag.addChild(originauthortag)

        #roll up the origin tag
        origintag.addChild(timetag)
        origintag.addChild(lattag)
        origintag.addChild(lontag)
        origintag.addChild(depthtag)
        origintag.addChild(origincreationtag)

        return origintag

if __name__ == '__main__':
    event = {'id':'us12345678',
             'lat':34.1234,
             'lon':-118.1234,
             'depth':10.0,
             'time':datetime.utcnow(),
             'magnitude':6.1,
             'impacts':[
                 {'preferred':True,
                  'source':'pde',
                  'losstype':'shakingDeaths',
                  'value':101,
                  'valuetype':EXACT,
                  'comment':'101 deaths caused by shaking'},
                 {'preferred':False,
                  'source':'utsu',
                  'losstype':'shakingDeaths',
                  'value':100,
                  'valuetype':NEARLY,
                  'comment':'nearly 100 injuries'},
                 {'preferred':True,
                  'source':'pde',
                  'losstype':'injured',
                  'value':1000,
                  'valuetype':ATLEAST,
                  'comment':'at least 1000 injuries'}]}
    itag = ImpactTag(event)
    xmltext = itag.quaketag.renderTag(0)
    #strip out all newline characters
    xmltext = xmltext.replace('\n','')
    xmltext = xmltext.replace('\t','')
    #print xmlstr
    root = xml.dom.minidom.parseString(xmltext)
    pretty_xml_as_string = root.toprettyxml(indent="  ")
    for line in pretty_xml_as_string.split('\n'):
        if not len(line.strip()):
            continue
        print line
