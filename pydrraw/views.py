# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
import os
import re
from pyrrd.rrd import DataSource, RRA, RRD
from pyrrd.graph import DEF, CDEF, VDEF, LINE, AREA, GPRINT, Graph, COMMENT
import simplejson
#import json
from pydrraw.models import Rrdfiles, Rrdpaths, GraphItems, Dgraph, Dash, DashItems
from django.views import generic
import time
from sets import Set

#rrdPath = 'DjangoRRD/public/rrds/'
#rrdPath = '/usr/var/lib/collectd/rrd/worm.circuit5.com/memory/'
class GraphDetailView(generic.ListView):
    #model = dGraph
    template_name = 'pydrraw/graphdetail.html'
    context_object_name = 'graph'
    def get_queryset(self):
        self.graph = get_object_or_404(Dgraph, name="yo")
        return GraphItems.objects.filter(graph=self.graph)
    def get_context_data(self, **kwargs):
	context = super(GraphDetailView, self).get_context_data(**kwargs)
	context['graph'] = self.graph
	return context

def paths(req, rrdpathname):
	rrdpaths = RRDpaths.objects.all()
	return render_to_response('pydrraw/paths.html', {'rrdpaths': rrdpaths})
	

def list(req, rrdpathname):
#	rrds = os.listdir(rrdPath)
        if (rrdpathname == "all"):
#                rrds = Rrdpaths.listfiles(rrdsource)
#	return render_to_response('pydrraw/list.html', {'rrds': rrds})
	        rrds = Rrdfiles.objects.all()
	else:
		rrds = Rrdfiles.objects.filter(rootdir__name=rrdpathname)

	return render_to_response('pydrraw/list.html', {'rrds': rrds, 'rrdpathname': rrdpathname})


def infoview(req, rrdpathname, rrd):
	filename = Rrdpaths.objects.get(name=str(rrdpathname)).path 
	fullfilename = filename + '/' + rrd
	if os.path.isfile(fullfilename):
		rrd = RRD(fullfilename, mode='r')
		info = rrd.getData()
		info['filename'] = filename
		#info['dslength'] = 5
		info['rrdpathname'] = str(rrdpathname)
		return render_to_response('pydrraw/info.html', {'info': info})
    		#return HttpResponse(fullfilename,mimetype="text/plain")

def raw(req, rrdpathname, rrd):
	filename = Rrdpaths.objects.get(name=str(rrdpathname)).path 
	fullfilename = filename + '/' + rrd
	if os.path.isfile(fullfilename):
                myrrd = RRD(fullfilename, mode='r')
                info = myrrd.getData()
		info['rrdpathname'] = rrdpathname
		info['rrd'] = rrd
		info['filename'] = filename
        	return render_to_response('pydrraw/raw.html', {'info': info})

def data(req, rrdpathname, rrd, ds, rra):
	filename = Rrdpaths.objects.get(name=str(rrdpathname)).path 
	fullfilename = filename + '/' + rrd
	if os.path.isfile(fullfilename):
                rrd = RRD(fullfilename, mode='r')
		info = rrd.getData()
		step = info['step']
		#this should be the pdp maybe
		start = info['lastupdate'] - 100*step
                #data = rrd.fetch(resolution=step, start=start, end=info['lastupdate'])
                data = rrd.fetch(resolution=step, start=start, end=info['lastupdate'])
        	return HttpResponse(simplejson.dumps(data))

def oldgraph(req, rrdpathname, rrd):
	filename = Rrdpaths.objects.get(name=str(rrdpathname)).path 
	fullfilename = filename + '/' + rrd
	if os.path.isfile(fullfilename):
                rrdobj = RRD(fullfilename, mode='r')
                info = rrdobj.getData()
                info['filename'] = filename
		info['rrdpathname'] = str(rrdpathname)
		info['rrd'] = rrd
                return render_to_response('pydrraw/graph.html', {'info': info})
    	#return HttpResponse(full_filename,mimetype="text/plain")


