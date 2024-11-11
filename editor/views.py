

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Document

def home(request):
    return redirect('document_list')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'editor/register.html', {'form': form})

@login_required
def document_list(request):
    documents = Document.objects.filter(owner=request.user)
    return render(request, 'editor/document_list.html', {'documents': documents})

@login_required
def document_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            document = Document.objects.create(title=title, owner=request.user)
            return redirect('document_detail', pk=document.pk)
        else:
            error = 'Title is required.'
            return render(request, 'editor/document_create.html', {'error': error})
    else:
        return render(request, 'editor/document_create.html')


@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if document.owner != request.user:
        return redirect('document_list')
    return render(request, 'editor/document_detail.html', {'document': document})