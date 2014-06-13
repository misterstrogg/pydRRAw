from django.core.management.base import BaseCommand
from pydrraw.models import Rrdfiles, Rrdpaths
import re

class Command(BaseCommand):
    args = '<name of rrd path>'
    help = 'Refresh the RRD info table from the filesystem for a configured rrd path'

    def _clear_db(self, *args):
	#print args
        for rrdpathname in args:
	    #print rrdpathname
	    rrds = Rrdfiles.objects.filter(rootdir__name=rrdpathname)
	    #print Rrdfiles.objects.filter(rootdir__name=rrdpathname)
	    #print rrds
	    print rrds.delete()

    def _populate_db(self, *args):
	#print args
        for rrdpathname in args:
#            try:
	        datasources = Rrdpaths.dumpfileinfo(Rrdpaths.objects.get(name=str(rrdpathname)))
		for rrdsource,spath,filename,dsource in datasources:
		    #print spath
		    #for x in range (0, 100):
			cleanpath = re.sub(r'^/',r'', spath)
			record = Rrdfiles(file=filename, subpath=cleanpath, rootdir=rrdsource, ds=dsource)
			record.save()
#                	self.stdout.write('Successfully closed poll "%s"' % d) 
#            except rrdpathname.DoesNotExist:
#                raise CommandError('Cannot get anything from "%s"' % rrdpathname)

    def handle(self, *args, **options):
	self._clear_db(*args)
	self._populate_db(*args)
