from django.contrib import admin

# Register your models here.

from doll_sites.models import Series,Photo,PhotoFile,PhotoLink,Tag,Company,Actress,SiteConfig,Order,UserProfile,UserAlbumPaidRecord,MemberConfig


class PhotoFileInline(admin.TabularInline):
	model = PhotoFile

class PhotoLinkInline(admin.TabularInline):
	model = PhotoLink	

# Define the admin class
class PhotoAdmin(admin.ModelAdmin):
	search_fields = ['name_chinese']
	list_display = ('id','series','company','name','name_chinese','date_added','views_count')
	list_editable = ('company','name','name_chinese',)
	inlines = [PhotoFileInline,PhotoLinkInline]
	list_filter = ('series','company','vip_photo','model_name')

	# radio_fields = {"model_name": admin.HORIZONTAL}
	filter_horizontal = ['photo_tag','model_name']
	save_on_top = True
	fieldsets = (
        ('Basic', {
            'fields': ('series', 'company', 'model_name', )
        }),
        ('Info', {
            'fields': ('name', 'name_chinese','photo_tag')
        }),
        ('Pay', {
            'fields': ('vip_photo', 'buy_link','buy_price','buy_content','vip_bundle','bundle_link','bundle_price','bundle_content')
        }),
        # ('photos', {
        #     'classes': ('collapse',),
        #     'fields': ('registration_required', 'template_name'),
        # }),
    )
	# search_field = ('series') #添加快速查询栏

class PhotoFileAdmin(admin.ModelAdmin):
	list_display = ('id','model_name',)
	list_filter = ('model_name')

class PhotoInline(admin.TabularInline):
	model = Photo

class SeriesAdmin(admin.ModelAdmin):
	list_display = ('id','text','date_added')
	inlines = [PhotoInline]

class CompanyAdmin(admin.ModelAdmin):
	list_display = ('company_name',)

class TagAdmin(admin.ModelAdmin):
	list_display = ('tag_name',)

class OrderAdmin(admin.ModelAdmin):
	model = Order
	list_display = ('order_id','user_name','order_info','order_status','order_price','paid_price','date_created','date_update')
	list_filter = ('order_status',)

class ActressAdmin(admin.ModelAdmin):
	list_display = ('actress_name_ch','actress_name_jp','actress_name_en')

class SiteConfigAdmin(admin.ModelAdmin):
	list_display = ('config_name','config_value')
	list_editable = ('config_value',)

class MemberConfigAdmin(admin.ModelAdmin):
	list_display = ('config_name','config_value')
	list_editable = ('config_value',)

# Register the admin class with the associated model
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Actress,ActressAdmin)
admin.site.register(PhotoFile)
admin.site.register(PhotoLink)
admin.site.register(UserProfile)
admin.site.register(SiteConfig,SiteConfigAdmin)
admin.site.register(MemberConfig,MemberConfigAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(UserAlbumPaidRecord)