# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404, render
from django.template import RequestContext
from django.core.urlresolvers import reverse
import os
import re
from pyrrd.rrd import DataSource, RRA, RRD
from pyrrd.graph import DEF, CDEF, VDEF, LINE, AREA, GPRINT, Graph, COMMENT, ColorAttributes
import simplejson
#import json
from pydrraw.models import *
from django.views import generic
import time
from sets import Set
from django.forms import ModelForm, TextInput
from django.forms.models import inlineformset_factory
from django.db import transaction

#rrdPath = 'DjangoRRD/public/rrds/'
#rrdPath = '/usr/var/lib/collectd/rrd/worm.circuit5.com/memory/'
class GraphDetailView(generic.ListView):
    #model = dGraph
    template_name = 'pydrraw/graphdetail.html'
    context_object_name = 'graph'
    def get_queryset(self):
        self.graph = get_object_or_404(Rrdgraph, name="yo")
        return GraphItems.objects.filter(graph=self.graph)
    def get_context_data(self, **kwargs):
	context = super(GraphDetailView, self).get_context_data(**kwargs)
	context['graph'] = self.graph
	return context

def paths(req, rrdpathname):
	rrdpaths = RRDpaths.objects.all()
	return render_to_response('pydrraw/paths.html', {'rrdpaths': rrdpaths})
	

def list(req, rrdpathname):
        if (rrdpathname == "all"):
	        rrds = Rrdfiles.objects.all()
	else:
		rrds = Rrdfiles.objects.filter(rootdir__name=rrdpathname)
	return render_to_response('pydrraw/list.html', {'rrds': rrds, 'rrdpathname': rrdpathname})


def infoview(req, rrdpathname, rrd):
	filename = Rrdpath.objects.get(name=str(rrdpathname)).path 
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
	filename = Rrdpath.objects.get(name=str(rrdpathname)).path 
	fullfilename = filename + '/' + rrd
	if os.path.isfile(fullfilename):
                myrrd = RRD(fullfilename, mode='r')
                info = myrrd.getData()
		info['rrdpathname'] = rrdpathname
		info['rrd'] = rrd
		info['filename'] = filename
        	return render_to_response('pydrraw/raw.html', {'info': info})

def data(req, rrdpathname, rrd, ds, rra):
	filename = Rrdpath.objects.get(name=str(rrdpathname)).path 
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
	filename = Rrdpath.objects.get(name=str(rrdpathname)).path 
	fullfilename = filename + '/' + rrd
	if os.path.isfile(fullfilename):
                rrdobj = RRD(fullfilename, mode='r')
                info = rrdobj.getData()
                info['filename'] = filename
		info['rrdpathname'] = str(rrdpathname)
		info['rrd'] = rrd
                return render_to_response('pydrraw/graph.html', {'info': info})
    	#return HttpResponse(full_filename,mimetype="text/plain")
def secsago(req):
	seconds = int(req.GET.get('seconds', 0))
	minutes = int(req.GET.get('minutes', 0))
	hours = int(req.GET.get('hours', 0))
	days = int(req.GET.get('days', 0))
	weeks = int(req.GET.get('weeks', 0))
	months = int(req.GET.get('months', 0))
	years = int(req.GET.get('years', 0))
	timelagratio = req.GET.get('timelagratio', 1)
	secsago = (seconds + (minutes*60) + (hours*60*60) + (days*24*3600) + (weeks*7*24*3600) + (months*30*24*3600) + (years*365*24*3600))

	secsago = timelagratio * secsago
	return int(secsago)

