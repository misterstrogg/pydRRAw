from django import forms
from django.contrib import admin
#from django.forms.models import BaseInlineFormSet
#Afrom pydrraw.models import Rrdgraph, GraphItems, Rrdpath, Rrdfiles, Dash, DashItems, DashLayouts, GraphColorScheme
from pydrraw.models import *
from string import Template

#class GraphItemsAdminFormset():
#	def add_fields(self, form, index):
#        	super(GraphItemsAdminFormset, self).add_fields(form, index)
#        	tehfiles = rrdpaths.objects.all()
#        if form.instance:
#            try:        
#                area = form.instance.area
#            except Area.DoesNotExist:
#                pass   
#            else:  
#                tehfiles = Landmark.objects.filter(point__within=area.area)
#        form.fields['tehfile'].queryset = tehfiles


from django.contrib.admin.widgets import AdminFileWidget
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name=str(value)
            output.append(u' <a href="%s" target="_blank"><img src="%s" alt="%s" /></a> %s ' % \
                (image_url, image_url, file_name, _('Change:')))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

class GraphItemColorCycleColorChoice(admin.TabularInline):
	model = GraphItemColorCycleColor
	extra = 2
	class Media:
		js = ('/static/pydrraw/js/jscolor/jscolor.js', )
	def formfield_for_dbfield(self, db_field, **kwargs):
	    if "color" in db_field.name:
		attrs = { 'class': 'color' }
	    	kwargs['widget'] = forms.TextInput(attrs=attrs)
	    return super(GraphItemColorCycleColorChoice,self).formfield_for_dbfield(db_field,**kwargs)



class GraphItemColorCycleAdmin(admin.ModelAdmin):
	inlines = [GraphItemColorCycleColorChoice]

class GraphItemsForm(forms.ModelForm):
	class Meta:
	    model = GraphItems


class GraphItemsChoice(admin.StackedInline):
	model = GraphItems
	extra = 0
	fieldsets = (
        	(None, {
        	    #'classes': ('collapse',),
        	    'fields': (('itemtype', 'rrdds', 'linetype', 'stack', 'color', 'rra', 'seq', 'option_text',),())
        	}),
	)

	class Media:
		js = (
		'/static/pydrraw/js/jscolor/jscolor.js', 
		'/static/pydrraw/js/mycolor.js', 
		#'/static/pydrraw/js/jquery-1.7.2.min.js',
		#'/static/pydrraw/js/jquery.multiselect.filter.min.js', 
		)
	def formfield_for_dbfield(self, db_field, **kwargs):
	    if "color" in db_field.name:
		attrs = { 'class': 'color', 'onClick':'change_class()' }
	    	kwargs['widget'] = forms.TextInput(attrs=attrs)
	    #if db_field.name == 'alttext':
	    #	attrs = { 'class': 'color' }
	    #	kwargs['widget'] = forms.TextArea(attrs=attrs)
	    return super(GraphItemsChoice,self).formfield_for_dbfield(db_field,**kwargs)

class ColorWidget(forms.TextInput):
	class Media:
		js = ('/static/pydrraw/js/jscolor/jscolor.js', )

class RrdgraphAdmin(admin.ModelAdmin):
	readonly_fields=['image_tag',]
	fieldsets = (
        	(None, {
        	    'fields': ('name', 'vertical_label', 'gcolorscheme', 'image_tag')
        	}),
        	('Advanced options', {
        	    'classes': ('collapse', 'grp-collapse grp-closed'),
        	    'fields': ('graph_options','upper_limit','lower_limit','rigid_boundaries','logarithmic','only_graph','alt_autoscale','alt_autoscale_max','no_gridfit','x_grid','y_grid','alt_y_grid','units_exponent','zoom','font','font_render_mode','no_legend','force_rules_legend','tabwidth','base','slope_mode','backend','showdate_start','showdate_end','showdate_now',)
        	}),
	)
	class Media:
		js = ('/static/pydrraw/js/jscolor/jscolor.js', )
	def formfield_for_dbfield(self, db_field, **kwargs):
	    if db_field.name == 'color':
		attrs = { 'class': 'color' }
	    	kwargs['widget'] = forms.TextInput(attrs=attrs)
	    return super(RrdgraphAdmin,self).formfield_for_dbfield(db_field,**kwargs)
	inlines = [GraphItemsChoice]

class GraphColorSchemeAdmin(admin.ModelAdmin):
	class Media:
		js = ('/static/pydrraw/js/jscolor/jscolor.js', )
	def formfield_for_dbfield(self, db_field, **kwargs):
	    if db_field.name.startswith('c'):
		attrs = { 'class': 'color' }
	    	kwargs['widget'] = forms.TextInput(attrs=attrs)
	    return super(GraphColorSchemeAdmin,self).formfield_for_dbfield(db_field,**kwargs)

class RrdfilesChoice(admin.TabularInline):
	model = Rrdfiles
	list_per_page = 10
	extra = 0

class RrdPathsAdmin(admin.ModelAdmin):
	list_per_page = 100
	#inlines = [RrdfilesChoice]	

class DashItemsChoice(admin.TabularInline):
	model = DashItems
	list_per_page = 10
	extra = 0
	def formfield_for_dbfield(self, db_field, **kwargs):
	    if "color" in db_field.name:
	    	kwargs['widget'] = forms.TextInput({ 'class': 'color' })
	    if db_field.name == 'graphurl':
	    	kwargs['widget'] = forms.Textarea(attrs={'rows':2, 'cols':50})
	    if db_field.name == 'alttext':
	    	kwargs['widget'] = forms.Textarea(attrs={'rows':2, 'cols':20})
	    return super(DashItemsChoice,self).formfield_for_dbfield(db_field,**kwargs)

class DashAdmin(admin.ModelAdmin):
    fieldsets = (
        	(None, {
        	    'fields': ('name', 'description', 'timespan', 'columns', 'gcolorscheme',)
        	}),
        	('Advanced options', {
        	    'classes': ('collapse',),
        	    'fields': ('width', 'height', 'hmargin', 'vmargin', 'nolegend', 'graphonly', 'forcecolor', 'serialized_layout')
        	}),
	)
    inlines = [DashItemsChoice]	
    def formfield_for_dbfield(self, db_field, **kwargs):
	    if db_field.name == 'serialized_layout':
	    	kwargs['widget'] = forms.Textarea(attrs={'cols':50})
	    if db_field.name == 'description':
	    	kwargs['widget'] = forms.Textarea(attrs={'cols':50, 'rows':4})
	    return super(DashAdmin,self).formfield_for_dbfield(db_field,**kwargs)


	
# Register your models here.
admin.site.register(Rrdgraph, RrdgraphAdmin)
admin.site.register(Rrdpath, RrdPathsAdmin)
#admin.site.register(DashLayouts)
admin.site.register(Dash, DashAdmin)
admin.site.register(GraphColorScheme, GraphColorSchemeAdmin)
admin.site.register(GraphItemColorCycle, GraphItemColorCycleAdmin)
