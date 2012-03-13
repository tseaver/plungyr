from pyramid.view import view_config
from .models import Plungyr

@view_config(context=Plungyr, renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project':'plungyr'}
