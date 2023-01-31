from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.contrib import messages

from .models import Page, Revision
from accounts.models import User
from .forms import *
from django.forms.models import model_to_dict
from django.utils.text import slugify
from django.utils.html import mark_safe
from diff_match_patch import diff_match_patch

def validate_page(page_path):
    pages = page_path.split("/")
    pages = [p for p in pages if p]
    parent = None
    for slug in pages:
        page = get_object_or_404(Page, parent=parent, slug=slug)
        parent = page
    return {"page": page}

def get_link_html(page):
    url = reverse('wiki:detail', kwargs={'page_path': page.get_url()})
    text = page.title if not page.file else f'📄 {page.title}'
    return mark_safe(f'<a href="{url}">{text}</a>')

def traverse_pages(root):
    #print(f'the root is {root.title}')
    if root.child.all():
        children = []
        for child in root.child.all():
            traversal = traverse_pages(child)
            if isinstance(traversal, tuple):
                for thing in traverse_pages(child):
                    children.append(thing)
            else:
                children.append(traversal)
        return get_link_html(root), children
    return get_link_html(root)

class IndexView(generic.ListView):
    template_name = 'wiki/index.html'
    context_object_name = 'pages'

    def get_queryset(self):
        #return Page.objects.order_by('-edit_date')
        #return sorted(Page.objects.all(),  key=lambda p: p.edit_date)
        #return sorted(Page.objects.all(), key=lambda m: m.title)
        pages = []
        page_roots = Page.objects.filter(parent = None)
        for root in page_roots:
            traversal = traverse_pages(root)
            if isinstance(traversal, tuple):
                for thing in traversal:
                    pages.append(thing)
            else:
                pages.append(traversal)
        #ok, so I know i fucked up my recursion because I reused code here and in traverse_pages, but whatever, I'm done with this
        return pages


def detail(request, page_path):
    context = validate_page(page_path)
    return render(request, 'wiki/detail.html', context)

def create_helper(request, page_path, upload=False):
    context = {}
    if page_path:
        context = validate_page(page_path)
        page = context['page']
        if not(page.protection != "NC" or page.protection == "NC" and page.created_by == request.user):
            messages.error(request, "The page's parent, %s, doesn't allow children to be created here." %(page.title))
            return HttpResponseRedirect(reverse('wiki:detail', kwargs={'page_path': page.get_url()}))
    form = PageForm() if not upload else PageFileForm()
    if request.method == "POST":
        form = PageForm(request.POST) if not upload else PageFileForm(request.POST, request.FILES)
        if form.is_valid():
            new_page = form.save(commit=False)
            if page_path:
                new_page.parent = page
            new_page.created_by = request.user
            new_page.save()
            messages.success(request, "Successfully added the page %s" %(new_page.title))
            return HttpResponseRedirect(reverse('wiki:detail', kwargs={'page_path': new_page.get_url()}))
        else:
            messages.error(request, "Form is invalid. Please correct the errors below.")
    context['create'] = True #for template reasons
    context['form'] = form
    return render(request, 'wiki/form.html', context)

def create(request, page_path=None):
    return create_helper(request, page_path)
def upload(request, page_path=None):
    return create_helper(request, page_path, upload=True)

'''
Revision system: Revisions are created in the update thingy ONLY IF the content OR title is changed.
So in this case we do make the changes to the page, we just also generate a revision that contains a patch to get from new content to old content, then mark it as latest (make the other ones not the latest), and foreign key it to the new page

No matter what we do, we update/save the page as usual (we just might also create a revision in the process)
'''
'''
OLD, BAD, DECREPIT: new code looks very similar but instead contains the information for the PREVIOUS version, not the changed/current version
def create_revision(request, page, data, form):
    for r in page.revision.all():
        r.latest = False
        r.save()
    revision = Revision(page=page, edit_number=len(page.revision.all()), latest=True)
    if 'title' in form.changed_data:
        revision.title = form.title
        new_slug = slugify(form.title)
        if new_slug != data['slug']: revision.slug = new_slug
    if 'content' in form.changed_data:
        dmp = diff_match_patch()
        #patches = dmp.patch_make(data['content'], form.cleaned_data["content"])
        patches = dmp.patch_make(form.cleaned_data['content'], data["content"])
        revision.patch = dmp.patch_toText(patches)
    #if page.created_by != request.user:
    revision.created_by = request.user
    revision.save()
'''

