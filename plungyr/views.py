from pyramid.view import view_config
from pyramid.url import resource_url

from .models import Plungyr

@view_config(context=Plungyr, renderer='templates/mytemplate.pt')
def plungyr_main(context, request):
    return {'purl': resource_url(context, request)}
