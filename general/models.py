from tkinter import CASCADE
from django.db import models
from django.db.models import When, Exists
from django.contrib.auth.models import Group
from back_office.models import *
from django.utils.translation import gettext_lazy as _


class Folder(models.Model):
    class ContentType(models.TextChoices):
        ROOT = "GL", _("GLOBAL")
        DOMAIN = "DO", _("DOMAIN")
    name = models.CharField(max_length=200, default=_("<Group title>"), verbose_name=_("Name"))
    # childrenClassName
    description = models.CharField(
        max_length=100, default=_("<Short description>"), 
        blank=True, null=True, verbose_name=_("Description"))
    content_type = models.CharField(max_length=2, choices=ContentType.choices, default=ContentType.DOMAIN)
    parent_folder = models.ForeignKey("self", null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Folder")
        verbose_name_plural = _("Folders")

    def __str__(self):
        return self.name

    @classmethod
    def create(cls, name):
        folder = Folder.objects.create(name=name, parent_folder=Folder.objects.get(name="root"))
        auditors = UserGroup.objects.create(name= name + " Auditors", folder = folder)
        analysts = UserGroup.objects.create(name= name + " Analysts", folder = folder)
        managers = UserGroup.objects.create(name= name + " Domain Managers", folder = folder)
        ra1 = RoleAssignment.objects.create(isUserGroup = True, userGroup = auditors, role = Role.objects.get(name="Auditor"))
        ra1.folders.add(folder)
        ra2 = RoleAssignment.objects.create(isUserGroup = True, userGroup = analysts, role = Role.objects.get(name="Analyst"))
        ra2.folders.add(folder)
        ra3 = RoleAssignment.objects.create(isUserGroup = True, userGroup = managers, role = Role.objects.get(name="Domain Manager"))
        ra3.folders.add(folder)
        return cls(name=name)


class Project(models.Model):
    PRJ_LC_STATUS = [
        ('undefined', _('--')),
        ('in_design', _('Design')),
        ('in_dev', _('Development')),
        ('in_prod', _('Production')),
        ('eol', _('End Of Life')),
        ('dropped', _('Dropped')),

    ]
    name = models.CharField(max_length=200, default=_("<short project name>"), verbose_name=_("Project Name"))
    internal_id = models.CharField(max_length=100, default=_("<if an internal reference applies>"), 
        null=True, blank=True, verbose_name=_("Internal ID"))
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, verbose_name=_("Domain"))
    lc_status = models.CharField(max_length=20, default='in_design', 
        choices=PRJ_LC_STATUS, verbose_name=_("Status"))
    summary = models.TextField(max_length=1000, blank=True, null=True, 
        default=_("<brief summary of the project>"),
        help_text=_("This summary is optional and will appear in the risk analysis for context"),
        verbose_name=_("Summary"))
    
    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    def description(self):
        return self.folder.description
    description.short_description = _("Description")

    def __str__(self):
        return self.name


class ParentRisk(models.Model):
    title = models.CharField(max_length=200, default=_("<threat short title>"), verbose_name=_("Title"))
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, blank=True)
    isPublished = models.BooleanField(_('published'), default=False)

    class Meta:
        verbose_name = _("Threat")
        verbose_name_plural = _("Threats")

    def __str__(self):
        return self.title


class Asset(models.Model):
    class Meta:
        verbose_name_plural = _("Assets")
        verbose_name = _("Asset")
    
    name = models.CharField(max_length=100, verbose_name=_('name'))
    business_value = models.TextField(blank=True, verbose_name=_('business value'))
    comments = models.TextField(blank=True, verbose_name=_('comments'))
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, blank=True)
    isPublished = models.BooleanField(_('published'), default=False)

    def __str__(self):
        return self.name


class Solution(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    provider = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Provider"))
    contact = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Contact"))
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, blank=True)
    isPublished = models.BooleanField(_('published'), default=False)

    class Meta:
        verbose_name = _("Solution")
        verbose_name_plural = _("Solutions")

    def __str__(self):
        return self.name


class GroupExtra(models.Model):
    """
    Overwrites original Django Group.
    """

    def __str__(self):
        return "{}".format(self.group.name)

    group = models.OneToOneField('auth.Group', unique=True, on_delete=models.CASCADE)
    group_email = models.EmailField(max_length=70, blank=True, default="", 
        help_text=_("Group email for notifications"),
        verbose_name=_("Group email"))
    prj_groups = models.ManyToManyField(Folder, blank=True, 
        verbose_name=_("Allowed Projects Groups"), 
        help_text=_("Project groups allowed for read access on the Portal. "))