def drawgraph(req, graphid):
	now = int(time.time())
	ginfo = Dgraph.objects.get(pk=graphid)
	gobjects = GraphItems.objects.filter(graph__id=graphid).order_by('seq')
	gitems = []

	start = req.GET.get('start', now - (7 * 86400))
	end = req.GET.get('end', now)

	for gobject in gobjects: #cycle through graph items...need to order this above

            if gobject.itemtype == 'S': #Handle Static RRD DataSources
		rootdir = gobject.rrdds.rootdir.path
		subpath = gobject.rrdds.subpath
		rrdds = gobject.rrdds.ds
		filename = rootdir + '/' + gobject.rrdds.subpath
		rra = gobject.rra
		namesuff = str(gobject.seq)
		legendtext = subpath+" "+rrdds+" "+rra+ " " +str(now)
                gitems.append(DEF(rrdfile=filename, vname='d'+namesuff, dsName=rrdds))
		gitems.append(CDEF(vname='c'+namesuff, rpn='%s' % 'd'+namesuff))
		linetype = gobject.linetype.upper()
		if linetype == 'A':
			gitems.append(AREA(value='c'+namesuff, color=gobject.color, legend=legendtext, stack=gobject.stack))
		elif linetype[:1] == 'L':
			gitems.append(LINE(linetype[-1:], 'c'+namesuff, color=gobject.color, legend=legendtext, stack=gobject.stack))
		else:
			gitems.append(LINE(0, 'c'+namesuff, color=gobject.color, legend=legendtext, stack=gobject.stack))

	    if gobject.itemtype == 'R':  #Handle Regex
	     	regtextarr = gobject.option_text.rsplit(' ',2)
	        rrddslist = Rrdfiles.objects.filter(rootdir__name__regex=regtextarr[0]).filter(subpath__regex=regtextarr[1]).filter(ds__regex=regtextarr[2])
		i = 0

		colors = []
		colorset = GraphItems.COLORS
		for x in colorset:
		     	colors.append(x)

		for rrdds in rrddslist:
			rootdir = rrdds.rootdir.path
			subpath = rrdds.subpath
			rrdds = rrdds.ds
			filename = rootdir + subpath
			#filename = rootdir + '/' + subpath
			rra = gobject.rra
			linetype = gobject.linetype.upper()
			mycolor = colors[i % len(colors)][0]
			namesuff = str(gobject.seq) + '_' + str(i)
			legendtext = subpath+" "+rrdds+" "+rra+ " " +str(now)
                	gitems.append(DEF(rrdfile=filename, vname='d'+namesuff, dsName=rrdds))
			gitems.append(CDEF(vname='c'+namesuff, rpn='%s' % 'd'+namesuff))
			if linetype == 'A':
				gitems.append(AREA(value='c'+namesuff, color=mycolor, legend=legendtext, stack=gobject.stack))
			elif linetype[:1] == 'L':
				gitems.append(LINE(linetype[-1:], 'c'+namesuff, color=mycolor, legend=legendtext, stack=gobject.stack))
			else:
				gitems.append(LINE(0, 'c'+namesuff, color=mycolor, legend=legendtext, stack=gobject.stack))
			prnFmt = '%6.2lf'
			vdef = VDEF(vname='va'+namesuff, rpn='%s,AVERAGE' % ('d'+namesuff) )
			gitems.append(vdef)
			gitems.append(GPRINT(vdef, ('Avg\:'+prnFmt)))
			vdef = VDEF(vname='vn'+namesuff, rpn='%s,MINIMUM' % ('d'+namesuff) )
			gitems.append(vdef)
			gitems.append(GPRINT(vdef, ('Min\:'+prnFmt)))
			vdef = VDEF(vname='vx'+namesuff, rpn='%s,MAXIMUM' % ('d'+namesuff) )
			gitems.append(vdef)
			gitems.append(GPRINT(vdef, ('Max\:'+prnFmt)))
			vdef = VDEF(vname='vl'+namesuff, rpn='%s,LAST' % ('d'+namesuff) )
			gitems.append(vdef)
			gitems.append(GPRINT(vdef, ('LAST\:'+prnFmt+'\\n')))
			#gitems.append(COMMENT('\\n', False))
			i = i + 1

	    if gobject.itemtype == 'C':  #Handle Custom CDEFS
		pass

	    if gobject.itemtype == 'V': #Handle Custom VDEFs
		pass
			

	#make a pyrrd Graph object to add our data to, destination standard out (-)
	g = Graph('-', imgformat='png', start=str(start), end=str(end), vertical_label='"'+ginfo.name+'"')
	#populate it with our url params, defaulting to Dgraph instance (ginfo) options
	fullsizemode = req.GET.get('fullsizemode')
	if (fullsizemode in ['0', 'False' , 'false', 'no', 'No']):
		g.full_size_mode = False
	else:
		g.full_size_mode = True
	graphonly = req.GET.get('graphonly')
	if (graphonly in ['1', 'True' , 'true', 'yes']):
		g.only_graph = True
	noleg = req.GET.get('nolegend')
	if (noleg in ['1', 'True' , 'true', 'yes']):
		g.no_legend = True
	log = req.GET.get('logarithmic')

	if (log in ['1', 'True' , 'true', 'yes', 'Yes']):
		g.logarithmic = True
	elif (log in ['0', 'False' , 'false', 'no', 'No']):
		g.logarithmic = False
	else:
		g.logarithmic = getattr(ginfo, 'logarithmic', False)

	g.height = req.GET.get('height', 600)
	g.width = req.GET.get('width', 1200)
	g.title = '"'+ginfo.name+'"' 
	g.data.extend(gitems)  #write in our gitems we generated
	a = g.write()	#gets the binary image finally
	#minetype = gobject.linetype.value.upper() #just a thing to cause an error and debug
    	return HttpResponse(a,mimetype="image/png")
