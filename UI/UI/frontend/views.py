from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    html = "<html><body>Hello wollolo</body></html>"
    return HttpResponse(html)
# return render(request,'home.html',context)
# render page(template(home.html)) with some request(get/post/..), populate with data in context