def drawgraph(req, graphid):
	now = int(time.time())
	ginfo = Rrdgraph.objects.get(pk=graphid)
	gobjects = GraphItems.objects.filter(graph__id=graphid).order_by('seq')
	gitems = []
	secondsago = secsago(req)
	if secondsago == 0:
		secondsago = 3600
	#	secsago = ginfo.timespan
	
	end = int(req.GET.get('end', now))
	start = int(req.GET.get('start', end - secondsago))


	for gobject in gobjects: #cycle through graph items...need to order this above

            if gobject.itemtype == 'S': #Handle Static RRD DataSources
		rootdir = gobject.rrdds.rootdir.path
		subpath = gobject.rrdds.subpath
		rrdds = gobject.rrdds.ds
		filename = rootdir + '/' + gobject.rrdds.subpath
		rra = gobject.rra
		namesuff = str(gobject.seq)
		legendtext = subpath+" "+rrdds+" "+rra+ " "
                gitems.append(DEF(rrdfile=filename, vname='d'+namesuff, dsName=rrdds))
		gitems.append(CDEF(vname='c'+namesuff, rpn='%s' % 'd'+namesuff))
		linetype = gobject.linetype.upper()
		mycolor = '#' + gobject.color + gobject.transparency
		if linetype == 'A':
			gitems.append(AREA(value='c'+namesuff, color=mycolor, legend=legendtext, stack=gobject.stack))
		elif linetype[:1] == 'L':
			gitems.append(LINE(linetype[-1:], 'c'+namesuff, color=mycolor, legend=legendtext, stack=gobject.stack))
		else:
			gitems.append(LINE(0, 'c'+namesuff, color=mycolor, legend=legendtext, stack=gobject.stack))

	    if gobject.itemtype == 'R':  #Handle Regex
	     	regtextarr = gobject.option_text.rsplit(' ',2)
	        rrddslist = Rrdfiles.objects.filter(rootdir__name__regex=regtextarr[0]).filter(subpath__regex=regtextarr[1]).filter(ds__regex=regtextarr[2])
		i = 0

		colors = []
		colorset = GraphItemColorCycleColor.objects.filter(name='weeee').order_by('seq')
		for x in colorset:
		     	colors.append(str('#' + x.color))

		for rrdds in rrddslist:
			rootdir = rrdds.rootdir.path
			subpath = rrdds.subpath
			rrdds = rrdds.ds
			filename = rootdir + subpath
			rra = gobject.rra
			linetype = gobject.linetype.upper()
			mycolor = colors[i % len(colors)]
			namesuff = str(gobject.seq) + '_' + str(i)
			legendtext = subpath+" "+rrdds+" ("+rra+ ") "
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
	cs = req.GET.get('cs', ginfo.gcolorscheme)
	colsch = GraphColorScheme.objects.get(pk=cs)
   	ca = ColorAttributes()
   	ca.back = '#' + colsch.cback + colsch.tback
   	ca.canvas = '#' + colsch.ccanvas + colsch.tcanvas
   	ca.shadea = '#' + colsch.cshadea + colsch.tshadea
   	ca.shadeb = '#' + colsch.cshadeb + colsch.tshadeb
   	ca.mgrid = '#' + colsch.cmgrid + colsch.tmgrid
   	ca.axis = '#' + colsch.caxis + colsch.taxis
   	ca.frame = '#' + colsch.cframe + colsch.tframe
   	ca.font = '#' + colsch.cfont + colsch.tfont
   	ca.arrow = '#' + colsch.carrow + colsch.tarrow
	#make a pyrrd Graph object, destination standard out (-)
	g = Graph('-', imgformat='png', start=start, end=end, color=ca, vertical_label='"'+ginfo.vertical_label+'"')
	#populate it with our url params, defaulting to Rrdgraph instance (ginfo) options
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
	g.disable_rrdtool_tags = True
	g.height = req.GET.get('height', 600)
	g.width = req.GET.get('width', 1200)
	g.title = '"'+ginfo.name+'"' 
	g.data.extend(gitems)  #write in our gitems we generated
	a = g.write()	#gets the binary image finally
	#minetype #just a thing to cause an error and debug
    	return HttpResponse(a,mimetype="image/png")
#  return HttpResponse("failed to retrieve graph objects",mimetype="text/plain")
def dash2(req, dashid):
	now = int(time.time())
	dashobj = Dash.objects.get(pk=dashid)
	dobjects = DashItems.objects.filter(dashboard__id=dashid).values('graphid', 'type', 'widthratio', 'heightratio', 'seq', 'timelagratio', 'alttext').order_by('seq')	

	#handle time shorthand
	secondsago = secsago(req)
	if secondsago <= 0:
		secondsago = dashobj.timespan
	end = int(req.GET.get('end', now))
	start = int(req.GET.get('start', end - secondsago))
	dinfo = {
	'start' : start,
	'end' : end,
	#get rest of info from dash object, allow url override
	'width' : req.GET.get('width', dashobj.width),
	'height' : req.GET.get('height', dashobj.height),
	'nolegend' : req.GET.get('nolegend', dashobj.nolegend),
	'graphonly' : req.GET.get('graphonly', dashobj.graphonly),
	'columns' : req.GET.get('columns', dashobj.columns),
	'title' : req.GET.get('title', dashobj.name),
	'desc' : req.GET.get('desc', dashobj.description),
	'forcecolor' : req.GET.get('forcecolor', dashobj.forcecolor),
	'cs' : req.GET.get('cs', dashobj.gcolorscheme),
	'serialized_layout' : req.GET.get('cl', dashobj.serialized_layout),
	}
	csobj = GraphColorScheme.objects.get(pk=dinfo['cs'])
	return render_to_response('pydrraw/dash2.html', {'dobjects': dobjects, 'dinfo': dinfo, 'csobj': csobj })

