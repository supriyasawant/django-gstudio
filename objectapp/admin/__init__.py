"""Admin of Objectapp"""
from django.contrib import admin

from objectapp.models import Gbobject
from objectapp.models import Process
from objectapp.models import System

from objectapp.admin.gbobject import GbobjectAdmin
from objectapp.admin.process import ProcessAdmin
from objectapp.admin.system import SystemAdmin

admin.site.register(Gbobject, GbobjectAdmin)
admin.site.register(Process, ProcessAdmin)
admin.site.register(System, SystemAdmin)

