from django.core.management.base import BaseCommand
from pydrraw.models import Dgraph, GraphItems
import re, urlparse

class Command(BaseCommand):
    args = '<drraw saved path>'
    help = 'Refresh the RRD info table from the filesystem for a configured rrd path'
## Open the file with read only permit


#    def _populate_db(self, *args):
	#print args
#        for templatename in args:
#            try:
#	        datasources = Rrdpaths.dumpfileinfo(Rrdpaths.objects.get(name=str(templatename)))
#		for rrdsource,spath,filename,dsource in datasources:
		    #print spath
		    #for x in range (0, 100):
#			cleanpath = re.sub(r'^/',r'', spath)
#			record = Rrdfiles(file=filename, subpath=cleanpath, rootdir=rrdsource, ds=dsource)
#			record.save()
#                	self.stdout.write('Successfully closed poll "%s"' % d) 
#            except templatename.DoesNotExist:
#                raise CommandError('Cannot get anything from "%s"' % templatename)

    def handle(self, *args, **options):
    	for templatename in args:
#	    if templatename[0:1] == 't':
 		print templatename
		f = open(templatename, "r")
		lines = f.readlines()
		f.close()
#		print lines
		attribs = []
		for line in lines:
			currentattrib = line.split('=',1)
			attribs.append(currentattrib)
			print currentattrib[0]
			print urlparse.unquote(currentattrib[1]).strip()
			#matchObj = re.search( r'^(.*)=(?:.+){0,1}$', line, re.M|re.I)
			#print matchObj.group(1)
			#if matchObj.group(2):
		#		print matchObj.group(2)


#	for line in lines:
#		if  
#	self._clear_db(*args)
#	self._populate_db(*args)
