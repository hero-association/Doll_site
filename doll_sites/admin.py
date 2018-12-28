from django.contrib import admin

# Register your models here.

from doll_sites.models import Series,Photo,PhotoFile,PhotoLink,Tag,Company


class PhotoFileInline(admin.TabularInline):
	model = PhotoFile

class PhotoLinkInline(admin.TabularInline):
	model = PhotoLink	

# Define the admin class
class PhotoAdmin(admin.ModelAdmin):
	list_display = ('id','series','company','name','name_chinese','actress_name','date_added')
	list_editable = ('actress_name','company',)
	inlines = [PhotoFileInline,PhotoLinkInline]
	list_filter = ('series','company','actress_name',)
	# search_field = ('series') #添加快速查询栏

class PhotoInline(admin.TabularInline):
	model = Photo

class SeriesAdmin(admin.ModelAdmin):
	list_display = ('id','text','date_added')
	inlines = [PhotoInline]

class CompanyAdmin(admin.ModelAdmin):
	list_display = ('company_name',)

class TagAdmin(admin.ModelAdmin):
	list_display = ('tag_name',)

# Register the admin class with the associated model
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(PhotoFile)
admin.site.register(PhotoLink)