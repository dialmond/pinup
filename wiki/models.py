from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from diff_match_patch import diff_match_patch

from accounts.models import User

#pages store the most recent version of a file
class PageBase(models.Model):
    title = models.CharField(max_length=100, null=True)
    slug = models.SlugField(max_length=115, blank=True, null=True)

    created_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        abstract = True

class Page(PageBase):
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="child")
    content = models.TextField(blank=True)#MarkdownxField(default="", max_length="10000", blank=True)
    file = models.FileField(upload_to='uploads', blank=True)
    class protection_choices(models.TextChoices):
        NO = 'NO', _('None') #all signed in users can edit
        LO = 'LO', _('Locked') #only created_by user can edit
        NC = 'NC', _('Locked and doesn\'t allow children') #only created_by user can edit, and prevents children from being created

    protection = models.CharField(
        help_text="Setting the protection to 'locked' will not allow others to edit this page in the future.",
        max_length=2,
        choices=protection_choices.choices,
        default=protection_choices.NO,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields= ['parent','title'], name='unique_page_title'),
            models.UniqueConstraint(fields= ['parent','slug'], name='unique_page_slug'),
        ]
        ordering = ['title']

    def get_absolute_url(self):
        if self.parent:
            return self.parent.get_absolute_url() + '/' + self.slug
        else:
            return '/' + self.slug

    def get_url(self):
        #this isn't an absolute url path, because it misses the first '/',
        #but it's used in the urls
        return self.get_absolute_url()[1:]

    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        if not self.id: # we're creating this for the first time
            if not self.slug:
                self.slug = slugify(self.title)
        super(Page, self).save(*args, **kwargs)

    @property
    def get_latest_revision(self):
        try:
            return Revision.objects.filter(page__id=self.id, latest=True).get()
        except:
            return None

    @property
    def edit_date(self):
        revision = self.get_latest_revision
        if revision:
            return revision.created_date
        return self.created_date

    def revert(self, count=0):
        dmp = diff_match_patch()
        modified_fields = set()
        for i in range(count+1): #so we can start at 0, I like that
            revision = self.get_latest_revision
            fields = ['slug', 'parent', 'title', 'created_date', 'created_by']
            #fields = ['slug', 'title', 'created_date', 'created_by']
            for field in fields: #set the relevant fields
                value = getattr(revision, field)
                if value is not None:
                    if value != getattr(self, field):
                        modified_fields.add(Page._meta.get_field(field).verbose_name)
                    self.__setattr__(field, value)
            if self.content and revision.patch:
                modified_fields.add(Page._meta.get_field('content').verbose_name)
                patches = dmp.patch_fromText(revision.patch)
                new_content, _ = dmp.patch_apply(patches, self.content)
                self.content = new_content
            if revision.parent != None and revision.parent != self.parent:
                self.parent = revision.parent
            prev_revision = revision.get_previous
            if prev_revision:
                prev_revision.latest = True; prev_revision.save()
            revision.delete()
            #make the previous revision the new latest one, if there is one
            self.save()
        if Page._meta.get_field('content').verbose_name not in modified_fields:
            modified_fields.add(Page._meta.get_field('title').verbose_name)
            #^since revisions are only created when we change content or title, then there
            #must've been a title change
        success_msg = f"reverted fields: {', '.join(sorted(list(modified_fields)))}"
        return success_msg

    def delete(self, *args, **kwargs):
        if self.file:
            self.file.delete()
        super().delete(*args, **kwargs)


#used to go from the current version to the previous version
class Revision(PageBase):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="revision")
    parent = models.ForeignKey(Page, null=True, blank=True, on_delete=models.SET_NULL, related_name="revisions_parent") #where the file WAS saved at this time
    #if this is null, then it either has no parent or it has the same parent
    edit_number = models.PositiveSmallIntegerField(default=0)
    edit_summary = models.CharField(max_length=255, blank=True, null=True)
    latest = models.BooleanField(default=False)

    patch = models.TextField(null=True)

    class Meta:
        ordering = ['-latest', '-created_date']
        constraints = [
            models.UniqueConstraint(fields= ['parent','edit_number'], name='unique_edit_number'),
        ]

    @property
    def get_previous(self):
        if self.edit_number and self.edit_number > 0:
            return Revision.objects.filter(edit_number = self.edit_number - 1)[0]
        else:
            return None

    #returns how many times we have to call revert on page to get to this revision
    #returns negative if revision doesn't belong to page (shouldn't happen if done correctly)
    def get_revert_count(self, page):
        if self.page != page:
            return -1
        return page.get_latest_revision.edit_number - self.edit_number

    def __str__(self):
        s = f"Edit #{self.edit_number +1}" + ", " + self.created_date.strftime("%b. %d, %Y, %H:%m")
        if self.created_by:
            s += ", by " + str(self.created_by)
        else:
            s += ", deleted user"
        return s

    def save(self, *args, **kwargs):
        if not self.id: # we're creating this for the first time
            if self.title and not self.slug:
                self.slug = slugify(self.title)
        super(Revision, self).save(*args, **kwargs)
