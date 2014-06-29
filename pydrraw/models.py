from django.db import models
import datetime, os, time
from django.utils import timezone
from smart_selects.db_fields import GroupedForeignKey
from pyrrd.rrd import RRD
from django.core.urlresolvers import reverse

class GraphItemColorCycle(models.Model):
	name = models.CharField(max_length=20, primary_key=True)
    	def __unicode__(self): 
		return self.name

class GraphItemColorCycleColor(models.Model):
	name = models.ForeignKey(GraphItemColorCycle)
	color = models.CharField(max_length=6, default='FFFFFF')
	transparency = models.CharField(max_length=2, default='FF')
	seq = models.IntegerField(max_length=20, blank=True)
    	def __unicode__(self): 
		return self.color

class GraphColorScheme(models.Model):
	COLORS = {
	('#000066','SkyBlue'),
	('#000000','Black'),
	('#C0C0C0','Silver'),
	('#808080','Gray'),
	('#FFFFFF','White'),
	('#800000','Maroon'),
	('#FF0000','Red'),
	('#800080','Purple'),
	('#FF00FF','Fuchsia'),
	('#008000','Green'),
	('#00FF00','Lime'),
	('#808000','Olive'),
	('#FFFF00','Yellow'),
	('#FFA500','Orange'),
	('#000080','Navy'),
	('#0000FF','Blue'),
	('#008080','Teal'),
	('#00FFFF','Aqua'),
	}
	name = models.CharField(max_length=20, primary_key=True)
	name.unique
    	cback = models.CharField(max_length=7, blank=True, choices=COLORS)
    	tback = models.CharField(max_length=2, blank=True)
    	ccanvas = models.CharField(max_length=7, blank=True, choices=COLORS)
    	tcanvas = models.CharField(max_length=2, blank=True)
    	cshadea = models.CharField(max_length=7, blank=True, choices=COLORS)
    	tshadea = models.CharField(max_length=2, blank=True)
    	cshadeb = models.CharField(max_length=7, blank=True, choices=COLORS)
    	tshadeb = models.CharField(max_length=2, blank=True, verbose_name="Shade B Transparency")
    	cmgrid = models.CharField(max_length=7, blank=True, choices=COLORS)
    	tmgrid = models.CharField(max_length=2, blank=True, )
    	caxis = models.CharField(max_length=7, blank=True, choices=COLORS)
    	taxis = models.CharField(max_length=2, blank=True, )
    	cframe = models.CharField(max_length=7, blank=True, choices=COLORS)
    	tframe = models.CharField(max_length=2, blank=True, )
    	cfont = models.CharField(max_length=7, blank=True, choices=COLORS)
    	tfont = models.CharField(max_length=2, blank=True, )
    	carrow = models.CharField(max_length=7, blank=True, choices=COLORS)
    	tarrow = models.CharField(max_length=2, blank=True, )
    	def __unicode__(self): 
		return self.name
	


class Rrdpath(models.Model):
	name = models.CharField(max_length=20, primary_key=True)
	name.unique
	path = models.CharField(max_length=200)
	path.unique

    	def __unicode__(self):  # Python 3: def __str__(self):
        	return self.name
	def listfiles(self):
	        #rrds = os.walk(self.path)
		mylist = []
		for root, dir, files in os.walk(self.path):
        		for sfile in files:
				filename = os.path.join(root, sfile)
				subpath = filename[len(self.path):]
				mylist.append(filename)
		return mylist
	def dumpfileinfo(self):
	        #rrds = os.walk(self.path)
		mylist = []
		for root, dir, files in os.walk(self.path):
        		for sfile in files:
				filename = os.path.join(root, sfile)
				subpath = filename[len(self.path):]
		                rrd = RRD(filename, mode='r')
		                info = rrd.getData()
				for i in rrd.ds:
					mylist.append((self,subpath,sfile,i.name),)
		return mylist
	def updaterrdcache(self):
	        #rrds = os.walk(self.path)
		mylist = []
		for root, dir, files in os.walk(self.path):
        		for sfile in files:
				filename = os.path.join(root, sfile)
				subpath = filename[len(self.path):]
		                #rrd = RRD(filename, mode='r')
		                #info = rrd.getData()
				#for i in rrd.ds:
				#	mylist.append((self.name,root,dir,sfile,i.name),)
				mylist.append((self,subpath,sfile),)
		return mylist