def dash(req, dashid):
	now = int(time.time())
	dashobj = Dash.objects.get(pk=dashid)
	dobjects = DashItems.objects.filter(dashboard__id=dashid).values('graphid', 'type', 'widthratio', 'heightratio', 'seq', 'timelagratio', 'graphurl', 'alttext').order_by('seq')	

	#handle time shorthand
	secondsago = secsago(req)
	if secondsago <= 0:
		secondsago = dashobj.timespan
	end = int(req.GET.get('end', now))
	start = int(req.GET.get('start', end - secondsago))
	dinfo = {
	'id' : dashobj.id,
	'start' : start,
	'end' : end,
	#get rest of info from dash object, allow url override
	'width' : req.GET.get('width', dashobj.width),
	'height' : req.GET.get('height', dashobj.height),
	'hmargin' : req.GET.get('width', dashobj.hmargin),
	'vmargin' : req.GET.get('height', dashobj.vmargin),
	'nolegend' : req.GET.get('nolegend', dashobj.nolegend),
	'graphonly' : req.GET.get('graphonly', dashobj.graphonly),
	'columns' : req.GET.get('columns', dashobj.columns),
	'title' : req.GET.get('title', dashobj.name),
	'desc' : req.GET.get('desc', dashobj.description),
	'forcecolor' : req.GET.get('forcecolor', dashobj.forcecolor),
	'cs' : req.GET.get('cs', dashobj.gcolorscheme),
	'serialized_layout' : req.GET.get('cl', dashobj.serialized_layout),
	}
	csobj = GraphColorScheme.objects.get(pk=dinfo['cs'])
	return render_to_response('pydrraw/dash.html', {'dobjects': dobjects, 'dinfo': dinfo, 'csobj': csobj })

def drawsimplegraph(req, rrdpathname, rrd, ds, rra, height=600, width=1200, start='default', end='default' ):
	filename = Rrdpath.objects.get(name=str(rrdpathname)).path 
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
		g.title = rrd + '/' +  ds + '/' + rra
		g.full_size_mode = True
		g.only_graph = req.GET.get('onlygraph', False)
		g.no_legend = req.GET.get('nolegend', True)
		g.height = req.GET.get('height', 600)
		g.width = req.GET.get('width', 1200)
		g.data.extend(gitems)
		a = g.write()
    		return HttpResponse(a,content_type="image/png")

class EditGraphItemForm(ModelForm):
	class Meta:
		model = GraphItems
		fields = '__all__'

	
class EditGraphForm(ModelForm):
	class Meta:
		model = Rrdgraph
		fields = '__all__'

def addgraph(req, graphid):
        form = EditGraphForm(req.POST or None)
    	return render(req, 'pydrraw/editgraph.html', { 'form': form, })
	

def editgraph(req, graphid=None):
    if graphid:
		ginfo = get_object_or_404(Rrdgraph, pk=graphid)
    else:
		ginfo = Rrdgraph()
    if req.method == 'POST': 
        form = EditGraphForm(req.POST, instance=ginfo)
	#formset = GraphItemFormSet(instance=ginfo)
        if form.is_valid(): 
	    gobject = form.save()
    	    GraphItemFormSet = inlineformset_factory(Rrdgraph, GraphItems, extra=1)
	    formset = GraphItemFormSet(req.POST, instance=gobject)
       	    if formset.is_valid(): 
		formset.instance = gobject
		formset.save()
		transaction.commit()
		status = 'Saved!'
		return HttpResponseRedirect('')
	    else:
		status = 'Formset failed to validate!'
	else:
	    status = 'Form failed to validate!'
    else:
        form = EditGraphForm(instance=ginfo)
    	GraphItemFormSet = inlineformset_factory(Rrdgraph, GraphItems, extra=2, widgets={'color': TextInput(attrs={'class':'color'})})
	#formset = GraphItemFormSet(instance=Rrdgraph(graphid))
	formset = GraphItemFormSet(instance=ginfo)
	status = 'Unsaved'
    return render_to_response('pydrraw/editgraph.html', {'form': form, 'formset': formset, 'graphid':graphid, 'status':status, }, context_instance=RequestContext(req))