#  return HttpResponse("failed to retrieve graph objects",mimetype="text/plain")

def dash(req, dashid):
	now = int(time.time())
	dashobj = Dash.objects.get(pk=dashid)
	dobjects = DashItems.objects.filter(dashboard__id=dashid).values('graphid', 'widthratio', 'heightratio', 'seq')
	#dobjects = DashItems.objects.filter(dashboard__id=dashid).values('graphid'
	dinfo = {
	'start' :  (req.GET.get('start', now - (7 * 86400))),
	'end' : int(req.GET.get('end', now)),
	'height' : req.GET.get('height', 200),
	'width' : req.GET.get('width', 300),
	'nolegend' : req.GET.get('nolegend', 1),
	'graphonly' : req.GET.get('graphonly', 1),
	'columns' : req.GET.get('columns', 3),
	}
	return render_to_response('pydrraw/dash.html', {'dobjects': dobjects, 'dinfo': dinfo })



def drawsimplegraph(req, rrdpathname, rrd, ds, rra, height=600, width=1200, start='default', end='default' ):
	filename = Rrdpaths.objects.get(name=str(rrdpathname)).path 
	fullfilename = filename + '/' + rrd
	if os.path.isfile(fullfilename):
                rrdobj = RRD(fullfilename, mode='r')
		info = rrdobj.getData()
		ds = str(ds)
		rra = str(rra)
		#step = info['step']
		if (start == 'default'):
			start = info['lastupdate'] - (7 * 86400)
		if (end == 'default'):
			end = info['lastupdate']
		gitems = []
                gitems.append(DEF(rrdfile=fullfilename, vname="fudge", dsName=ds))
		gitems.append(CDEF(vname='kmh', rpn='%s' % gitems[0].vname))
		gitems.append(AREA(defObj=gitems[1], color='#006600', legend=rrd+" "+str(start)+" "+str(end)))
		g = Graph('-', imgformat='png', start=str(start), end=str(end), vertical_label=ds)
		g.title = rrd
		g.height = req.GET.get('height')
		g.width = req.GET.get('width')
		g.data.extend(gitems)
		a = g.write()
    		return HttpResponse(a,content_type="image/png")
    		#return HttpResponse(dir(g),content_type="text/plain")