class Rrdfiles(models.Model):
	rootdir = models.ForeignKey(Rrdpath)
	file = models.CharField(max_length=200)
	subpath = models.CharField(max_length=200)
	ds = models.CharField(max_length=200, default="value")
	class Meta:
        	unique_together = (("rootdir", "subpath", "ds"))

	def __unicode__(self):  # Python 3: def __str__(self):
        	return u'%s %s %s' % ((self.rootdir, self.subpath, self.ds))
        	#return (self.subpath)

class Rrdgraph(models.Model):
    COLORS = {
	('#000066','SkyBlue'),
	('#000000','Black'),
	('#C0C0C0','Silver'),
	('#808080','Gray'),
	('#FFFFFF','White'),
	('#800000','Maroon'),
	('#FF0000','Red'),
	('#800080','Purple'),
	('#FF00FF','Fuchsia'),
	('#008000','Green'),
	('#00FF00','Lime'),
	('#808000','Olive'),
	('#FFFF00','Yellow'),
	('#FFA500','Orange'),
	('#000080','Navy'),
	('#0000FF','Blue'),
	('#008080','Teal'),
	('#00FFFF','Aqua'),
	}
    name = models.CharField(max_length=200)
    vertical_label = models.CharField(max_length=100)
    graph_options = models.CharField(max_length=200, blank=True)
    upper_limit = models.CharField(max_length=200, blank=True)
    lower_limit = models.CharField(max_length=199, blank=True)
    rigid_boundaries = models.BooleanField(default=False)
    logarithmic = models.BooleanField(default=False)
    only_graph = models.BooleanField(default=False)
    alt_autoscale = models.BooleanField(default=False)
    alt_autoscale_max = models.BooleanField(default=False)
    no_gridfit = models.BooleanField(default=False)
    x_grid = models.BooleanField(default=False)
    y_grid = models.BooleanField(default=False)
    alt_y_grid = models.BooleanField(default=False)
    units_exponent = models.BooleanField(default=False)
    color = models.CharField(max_length=200, default='#FFFFFF')
    zoom = models.BooleanField(default=False)
    font = models.CharField(max_length=200, blank=True)
    font_render_mode = models.CharField(max_length=200, blank=True)
    no_legend = models.BooleanField(default=False)
    force_rules_legend = models.BooleanField(default=False)
    tabwidth = models.IntegerField(default=1000, blank=True)
    base = models.IntegerField(default=1000)
    slope_mode = models.BooleanField(default=True)
    backend = models.CharField(max_length=200, blank=True)
    showdate_start = models.BooleanField(default=False)
    showdate_end = models.BooleanField(default=False)
    showdate_now = models.BooleanField(default=False)
    pub_date = models.DateTimeField('last published', auto_now=True)
    gcolorscheme = models.ForeignKey(GraphColorScheme, default='default')
    def __unicode__(self):  # i am but a name
        return self.name
    def image_tag(self): # get the latest image on first load and by clicking
	now = int(time.time())
	imgurl = reverse('pydrraw:drawgraph', kwargs={'graphid':int(self.id)})
	updateimg = '"this.src=' + "'" + imgurl + "?end='" + ' + (Math.round(new Date().getTime() / 1000))"'
	imgtag = '<img src="' + imgurl + '" onLoad= ' + updateimg + 'onClick=' + updateimg + ' />'
	return imgtag
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date < now
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

