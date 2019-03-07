from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# webmail.webfaction.com - Web Mail
# mail.webfaction.com - IMAP and POP
# smtp.webfaction.com - SMTP

def upload_location(instance,filename):
	return "{0}/{1}".format(instance.photo,filename)

def avatar_upload_location(instance,filename):
	return "{0}/{1}".format(instance.actress_name_ch,filename)

def banner_upload_location(instance,filename):
	return "{0}".format(filename)

class UserProfile(models.Model):
	"""对Django自带的User表进行扩展"""
	user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='profile')
	member_type = models.BooleanField(default=False)
	member_expire = models.DateField(null=True,blank=True)		#会员过期时间
	count_coin = models.DecimalField(default=0,max_digits=8,decimal_places=2) 	#金币余额
	Album_paid_count = models.IntegerField(default=0)		#相册购买总数

	def __str__(self):
		return "{}'s profile".format(self.user.__str__())

class UserAlbumPaidRecord(models.Model):
	user_id = models.CharField(max_length = 1024)
	order_id = models.CharField(max_length = 1024)	#同Order表ID字段
	photo_id = models.CharField(max_length = 1024)	#同Photo表ID字段
	order_type = models.CharField(max_length = 1024)	#字符串:single,bundle,member
	date_paid = models.DateTimeField(blank=True,null=True,auto_now_add=True)	#购买成功日期

	def get_album_name(self):
		photo_id = str(self.photo_id)
		album = Photo.objects.get(id=photo_id)
		album_name = album.name_chinese
		return album_name

	def get_actress_name(self):
		photo_id = str(self.photo_id)
		album = Photo.objects.get(id=photo_id)
		actress_name = album.model_name
		return actress_name

	def get_company(self):
		photo_id = str(self.photo_id)
		album = Photo.objects.get(id=photo_id)
		company_name = album.company
		return company_name

class Order(models.Model):
	user_name = models.CharField(max_length = 1024)	#对应用户表<用户名>字段
	order_id = models.CharField(max_length = 1024)
	date_created = models.DateTimeField(auto_now_add = True)
	date_update = models.DateTimeField(blank=True,null=True,auto_now=True)
	order_info = models.CharField(max_length = 2048)	#等于相册ID
	order_status = models.CharField(max_length = 1024)
	order_type = models.CharField(max_length = 1024)	#字符串:single,bundle,member
	order_price = models.CharField(max_length = 1024)
	paid_price = models.CharField(blank=True,null=True,max_length = 1024)
	ppz_order_id = models.CharField(max_length = 1024,null=True,blank=True)	#paypayzhu平台的订单号

	def get_album_name(self):
		photo_id = str(self.order_info)
		album = Photo.objects.get(id=photo_id)
		album_name = album.name_chinese
		return album_name

	def get_actress_name(self):
		photo_id = str(self.order_info)
		album = Photo.objects.get(id=photo_id)
		actress_name = album.model_name
		return actress_name

	def get_company(self):
		photo_id = str(self.order_info)
		album = Photo.objects.get(id=photo_id)
		company_name = album.company
		return company_name

class Series(models.Model):
	"""图片的分类"""
	text = models.CharField(max_length=40)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		"""返回模型的字符串表示"""
		return self.text

