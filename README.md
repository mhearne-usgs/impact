Introduction
------------

impact is a project designed to provide a library for creating ANSS Impact Products.

Installation and Dependencies
-----------------------------

This package depends on neicio, part of an effort at the NEIC to create generally useful Python libraries from
the <a href="http://earthquake.usgs.gov/earthquakes/pager/">PAGER</a> source code.

To install neicio (and it's dependencies), follow the instructions on the neicio page:

https://github.com/usgs/neicio

If you have the dependencies installed, do:

pip install git+git://github.com/usgs/neicio.git

To install this package:

pip install git+git://github.com/mhearne-usgs/impact.git

Uninstalling and Updating
-------------------------

To uninstall:

pip uninstall impact

To update:

pip install -U git+git://github.com/mhearne-usgs/impact.git

Application Programming Interface (API) Usage
----------------------------------------------------- 

The library code will be installed in
<PATH_TO_PYTHON>/lib/pythonX.Y/site-packages/impact/.  Developers
should be able to use the class in impact.py by
importing it:

<pre>
from impact.impact import ImpactObject
event = {'id':'12345678',
             'lat':34.1234,
             'lon':-118.1234,
             'depth':10.0,
             'time':datetime.utcnow(),
             'magnitude':6.1,
             'effects':[
                 {'preferred':True,
                  'effecttype':TSUNAMI,
                  'source':'UTSU',
                  'comment':'Tsunami swamped the island'},
                 {'preferred':False,
                  'effecttype':TSUNAMI,
                  'source':'NOAA',
                  'comment':'Small tsunami waves detected'}
             ],
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
                  'comment':'nearly 100 deaths'},
                 {'preferred':True,
                  'source':'pde',
                  'losstype':'injured',
                  'value':1000,
                  'valuetype':ATLEAST,
                  'comment':'at least 1000 injuries'},
                  {'preferred':False,
                   'source':'emdat',
                   'losstype':'injured',
                   'value':(1100,1200),
                   'valuetype':RANGE,
                   'comment':'Between 1100 and 1200 injured'}]}
    itag = ImpactObject(event)
    xmltext = itag.renderToString()
    for line in xmltext.split('\n'):
        if not len(line.strip()):
            continue
        print line
</pre>

