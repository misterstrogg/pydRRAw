from django.forms import ModelForm
from pydrraw.models import Dgraph, GraphItems

class GraphEditForm(ModelForm):
	class Meta:
		model = Dgraph
		fields = '__all__'
