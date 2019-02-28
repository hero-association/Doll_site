#encoding: utf-8
from django.shortcuts import render
from doll_sites import models
from django.contrib.auth.models import User
from .models import Series,upload_location,Photo,PhotoFile,PhotoLink,Company,Tag,Actress,SiteConfig,Order,UserAlbumPaidRecord,MemberConfig,UserProfile
from django.views import generic
from django.core.paginator import Paginator
import random
import hashlib
import json
import urllib
import datetime
from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

# Create your views here.
def index(request):
	"""网站主页"""
	num_pic = PhotoLink.objects.all().count()
	num_photo = Photo.objects.all().count()
	company_list = Company.objects.all()[:5]
	recommend_european = Photo.objects.filter(series=1).order_by('?')[:5]
	recommend_japanese = Photo.objects.filter(series=2).order_by('?')[:5]
	recommend_chinese = Photo.objects.filter(series=3).order_by('?')[:5]
	recommend_newest = Photo.objects.order_by('-date_added')[:5]
	recommend_hotest = Photo.objects.order_by('-views_count')[:5]
	recommend_person = Actress.objects.order_by('?')[:4]
	context = {
				'num_pic':num_pic,		#总图片数
				'num_photo':num_photo,		#总相册数
				'recommend_european':recommend_european,		#推荐相册-欧美
				'recommend_japanese':recommend_japanese,		#推荐相册-日本
				'recommend_chinese':recommend_chinese,		#推荐相册-中国
				'recommend_newest':recommend_newest,		#推荐相册-最新
				'recommend_hotest':recommend_hotest,		#推荐相册-最热
				'recommend_person':recommend_person,		#推荐偶像
				'company_list':company_list,		#公司列表
				'nbar':'home',	#导航标志
	}
	return render(
		request,
		'doll_sites/index.html',
		context
	)

