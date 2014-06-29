from django.forms import ModelForm
from pydrraw.models import Rrdgraph, GraphItems

class GraphEditForm(ModelForm):
	class Meta:
		model = Rrdgraph
		fields = '__all__'
