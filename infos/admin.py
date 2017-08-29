from django.contrib import admin

from infos.models import School, Subject, ClassLevel, District, Rating, Notify

admin.site.register(School)
admin.site.register(Subject)
admin.site.register(ClassLevel)
admin.site.register(District)
admin.site.register(Rating)
admin.site.register(Notify)