#保证循环的次数在规定的展示栏个数，如果设置11，循环的次数保证在11次
class DollPaginator(Paginator):
    def __init__(self,current_page,per_pager_num,*args,**kwargs):
        '''
        :param current_page:  当前页
        :param per_pager_num: 底边栏展示页数
        '''
        self.current_page = int(current_page)
        self.per_pager_num = int(per_pager_num)
        super(DollPaginator, self).__init__(*args, **kwargs)

    def page_num_range(self):
	#总页数小于实际展示页
        if self.num_pages < self.per_pager_num:
            return range(1,self.num_pages+1)

        #part 当前总展示栏中间点5
        part = int(self.per_pager_num//2)

        #最小页数为1防止出现负数情况
        if self.current_page <= part:
            return range(1,self.per_pager_num+1)

        #最大页数为实际总页数
        if(self.current_page+part)>self.num_pages:
            return range(self.num_pages-self.per_pager_num+1,self.num_pages+1)
        
        return range(self.current_page-part,self.current_page+part+1)

def photolist(request,series,company,pageid):
	"""列表页"""
	sort = request.GET.get('sort','-date_added')

	if series == 0:
		if company == 0:
			photo_list = Photo.objects.order_by(sort)
		else:
			photo_list = Photo.objects.filter(company=company).order_by(sort)
	else:
		if company == 0:
			photo_list = Photo.objects.filter(series=series).order_by(sort)
		else:
			photo_list = Photo.objects.filter(series=series,company=company).order_by(sort)
	# photo_list = Photo.objects.order_by('-date_added')
	limit = 20
	#分页器
	paginator = DollPaginator(pageid,5,photo_list,limit)
	# page = request.GET.get('page','1')
	current_photo_list = paginator.page(pageid)
	#热搜标签&最新图集
	hot_actress = Actress.objects.all().order_by('?')[:6]
	new_photo_list = Photo.objects.order_by(sort)[:6]
	#导航高亮
	if company != 0:
		current_company = Company.objects.get(id=company)
	else:
		current_company = "all_company"
	nbar = str(current_company)

	context = {
		'current_photo_list':current_photo_list,		#分页的相册列表
		'photo_list':photo_list,		#未分页的相册列表
		'nbar':nbar,	#导航标志
		'new_photo_list':new_photo_list,	#最新图集
		'hot_actress':hot_actress,		#热搜标签
	}

	return render(
		request,
		'doll_sites/photo_list.html',
		context
	)

def photodetail(request,photoid):
	"""详情页"""
	user = request.user
	#判断用户是否为VIP
	if user.is_authenticated:
		try:
			user_profile_object = UserProfile.objects.get(user=user)
			user_vip_status = user_profile_object.member_type
		except:
			user_vip_status = False
	else:
		user_vip_status = False
	photo_detail = Photo.objects.get(id=photoid)
	photo_detail.increase_views_count()		#访问次数+1
	#照片购买
	payment_status = SiteConfig.objects.get(config_name='Payment_links')
	if payment_status.config_value == 'True':
		if photo_detail.buy_link is None:
			buy_links = []
		else:
			buy_links = [photo_detail.buy_link,]
	else:
		buy_links = []
	#Bundle购买
	if photo_detail.bundle_link is None:
		bundle_links = []
	else:
		bundle_links = [photo_detail.bundle_link,]
	#当前相册的购买状态
	if UserAlbumPaidRecord.objects.filter( Q(photo_id=photoid) & Q(user_id=user.username) ):
		album_already_paid = True
	else:
		album_already_paid = False
	#查询当前演员的相关图集
	current_actress = photo_detail.model_name.all().order_by('pk')
	related_album = []
	for actress in current_actress:
		p = Photo.objects.filter(model_name = Actress.objects.get(actress_name_ch = actress)).order_by('-views_count')
		related_album += p
	current_album = Photo.objects.filter(id=photoid)
	related_album = list(set(related_album) - set(current_album))[:10]
	buy_content = photo_detail.buy_content
	bundle_content = photo_detail.bundle_content
	#热搜标签
	hot_actress = Actress.objects.all().order_by('?')[:6]
	#相册标签
	photo_tag = photo_detail.photo_tag.all()
	#创建订单
	api_user = '182553c7'
	api_key = 'c3ff51b8-a1f5-4ad3-8b93-f770b81a02f0'
	order_price = str(photo_detail.buy_price)+".00"
	user_name = 'user_mail'
	pay_type = int(2)	#表示支付宝
	nowtime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
	random_id = str(random.randint(1000000,9999999))
	order_id = str(pay_type)+str(nowtime)+random_id
	redirect = 'http://127.0.0.1:8000/order/' + order_id
	order_info = photo_detail.id
	notify_url = 'http://requestbin.fullcontact.com/16xwxr61'
	single_signature = make_signature(order_price,pay_type,redirect,order_id,order_info,notify_url)
	current_url = request.path
	#VIP相册逻辑
	vip_album = photo_detail.vip_photo
	context = {
		'buy_links':buy_links,		#购买链接列表
		'bundle_links':bundle_links,		#Bundle链接列表
		'photo_detail':photo_detail,		#当前相册
		'related_album':related_album,		#当前演员的相关图集
		'current_actress':current_actress,		
		'hot_actress':hot_actress,		#热搜标签
		'photo_tag':photo_tag,		#相册标签
		#支付参数
		'api_user':api_user,
		'order_price':order_price,
		'pay_type':pay_type,
		'redirect':redirect,
		'order_id':order_id,
		'order_info':order_info,
		'notify_url':notify_url,
		'single_signature':single_signature,
		'buy_content':buy_content,
		'bundle_content':bundle_content,
		'album_already_paid':album_already_paid,
		'current_url':current_url,
		'vip_album':vip_album,
		'user_vip_status':user_vip_status,
	}

	return render(
		request,
		'doll_sites/photo_detail.html',
		context
	)

def order_detail(request,order_id):
	order_id = str(order_id)
	current_order = Order.objects.get(order_id=order_id)
	photo_id = current_order.order_info
	related_album = Photo.objects.get(id=photo_id)
	order_status = current_order.order_status
	photo_name = related_album.name_chinese
	photo_actress = list(related_album.model_name.all())
	actress_name = ''
	for actress in photo_actress:
		actress_name += str(actress)
	download_link = ''

	if current_order.order_type == 'single':
		download_link = related_album.buy_link
		order_type = '照片集'
	elif current_order.order_type == 'bundle':
		download_link = related_album.bundle_link
		order_type = '照片+视频'
	elif current_order.order_type == 'member':
		download_link = ''
		order_type = '购买会员'
	product_name = '['+actress_name+']' +' '+ photo_name +' '+ order_type
	price = current_order.order_price

	context = {
		'order_id':order_id,
		'order_status':order_status,
		'product_name':product_name,
		'price':price,
		'download_link':download_link,
	}

	return render(
		request,
		'doll_sites/order_detail.html',
		context
	)


def make_signature(price,pay_type,redirect,order_id,order_info,notify_url):

	api_user = '182553c7'
	api_key = 'c3ff51b8-a1f5-4ad3-8b93-f770b81a02f0'

	param = {
        'api_user' : api_user,
        'price': price,
        'type': pay_type,
        'redirect': redirect,
        'order_id': order_id,
        'order_info': order_info,
        'notify_url' : notify_url,
    }
    
	param_keys = list(param.keys())
	param_keys.sort()
    
	param_str = api_key
    
	for key in param_keys:
		param_str += str(param[key])
    
	param_str = param_str.encode('utf-8')
	signature = hashlib.md5(param_str).hexdigest()
	return signature

def pay_info(order_price,pay_type,mail_addr,order_info,order_id):
	redirect = '/about'
	data = {
		'api_user' : '182553c7',
		'api_key' : 'c3ff51b8-a1f5-4ad3-8b93-f770b81a02f0',
		'price' : str(order_price),
		'user_id' : mail_addr,
		'redirect' : "https://paypayzhu.com/#/test",
		'type' : pay_type,
		'mail_addr' : mail_addr,
		'order_id' : str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + str(random.randint(1000000,9999999)),
		'order_info' : order_info,
		'signature' : make_signature(order_price,pay_type,redirect,order_id,order_info,notify_url),
	}
	return data
	
def payment_response(request):
	if request.method == 'POST':
		order_id = request.POST.get('order_id')
		ppz_order_id = request.POST.get('ppz_order_id')
		real_price = request.POST.get('real_price')
		current_order = Order.objects.filter(order_id=order_id)
		current_order_object = Order.objects.get(order_id=order_id)
		if current_order:
			current_order.update(order_status='Paid')
			current_order.update(ppz_order_id='ppz_order_id')
			current_order.update(paid_price='real_price')
			user_name = Order.objects.filter(order_id=order_id)[0].user_name
			order_info = Order.objects.filter(order_id=order_id)[0].order_info
			order_type = Order.objects.filter(order_id=order_id)[0].order_type
			if current_order_object.order_info == 'month_member':
				days_add = 30
			elif current_order_object.order_info == 'season_member':
				days_add = 90
			elif current_order_object.order_info == 'year_member':
				days_add = 365
			if current_order_object.order_type == 'member':	#处理会员
				user_id = User.objects.get(username=user_name)
				user_profile = UserProfile.objects.filter(user=user_id)
				try:	#有资料的情况
					user_profile_object = UserProfile.objects.get(user=user_id)
					user_profile = UserProfile.objects.get(user=user_id)
					if user_profile_object.member_type == False:	#不是会员的情况
						user_profile.update(member_type=True)
						last_day = datetime.date.today()
						new_expire_time = last_day + datetime.timedelta(days=days_add)
						user_profile.update(member_expire=new_expire_time)
						return HttpResponse('Member Paid!')
					else:	#是会员的情况
						last_day = user_profile.member_expire
						user_profile = UserProfile.objects.filter(user=user_id)
						new_expire_time = last_day + datetime.timedelta(days=days_add)
						user_profile.update(member_expire=new_expire_time)
						return HttpResponse('Member Paid!')
				except:	#没有资料的情况
					last_day = datetime.date.today()
					new_expire_time = last_day + datetime.timedelta(days=days_add)
					models.UserProfile.objects.create(
						user=user_id,
						member_type=True,
						member_expire=new_expire_time,
			        )
					return HttpResponse('Member Paid!')
			else:
				if UserAlbumPaidRecord.objects.filter(order_id=order_id):	#创建已购列表
					return HttpResponse('Already Exist!')
				else:
					paid_record = UserAlbumPaidRecord.objects.filter(order_id=order_id)
					paid_record.create(
						user_id=user_name,
						order_id=order_id,
						photo_id=order_info,
						order_type=order_type,
					)
					return HttpResponse('Paid!')
		else:
			return HttpResponse('Not Exist!')
	else:
		return HttpResponse('It is not a POST request!!!')

def create_order(request):
	if request.method == 'POST':
		user_name = request.POST.get('user_name')
		order_id = request.POST.get('order_id')
		order_info = request.POST.get('order_info')
		order_status = request.POST.get('order_status')
		order_type = request.POST.get('order_type')
		order_price = request.POST.get('price')
		if Order.objects.filter(order_id=order_id):
			return HttpResponse('Already Exist!')
		else:
			models.Order.objects.create(
				user_name=user_name,
				order_id=order_id,
				order_info=order_info,
				order_status=order_status,
				order_type=order_type,
				order_price=order_price,
	        )
			return HttpResponse('Created!')
	else:
		return HttpResponse('It is not a POST request!!!')


def actresslist(request,pageid):
	"""演员列表页"""
	actress_list = Actress.objects.all().order_by('actress_name_ch')
	limit = 20
	paginator = DollPaginator(pageid,5,actress_list,limit)
	# page = request.GET.get('page','1')

	current_actress_list = paginator.page(pageid)
	context = {
		'current_actress_list' : current_actress_list,		#分页的偶像列表
		'actress_list' : actress_list,		#未分页的偶像列表
		'nbar':'actress',	#导航标志
	}

	return render(
		request,
		'doll_sites/actress_list.html',
		context
	)

def actressdetail(request,actressid):
	"""演员详情页"""
	current_actress = Actress.objects.get(id=actressid)
	related_album = Photo.objects.filter(model_name = Actress.objects.get(actress_name_ch = current_actress)).order_by('-views_count')
	related_company = []
	for album in related_album:
		related_company.append(album.company)
	related_company = set(related_company)

	context = {
		'related_album' : related_album,		#当前偶像的相册列表
		'current_actress' : current_actress,		#当前偶像
		'related_company' : related_company,		#关联的公司
		'nbar':'actress',	#导航标志
	}

	return render(
		request,
		'doll_sites/actress_detail.html',
		context
	)

def searchresult(request):
	"""搜索结果页"""
	kwd = request.GET.get('kwd')
	#搜演员
	searched_actress = Actress.objects.filter(actress_name_ch__icontains=kwd)
	result_list_actress = []
	for actress in searched_actress:
		p = Photo.objects.filter(model_name = Actress.objects.get(actress_name_ch=actress)).order_by('-views_count')
		result_list_actress += p
	#搜公司
	searched_company = Company.objects.filter(company_name__icontains=kwd)
	result_list_company = []
	for company in searched_company:
		p = Photo.objects.filter(company = Company.objects.get(company_name=company)).order_by('-views_count')
		result_list_company += p
	#搜TAG
	searched_tag = Tag.objects.filter(tag_name__icontains=kwd)
	result_list_tag = []
	for tag in searched_tag:
		p = Photo.objects.filter(photo_tag = Tag.objects.get(tag_name=tag)).order_by('-views_count')
		result_list_tag += p
	#搜标题
	result_list_title = Photo.objects.filter(name_chinese__icontains=kwd).order_by('views_count')		
	result_list = set(result_list_actress + list(result_list_title) + result_list_tag + result_list_company)
	result_count = len(result_list)

	context = {
		'result_list' : result_list,
		'kwd' : kwd,
		'result_count' : result_count,
	}

	return render(
		request,
		'doll_sites/search.html',
		context
	)

@login_required
def profile(request):
	"""用户资料"""
	user = request.user
	user_paid_albums = Order.objects.filter( Q(user_name=user) & Q(order_type='single') & Q(order_status='Paid') ).order_by('-date_created')
	try:
		user_profile = UserProfile.objects.get(user=user)
		member_expire = user_profile.member_expire
	except:
		member_expire = False
	context = {
		'nbar':'profile',	#导航标志
		'user':user,
		'user_paid_albums':user_paid_albums,
		'member_expire':member_expire,
	}
	return render(
		request,
		'doll_sites/profile.html',
		context
	)

def about(request):
	"""关于页面"""
	context = {
		'nbar':'about',	#导航标志
	}

	return render(
		request,
		'doll_sites/about.html',
		context
	)

def member(request):
	'''会员页面'''
	redirect_url = request.GET.get('redirect_url')
	month_price = MemberConfig.objects.get(config_name='month_price')
	month_content = MemberConfig.objects.get(config_name='month_content')
	season_price = MemberConfig.objects.get(config_name='season_price')
	season_content = MemberConfig.objects.get(config_name='season_content')
	year_price = MemberConfig.objects.get(config_name='year_price')
	year_content = MemberConfig.objects.get(config_name='year_content')
	intro_text = MemberConfig.objects.get(config_name='intro_text')
	#创建订单
	api_user = '182553c7'
	api_key = 'c3ff51b8-a1f5-4ad3-8b93-f770b81a02f0'
	user_name = 'user_mail'
	pay_type = int(2)	#表示支付宝
	nowtime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
	random_id = str(random.randint(1000000,9999999))
	random_id_2 = str(random.randint(1000000,9999999))
	random_id_3 = str(random.randint(1000000,9999999))
	order_id = str(pay_type)+str(nowtime)+random_id
	order_id_season = str(pay_type)+str(nowtime)+random_id_2
	order_id_year = str(pay_type)+str(nowtime)+random_id_3
	redirect = 'http://127.0.0.1:8000' + str(redirect_url)
	notify_url = 'http://requestbin.fullcontact.com/1al00m61'
	month_order_info = 'month_member'
	month_signature = make_signature(month_price.config_value,pay_type,redirect,order_id,month_order_info,notify_url)
	season_order_info = 'season_member'
	season_signature = make_signature(season_price.config_value,pay_type,redirect,order_id,season_order_info,notify_url)
	year_order_info = 'season_member'
	year_signature = make_signature(year_price.config_value,pay_type,redirect,order_id,year_order_info,notify_url)
	context = {
		'month_price':month_price,
		'month_content':month_content,
		'season_price':season_price,
		'season_content':season_content,
		'year_price':year_price,
		'year_content':year_content,
		'intro_text':intro_text,
		'redirect':redirect,
		'api_user':api_user,
		'user_name':user_name,
		'pay_type':pay_type,
		'order_id':order_id,
		'order_id_season':order_id_season,
		'order_id_year':order_id_year,
		'notify_url':notify_url,
		'month_order_info':month_order_info,
		'month_signature':month_signature,
		'season_order_info':season_order_info,
		'season_signature':season_signature,
		'year_order_info':year_order_info,
		'year_signature':year_signature,

	}
	return render(
		request,
		'doll_sites/member_order.html',
		context
	)

def baidu(request):
	'''百度验证'''
	context = {
		'nbar':'about',	#导航标志
	}

	return render(
		request,
		'doll_sites/baidu_verify_jiNtuP7fb1.html',
		context
	)
