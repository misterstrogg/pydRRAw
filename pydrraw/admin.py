from django import forms
from django.contrib import admin
#from django.forms.models import BaseInlineFormSet
#from pydrraw.models import Dgraph, GraphItems, Rrdpaths, Rrdfiles, Dash, DashItems, DashLayouts, GraphColorScheme
from pydrraw.models import *

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

class GraphItemsForm(forms.ModelForm):
	class Meta:
		model = GraphItems
#		exclude = ['option_text']

class GraphItemsChoice(admin.TabularInline):
#	fields = ['graph', 'option_type', 'option_text']
	model = GraphItems
#	formset = GraphItemsAdminFormset
	extra = 2
	form = GraphItemsForm

class DgraphAdmin(admin.ModelAdmin):
	inlines = [GraphItemsChoice]
	#fields = ['pub_date', 'name']

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

#class DashTablesChoice(admin.TabularInline):
#	model = DashTables
#	inlines = [DashItemsChoice]
#	list_per_page = 10
#	extra = 0

class DashAdmin(admin.ModelAdmin):
    inlines = [DashItemsChoice]
	
# Register your models here.
admin.site.register(Dgraph, DgraphAdmin)
admin.site.register(Rrdpaths, RrdPathsAdmin)
admin.site.register(DashLayouts)
admin.site.register(Dash, DashAdmin)
admin.site.register(GraphColorScheme)