class GraphItems(models.Model):
        graph = models.ForeignKey(Rrdgraph)
        ITEMOPTIONS = {
        ('S', 'Static'),
        ('R', 'REGEX'),
        ('C', 'CDEF'),
        ('V', 'VDEF'),
	}
        LINEOPTIONS = {
        ('A', 'Area'),
        ('G', 'Gprint'),
        ('L1', 'Line1'),
        ('L2', 'Line2'),
        ('L3', 'Line3'),
	}
	RRAS = {
	('MAX', 'MAX'),
	('MIN', 'MIN'),
	('AVERAGE', 'Average'),
	('LAST', 'Last'),
	}
	COLORS = {
	('#000066','SkyBlue'),
	('#000000','Black'),
	('#C0C0C0','Silver'),
	('#808080','Gray'),
	('#FFFFFF','White'),
	('#800000','Maroon'),
	('#FF0000','Red'),
	('#800080','Purple'),
	('#FF00FF','Fuchsia'),
	('#008000','Green'),
	('#00FF00','Lime'),
	('#808000','Olive'),
	('#FFFF00','Yellow'),
	('#FFA500','Orange'),
	('#000080','Navy'),
	('#0000FF','Blue'),
	('#008080','Teal'),
	('#00FFFF','Aqua'),
	}

        itemtype = models.CharField(max_length=7, choices=ITEMOPTIONS)
	rrdds = models.ForeignKey(Rrdfiles, null=True, blank=True)
        linetype = models.CharField(max_length=7, choices=LINEOPTIONS, default='L1')
	stack = models.BooleanField(default=False)
        color = models.CharField(max_length=7, default='000000')
        transparency = models.CharField(max_length=2, default='FF')
        rra = models.CharField(max_length=7, choices=RRAS, default='AVERAGE')
        option_text = models.CharField(max_length=200, blank=True)
	seq = models.IntegerField(max_length=20, null=True)

class Dash(models.Model):
	RATIOS = {
	(1, '1'),
	(2, '2'),
	(3, '3'),
	(4, '4'),
	(5, '5'),
	(6, '6'),
	(7, '7'),
	(8, '8'),
	}
	TIMESPANS = {
	(1800,'Last Half Hour'),
	(3600,'Last Hour'),
	(86400,'Last Day'),
	(365*86400,'Last Year'),
	}
	name = models.CharField(max_length=1000)
	description = models.CharField(max_length=1000)
	timespan = models.IntegerField(choices=TIMESPANS)
	columns = models.IntegerField(default=4)
	width = models.IntegerField(default=400)
	height = models.IntegerField(default=200)
	hmargin = models.IntegerField(default=2)
	vmargin = models.IntegerField(default=2)
	nolegend = models.BooleanField(default=True)
	graphonly = models.BooleanField(default=False)
	forcecolor = models.BooleanField(default=True)
	gcolorscheme = models.ForeignKey(GraphColorScheme, default='default')
	#dcolorscheme = models.ForeignKey(GraphColorScheme)
	serialized_layout = models.CharField(max_length=1000, blank=True)
    	def __unicode__(self):  # Python 3: def __str__(self):
        	return self.name

#class DashLayouts(models.Model):
#        dashboard = models.OneToOneField(Dash, primary_key=True)
#	serialized_layout = models.CharField(max_length=1000, blank=True)
#    	def __unicode__(self):  # Python 3: def __str__(self):
#        	return "%s" % self.serialized_layout

class DashItems(models.Model):
        dashboard = models.ForeignKey(Dash)
	TYPES = {
	('B','Table'),
	('S','Pydrraw Graph'),
	('T','Pydrraw Template'),
	('C','Cacti Image URL'),
	('I','Generic Image URL'),
	('F','Generic IFrame URL'),
	('H','Generic HTML'),
	('G','Graphite Image URL'),
	}
	RATIOS = {
	(1, '1'),
	(2, '2'),
	(3, '3'),
	(4, '4'),
	(5, '5'),
	}
	type = models.CharField(max_length=20, choices=TYPES, default='S')
	graphurl = models.URLField(max_length=1000, blank=True)
	alttext = models.CharField(max_length=1000, blank=True)
	graphid = models.ForeignKey(Rrdgraph, null=True, blank=True)
	seq = models.IntegerField(max_length=20, null=True)
	widthratio = models.IntegerField(choices=RATIOS, default=1)
	heightratio = models.IntegerField(choices=RATIOS, default=1)
	timelagratio = models.IntegerField(max_length=200, default=1)
    	def __unicode__(self):  # Python 3: def __str__(self):
        	return self.graphid

