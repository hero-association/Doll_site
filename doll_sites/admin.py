from django.contrib import admin
import datetime
from django.db.models import Q

# Register your models here.

from doll_sites.models import Series,Photo,PhotoFile,PhotoLink,Tag,Company,Actress,SiteConfig,Order,UserProfile,UserAlbumPaidRecord,SlideBanner,MemberConfig,XdataOrder

class PhotoFileInline(admin.TabularInline):
	model = PhotoFile

class PhotoLinkInline(admin.TabularInline):
	model = PhotoLink	

# Define the admin class
class PhotoAdmin(admin.ModelAdmin):
	search_fields = ['name_chinese']
	list_display = ('id','series','company','name','name_chinese','date_added','vip_photo','views_count','temperature','history_views_count')
	list_editable = ('company','name','name_chinese','vip_photo',)
	inlines = [PhotoFileInline,PhotoLinkInline]
	list_filter = ('series','company','vip_photo','model_name')

	# radio_fields = {"model_name": admin.HORIZONTAL}
	filter_horizontal = ['photo_tag','model_name']
	save_on_top = True
	fieldsets = (
        ('Basic', {
            'fields': ('series', 'company', 'model_name','temperature' )
        }),
        ('Info', {
            'fields': ('name', 'name_chinese','photo_tag')
        }),
        ('Pay', {
            'fields': ('vip_photo', 'buy_link','buy_price','buy_content','vip_bundle','bundle_link','bundle_price','bundle_content')
        }),
        ('auto_image_link', {
            'fields': ('suited_count',)
        }),
        ('Video', {
            'fields': ('video_poster','video_link')
        }),
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
	search_fields = ['user_name']
	model = Order
	list_display = ('order_id','user_name','order_info','order_status','order_price','paid_price','date_created','date_update')
	list_filter = ('order_status',)
	date_hierarchy = "date_created"

class ActressAdmin(admin.ModelAdmin):
	list_display = ('actress_name_ch','actress_name_jp','actress_name_en','get_album_num','get_avg_temperature','get_his_avg_views','get_ytd_avg_views')
	
	def get_album_num(self,id):
		actress = Actress.objects.get(id=id.pk)
		num_albums_belong_to = Photo.objects.filter(model_name__id=actress.id).count()
		return(num_albums_belong_to)

	def get_avg_temperature(self,id):
		actress = Actress.objects.get(id=id.pk)
		albums_belong_to = Photo.objects.filter(model_name__id=actress.id)
		c = 0
		for album in albums_belong_to:
			c += album.temperature
		avg = c/albums_belong_to.count()
		avg = round(avg,2)
		return(avg)

	def get_his_avg_views(self,id):
		actress = Actress.objects.get(id=id.pk)
		albums_belong_to = Photo.objects.filter(model_name__id=actress.id)
		views_count = 0
		for album in albums_belong_to:
			views_count += album.views_count
		avg = views_count/albums_belong_to.count()
		avg = round(avg,2)
		return(avg)

	def get_ytd_avg_views(self,id):
		actress = Actress.objects.get(id=id.pk)
		albums_belong_to = Photo.objects.filter(model_name__id=actress.id)
		views_count = 0
		for album in albums_belong_to:
			views_count += album.yesterday_views_count
		avg = views_count/albums_belong_to.count()
		avg = round(avg,2)
		return(avg)

class UserProfileAdmin(admin.ModelAdmin):
	search_fields = ['id']
	list_display = ('get_user_name','member_type','member_expire')
	list_editable = ('member_expire',)

	def get_user_name(id,self):
		return self.user
		
class SiteConfigAdmin(admin.ModelAdmin):
	list_display = ('config_name','config_value')
	list_editable = ('config_value',)

class MemberConfigAdmin(admin.ModelAdmin):
	list_display = ('config_name','config_value')
	list_editable = ('config_value',)

class XdataOrderAdmin(admin.ModelAdmin):
	list_display = ('order_year','order_month','order_date','get_order_count','get_paid_count','get_total_income','get_avg_order_price')

	def get_order_count(id,self):
		if self.order_date:
			d = datetime.date(self.order_year,self.order_month,self.order_date)
			q = Order.objects.filter(date_created=d).count()
			return q
		else:
			month = int(self.order_month)
			year = int(self.order_year)
			q = Order.objects.filter( Q(date_created__month=month) & Q(date_created__year=year) ).count()
			return q

	def get_paid_count(id,self):
		if self.order_date:
			d = datetime.date(self.order_year,self.order_month,self.order_date)
			q = Order.objects.filter( Q(date_created=d) & Q(order_status='Paid') ).count()
			return q
		else:
			month = int(self.order_month)
			year = int(self.order_year)
			q = Order.objects.filter( Q(date_created__month=month) & Q(date_created__year=year) & Q(order_status='Paid') ).count()
			return q

	def get_total_income(id,self):
		if self.order_date:
			d = datetime.date(self.order_year,self.order_month,self.order_date)
			q = Order.objects.filter( Q(date_created=d) & Q(order_status='Paid') )
			num = 0
			for order in q:
				num += float(order.paid_price)
			return num
		else:
			month = int(self.order_month)
			year = int(self.order_year)
			q = Order.objects.filter( Q(date_created__month=month) & Q(date_created__year=year) & Q(order_status='Paid') )
			num = 0
			for order in q:
				if order.paid_price:
					num += float(order.paid_price)
			return num

	def get_avg_order_price(id,self):
		if self.order_date:
			d = datetime.date(self.order_year,self.order_month,self.order_date)
			q = Order.objects.filter( Q(date_created=d) & Q(order_status='Paid') )
			num = 0
			for order in q:
				num += float(order.paid_price)
			if q.count() != 0 and num != 0:
				num = num/q.count()
				num = num/q.count()
			else:
				num = 0
			return num
		else:
			month = int(self.order_month)
			year = int(self.order_year)
			q = Order.objects.filter( Q(date_created__month=month) & Q(date_created__year=year) & Q(order_status='Paid') )
			num = 0
			for order in q:
				if order.paid_price:
					num += float(order.paid_price)
			if q.count() != 0 and num != 0:
				num = num/q.count()
			else :
				num = 0
			return num

# Register the admin class with the associated model
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Actress,ActressAdmin)
admin.site.register(PhotoFile)
admin.site.register(PhotoLink)
admin.site.register(SiteConfig,SiteConfigAdmin)
admin.site.register(SlideBanner)
admin.site.register(UserProfile,UserProfileAdmin)
admin.site.register(MemberConfig,MemberConfigAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(UserAlbumPaidRecord)
admin.site.register(XdataOrder,XdataOrderAdmin)