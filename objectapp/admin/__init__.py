"""Admin of Objectapp"""
from django.contrib import admin

from objectapp.models import Gbobject

from objectapp.admin.gbobject import GbobjectAdmin



admin.site.register(Gbobject, GbobjectAdmin)