def create_revision(request, page, data, form):
    #print(form)
    for r in page.revision.all():
        r.latest = False
        r.save()
    revision = Revision(page=page, edit_number=len(page.revision.all()), latest=True)
    if 'title' in form.changed_data:
        revision.title = data['title']
        new_slug = slugify(form.cleaned_data['title'])
        if new_slug != data['slug']: revision.slug = data['slug']
    if 'content' in form.changed_data:
        dmp = diff_match_patch()
        patches = dmp.patch_make(form.cleaned_data['content'], data['content'])
        revision.patch = dmp.patch_toText(patches)
    revision.created_by = User.objects.get(id=data['created_by'])
    revision.save()

def update(request, page_path):
    context = validate_page(page_path)
    page = context['page']
    data = model_to_dict(page)
    if not(page.protection == "NO" or page.protection in ["LO", "NC"] and request.user == page.created_by):
        messages.error(request, "You don't have permission to edit this page!")
        return HttpResponseRedirect(reverse('wiki:detail', kwargs={'page_path': page.get_url()}))
    form = PageForm(instance = page) if page.content else PageFileForm(instance = page)
    if request.method == "POST":
        if page.content:
            form = PageForm(request.POST, instance=page, initial=data)
        else:
            form = PageFileForm(request.POST, request.FILES, instance=page, initial=data)
        if form.is_valid():
            if 'content' or 'title' in form.changed_data: #create a revision
                create_revision(request, page, data, form)
            form.save()
            messages.success(request, "Updated page")
            return HttpResponseRedirect(reverse('wiki:detail', kwargs={'page_path': page.get_url()}))
    context['form'] = form if page.content else form.render("wiki/update_form_snippet.html")
    return render(request, 'wiki/form.html', context)

def user_can_delete(request, page):
    for r in page.revision.all(): #pages can only be deleted if the user is the only one that has worked on it
        if r.created_by != request.user:
            return False
    for c in page.child.all(): #this stipulation also applies to their children, as well
        for r in c.revision.all():
            if r.created_by != request.user:
                return False
    return True

def delete(request, page_path):
    context = validate_page(page_path)
    page = context['page']
    parent = page.parent
    if user_can_delete(request, page):
        if request.method =="POST":
            title = page.title
            page.delete()
            messages.success(request, "Successfully deleted the page %s." %(title))
            if parent:
                return HttpResponseRedirect(reverse('wiki:detail', kwargs={'page_path' : parent.get_url()}))
            return HttpResponseRedirect(reverse('wiki:index'))
    else:
        messages.error(request, "You do not have permission to delete this page!")
        messages.info(request, "Pages that have had other contributors cannot be deleted. If you'd like to have this page deleted, for now contact an admin?")
        return HttpResponseRedirect(reverse('wiki:detail', kwargs={'page_path' : page.get_url()}))
    return render(request, 'wiki/delete.html', context)

def revert(request, page_path, edit_number):
    context = validate_page(page_path)
    page = context['page']
    if page.protection != "NO" and request.user != page.created_by:
        messages.error(f'Contact {page.created_by} to unlock this page first')
        return HttpResponseRedirect(reverse('wiki:detail', kwargs={'page_path' : page.get_url()}))
    revision = get_object_or_404(Revision, page=page, edit_number=edit_number)
    revert_count = revision.get_revert_count(page)
    if revert_count < 0:
        messages.error(request, "cannot revert to this version. xkcd 2220")
    else:
        success_msg = page.revert(revert_count)
        messages.success(request, success_msg)
    return HttpResponseRedirect(reverse('wiki:detail', kwargs={'page_path' : page.get_url()}))

def history(request, page_path):
    context = validate_page(page_path)
    page = context['page']
    latest = page.get_latest_revision
    if latest:
        versions = []
        revisions = page.revision.all()
        dmp = diff_match_patch()
        content = page.content
        #for i in range(latest.edit_number, -1, -1):
        for revision in revisions:
            #revision = revisions.get(edit_number=i) #is this not O(n^2)?
            if revision.patch:
                previous, _ = dmp.patch_apply(dmp.patch_fromText(revision.patch), content)
                #diff = dmp.diff_main(content, previous)
                #diffhtml = dmp.diff_prettyHtml(diff)
                content = previous
            versions.append((revision, content))
        context['versions'] = versions
    return render(request, 'wiki/history.html', context)