class Photo(models.Model):
	"""图片集"""
	series = models.ForeignKey("Series",on_delete=models.PROTECT,null=False)	#欧美|日本|中国
	company = models.ForeignKey("Company",max_length = 60,null=True,blank=True,on_delete=models.PROTECT)	#公司
	name = models.CharField(max_length = 60)	#标题
	name_chinese = models.CharField(max_length=60)	#中文标题
	model_name = models.ManyToManyField("Actress")	#演员名
	date_added = models.DateTimeField(null=True,blank=True,auto_now_add=True)	#添加日期
	photo_tag = models.ManyToManyField("Tag",blank=True)	#标签
	views_count = models.PositiveIntegerField(default=0)	#总点击量
	history_views_count = models.PositiveIntegerField(default=0)	#截至昨日总点击量
	yesterday_views_count = models.PositiveIntegerField(default=0,null=True)	#昨日点击量
	temperature = models.FloatField(default=0)	#相册热度
	#VIP相册
	vip_photo = models.BooleanField(default=False)
	#付费下载
	buy_content = models.CharField(max_length=60,null=True,blank=True)	#付费说明
	buy_price = models.IntegerField(null=True,blank=True)	#价格
	buy_link = models.CharField(max_length = 360,null=True,blank=True)	#购买链接
	#高级购买(VIP不免费)
	vip_bundle = models.BooleanField(default=False)
	#暂未启用
	bundle_content = models.CharField(max_length=60,null=True,blank=True)	#Bundle说明
	bundle_price = models.IntegerField(null=True,blank=True)	#价格
	bundle_link = models.CharField(max_length = 360,null=True,blank=True)	#购买链接
	"""自动链接数量"""
	suited_count = models.IntegerField(default=0)

	def __str__(self):
		"""返回模型的字符串表示"""
		return self.name

	def get_cover_pic_link(self):
		current_name = self.id
		cover_pic_link = PhotoLink.objects.filter(photo=current_name).order_by('id')[0]
		return cover_pic_link.pic_link

	def get_actress_name(self):
		actress_name = self.model_name.all()

	def get_actress_id(self):
		actress = self.model_name.all()[0]
		actress = Actress.objects.get(actress_name_ch=actress)
		return actress.id

	def get_company_name(self):
		current_company = self.company

	def get_photo_id(self):
		return self.id

	def get_all_pic_link(self):
		current_name = self.id
		all_pic_links = PhotoLink.objects.filter(photo=current_name).order_by('id')
		detail_pic_links = []
		for all_pic_link in all_pic_links:
			detail_pic_links.append(all_pic_link.pic_link)
		if self.suited_count != 0:
			num = 2
			first_pic_link = PhotoLink.objects.get(photo=current_name).pic_link[0:-5]
			while num <= self.suited_count:
				pic_link = first_pic_link + str(num) + '.jpg'
				detail_pic_links.append(pic_link)
				num += 1
		return detail_pic_links

	def increase_views_count(self):
		self.views_count += 1
		self.save(update_fields=['views_count'])

	def get_absolute_url(self):
		return '/photo/%i' % self.id

class Actress(models.Model):
	actress_name_ch = models.CharField(max_length=60,null=True,blank=True)
	actress_name_jp = models.CharField(max_length=60,null=True,blank=True)
	actress_name_en = models.CharField(max_length=60,null=True,blank=True)
	avatar = models.ImageField(
							upload_to=avatar_upload_location,
							null=True,blank=True,
							)
	description = models.TextField(max_length=9999,null=True,blank=True)
	count_album = models.IntegerField(default=0)
	temperature = models.FloatField(default=0)
	#是否进入热搜标签池
	hot_search = models.BooleanField(default=False)

	def __str__(self):
		return self.actress_name_ch

	def get_all_photos(self):
		current_actress = self.actress_name_ch
		all_photos = Photo.objects.filter(model_name=current_actress)
		return all_photos

	def get_absolute_url(self):
		return '/actress_detail/%i' % self.id


class Tag(models.Model):
	"""相册标签"""
	tag_name = models.CharField(max_length = 20)

	def __str__(self):
		"""返回模型的字符串表示"""
		return self.tag_name

class Company(models.Model):
	"""公司标签"""
	company_name = models.CharField(max_length = 60)

	def __str__(self):
		"""返回模型的字符串表示"""
		return self.company_name


class PhotoFile(models.Model):
	pic = models.ImageField(
							upload_to=upload_location,
							null=True,blank=True,
							)
	photo = models.ForeignKey("Photo",on_delete=models.CASCADE,null=False)

class PhotoLink(models.Model):
	pic_link = models.CharField(max_length=1024)
	photo = models.ForeignKey("Photo",on_delete=models.CASCADE,null=False)

class SiteConfig(models.Model):
	config_name = models.CharField(default=None,max_length=100)
	config_value = models.CharField(default=None,max_length=100)

class SlideBanner(models.Model):
	banner_pic = models.ImageField(
							upload_to=banner_upload_location
							)
	banner_title = models.CharField(max_length=999)
	banner_link = models.CharField(max_length=999)

class MemberConfig(models.Model):
	config_name = models.CharField(default=None,max_length=100)
	config_value = models.CharField(default=None,max_length=9999)
