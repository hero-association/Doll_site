#encoding: utf-8
from django.shortcuts import render
from doll_sites import models
from django.contrib.auth.models import User
from .models import Series,upload_location,Photo,PhotoFile,PhotoLink,Company,Tag,Actress,SiteConfig,SlideBanner,Order,UserAlbumPaidRecord,MemberConfig,UserProfile
from django.views import generic
from django.core.paginator import Paginator
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
import sqlite3
# import psycopg2
import random
import hashlib
import json
import urllib
import datetime
from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

def get_index_recommend(series_id):
	series_hot = Photo.objects.filter(series=series_id).order_by('-temperature')[:20]
	series_new = Photo.objects.filter(series=series_id).order_by('-temperature')[:10]
	series_index_recommend = list(set(list(series_hot) + list(series_new)))
	random.shuffle(series_index_recommend)
	series_index_recommend = series_index_recommend[:5]
	return series_index_recommend

def get_hot_search_actress():
	high_temperature_actress = []
	# high_temperature_actress = Actress.objects.order_by('-temperature')[:10]
	recommend_actress = Actress.objects.filter(hot_search=True)
	hot_actress_list = list(set(list(high_temperature_actress)+list(recommend_actress)))
	random.shuffle(hot_actress_list)
	hot_actress_list = hot_actress_list[:6]
	return hot_actress_list

def index(request):
	"""网站主页"""
	num_pic = PhotoLink.objects.all().count()
	num_photo = Photo.objects.all().count()
	company_list = Company.objects.all()[:5]
	silde_banner = SlideBanner.objects.all()
	#首页欧洲推荐
	recommend_european = get_index_recommend(1)
	#首页日本推荐
	recommend_japanese = get_index_recommend(2)
	#首页中国推荐
	recommend_chinese = get_index_recommend(3)
	#首页最新推荐
	recommend_newest = Photo.objects.order_by('-date_added')[:35]
	recommend_newest = list(recommend_newest)
	random.shuffle(recommend_newest)
	recommend_newest = recommend_newest[:5]
	#首页热门推荐
	recommend_hotest = Photo.objects.order_by('-temperature')[:15]
	recommend_hotest = list(recommend_hotest)
	random.shuffle(recommend_hotest)
	recommend_hotest = recommend_hotest[:5]
	#首页热门偶像
	recommend_person = Actress.objects.order_by('?')[:4]
	#SEO
	title = '小熊社-自由的萝莉图库|U15|白丝|Candydoll|Silverstar|Imouto.tv'
	keywords = '萝莉图库,萝莉写真,Silverstar,Candydoll,EvaR,ElonaV,LauraB,U15,金子美穗,河西莉子,牧原香鱼,稚名桃子,工口小学生赛高酱'
	description = '小熊社是自由的萝莉图库,提供包括Candydoll、Silverstar、Imouto、U15等多个品牌的写真图集,涵盖了包括EvaR,ElonaV,LauraB,金子美穗,河西莉子,牧原香鱼,稚名桃子,工口小学生赛高酱等海内外知名萝莉'
	context = {
		'title':title,
		'keywords':keywords,
		'description':description,
		'num_pic':num_pic,		#总图片数
		'num_photo':num_photo,		#总相册数
		'company_list':company_list,		#公司列表
		'silde_banner':silde_banner,		#轮播图
		'recommend_european':recommend_european,		#推荐相册-欧美
		'recommend_japanese':recommend_japanese,		#推荐相册-日本
		'recommend_chinese':recommend_chinese,		#推荐相册-中国
		'recommend_newest':recommend_newest,		#推荐相册-最新
		'recommend_hotest':recommend_hotest,		#推荐相册-最热
		'recommend_person':recommend_person,		#推荐偶像
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
	#热搜标签
	hot_actress = get_hot_search_actress()
	#最新图集
	right_side_sort = '-date_added'
	if sort == '-date_added':
		right_side_sort = '-views_count'
	if series == 0:
		if company == 0:
			new_photo_list = Photo.objects
		else:
			new_photo_list = Photo.objects.filter(company=company)
	else:
		if company == 0:
			new_photo_list = Photo.objects.filter(series=series)
		else:
			new_photo_list = Photo.objects.filter(series=series,company=company)
	new_photo_list = new_photo_list.order_by(right_side_sort)[:12]
	new_photo_list = list(new_photo_list)
	random.shuffle(new_photo_list)
	new_photo_list = new_photo_list[:4]

	#导航高亮
	if company != 0:
		current_company = Company.objects.get(id=company)
	else:
		current_company = "all_company"
	nbar = str(current_company)

	#SEO
	title = '相册列表-小熊社-自由的萝莉图库|U15|白丝|Candydoll|Silverstar|Imouto.tv'
	keywords = '萝莉图库,萝莉写真,Silverstar,Candydoll,EvaR,ElonaV,LauraB,U15,金子美穗,河西莉子,牧原香鱼,稚名桃子,工口小学生赛高酱'
	description = '小熊社是自由的萝莉图库,提供包括Candydoll、Silverstar、Imouto、U15等多个品牌的写真图集,涵盖了包括EvaR,ElonaV,LauraB,金子美穗,河西莉子,牧原香鱼,稚名桃子,工口小学生赛高酱等海内外知名萝莉'
	context = {
		'title':title,
		'keywords':keywords,
		'description':description,
		'current_photo_list':current_photo_list,		#分页的相册列表
		'photo_list':photo_list,		#未分页的相册列表
		'nbar':nbar,	#导航标志
		'new_photo_list':new_photo_list,	#最新图集
		'hot_actress':hot_actress,		#热搜标签
		'series':series,
		'company':company,
	}

	return render(
		request,
		'doll_sites/photo_list.html',
		context
	)

def photodetail(request,photoid):
	"""详情页"""
	user = request.user
	nowdate = datetime.datetime.now().strftime('%Y%m%d')
	#判断用户是否为VIP
	if user.is_authenticated:
		try:
			user_profile_object = UserProfile.objects.get(user=user)
			user_vip_expiration = user_profile_object.member_expire
			user_vip_expiration = user_vip_expiration.strftime('%Y%m%d')
			if int(user_vip_expiration) - int(nowdate) >= 0:
				user_vip_status = True
			else:
				user_vip_status = False
		except:
			user_vip_status = False
	else:
		user_vip_status = False
	photo_detail = Photo.objects.get(id=photoid)
	#访问次数+1
	photo_detail.increase_views_count()
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
	if photo_detail.vip_bundle == False:
		if user_vip_status == True:
			album_already_paid = True
		else:
			if UserAlbumPaidRecord.objects.filter( Q(photo_id=photoid) & Q(user_id=user.username) ):
				album_already_paid = True
			else:
				album_already_paid = False
	else:
		if UserAlbumPaidRecord.objects.filter( Q(photo_id=photoid) & Q(user_id=user.username) ):
			album_already_paid = True
		else:
			album_already_paid = False
	#查询当前演员的相关图集
	current_actress = photo_detail.model_name.all().order_by('pk')
	related_album = []
	for actress in current_actress:
		actress_q = Photo.objects.filter(model_name = Actress.objects.get(actress_name_ch = actress)).order_by('-temperature')
		r = actress_q.filter(buy_link__isnull = False)
		related_album += r
		p = actress_q[:11]
		related_album += p
		q = actress_q.order_by('-date_added')[:4]
		related_album += q

	current_album = Photo.objects.filter(id=photoid)
	related_album = list(set(related_album) - set(current_album))
	random.shuffle(related_album)
	related_album = related_album[:10]
	buy_content = photo_detail.buy_content
	bundle_content = photo_detail.bundle_content
	#热搜标签
	hot_actress = get_hot_search_actress()
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
	redirect = 'http://www.lolizhan.com/order/' + order_id
	order_info = photo_detail.id
	notify_url = 'http://www.lolizhan.com/payment_response'
	single_signature = make_signature(order_price,pay_type,redirect,order_id,order_info,notify_url)
	current_url = request.path
	#VIP相册逻辑
	vip_album = photo_detail.vip_photo
	#SEO信息
	actress_list = ''
	for actress in current_actress:
		actress_list += str(actress)
		actress_list += ','
	tag_list = ''
	for t in photo_tag:
		tag_list += str(t)
		tag_list += ','
	title = actress_list + str(photo_detail.company) + ' ' + str(photo_detail.name_chinese) + ' - 小熊社'
	keywords = actress_list + tag_list + str(photo_detail.company)
	description = '本图集是' + actress_list + '在' + str(photo_detail.company) + '公司拍摄的' + str(photo_detail.name_chinese) + '系列,包含了' + tag_list + '等元素,是小熊社精心收集的萝莉图集。'
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
		#SEO
		'title':title,
		'keywords':keywords,
		'description':description,
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
	#SEO
	title = '订单详情-小熊社-自由的萝莉图库|U15|白丝|Candydoll|Silverstar|Imouto.tv'
	keywords = '萝莉图库,萝莉写真,Silverstar,Candydoll,EvaR,ElonaV,LauraB,U15,金子美穗,河西莉子,牧原香鱼,稚名桃子,工口小学生赛高酱'
	description = '小熊社是自由的萝莉图库,提供包括Candydoll、Silverstar、Imouto、U15等多个品牌的写真图集,涵盖了包括EvaR,ElonaV,LauraB,金子美穗,河西莉子,牧原香鱼,稚名桃子,工口小学生赛高酱等海内外知名萝莉'
	context = {
		'title':title,
		'keywords':keywords,
		'description':description,
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
			current_order.update(ppz_order_id=ppz_order_id)
			current_order.update(paid_price=real_price)
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

def get_user_info(request):
	if request.method == 'GET':
		user = request.user
		if user.is_authenticated:
			user_id = str(user.id)
			try:
				user_profile_object = UserProfile.objects.get(user=user)
				if user_profile_object.member_type == True:
					nowdate = datetime.datetime.now().strftime('%Y%m%d')
					user_vip_expiration = user_profile_object.member_expire
					user_vip_expiration = user_vip_expiration.strftime('%Y%m%d')
					if int(user_vip_expiration) - int(nowdate) >= 0:
						user_status = 'vip'
					else:
						user_status = 'expired'
				else:
					user_status = 'normal'
			except:
				user_status = 'normal'
		else:
			user_status = ''
			user_id = ''
		response = {'user_id':user_id,'user_status':user_status}
		return JsonResponse(response)
	else:
		return HttpResponse('It is not a GET request!!!')

def actresslist(request,pageid):
	"""演员列表页"""
	actress_list = Actress.objects.all().order_by('actress_name_ch')
	limit = 20
	paginator = DollPaginator(pageid,5,actress_list,limit)
	current_actress_list = paginator.page(pageid)
	#SEO
	title = '偶像列表-小熊社-自由的萝莉图库|U15|白丝|Candydoll|Silverstar|Imouto.tv'
	keywords = '萝莉图库,萝莉写真,Silverstar,Candydoll,EvaR,ElonaV,LauraB,U15,金子美穗,河西莉子,牧原香鱼,稚名桃子,工口小学生赛高酱'
	description = '小熊社是自由的萝莉图库,提供包括Candydoll、Silverstar、Imouto、U15等多个品牌的写真图集,涵盖了包括EvaR,ElonaV,LauraB,金子美穗,河西莉子,牧原香鱼,稚名桃子,工口小学生赛高酱等海内外知名萝莉'
	context = {
		'title':title,
		'keywords':keywords,
		'description':description,
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
	#SEO
	company_list = ''
	for c in related_company:
		company_list += str(c)
		company_list += ','
	title = str(current_actress.actress_name_ch) + ' - 小熊社'
	keywords = company_list + str(current_actress.actress_name_ch)
	description = str(current_actress.description)
	context = {
		'title':title,
		'keywords':keywords,
		'description':description,
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

	#SEO
	title = kwd + ' - 共 ' + str(result_count) + ' 个搜索结果 - 小熊社'
	keywords = kwd + ',萝莉图库,萝莉写真,Silverstar,Candydoll,EvaR,ElonaV,LauraB,U15,金子美穗,河西莉子,牧原香鱼,稚名桃子,工口小学生赛高酱'
	description = '小熊社是自由的萝莉图库,提供包括Candydoll、Silverstar、Imouto、U15等多个品牌的写真图集,涵盖了包括EvaR,ElonaV,LauraB,金子美穗,河西莉子,牧原香鱼,稚名桃子,工口小学生赛高酱等海内外知名萝莉'
	context = {
		'title':title,
		'keywords':keywords,
		'description':description,
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
		user_profile_object = UserProfile.objects.get(user=user)
		user_vip_status = user_profile_object.member_type
	except:
		user_vip_status = False
	if user_vip_status == True:
		try:
			user_profile = UserProfile.objects.get(user=user)
			member_expire = user_profile.member_expire
		except:
			member_expire = []
	else:
		member_expire = []
	#SEO
	title = '会员中心-小熊社-自由的萝莉图库|U15|白丝|Candydoll|Silverstar|Imouto.tv'
	keywords = '萝莉图库,萝莉写真,Silverstar,Candydoll,EvaR,ElonaV,LauraB,U15,金子美穗,河西莉子,牧原香鱼,稚名桃子,工口小学生赛高酱'
	description = '小熊社是自由的萝莉图库,提供包括Candydoll、Silverstar、Imouto、U15等多个品牌的写真图集,涵盖了包括EvaR,ElonaV,LauraB,金子美穗,河西莉子,牧原香鱼,稚名桃子,工口小学生赛高酱等海内外知名萝莉'
	context = {
		'title':title,
		'keywords':keywords,
		'description':description,
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
	title = '小熊社-自由的萝莉图库|U15|白丝|Candydoll|Silverstar|Imouto.tv'
	keywords = '萝莉图库,萝莉写真,Silverstar,Candydoll,EvaR,ElonaV,LauraB,U15,金子美穗,河西莉子,牧原香鱼,稚名桃子,工口小学生赛高酱'
	description = '小熊社是自由的萝莉图库,提供包括Candydoll、Silverstar、Imouto、U15等多个品牌的写真图集,涵盖了包括EvaR,ElonaV,LauraB,金子美穗,河西莉子,牧原香鱼,稚名桃子,工口小学生赛高酱等海内外知名萝莉'
	context = {
		#SEO
		'title':title,
		'keywords':keywords,
		'description':description,
		'nbar':'about',	#导航标志
	}

	return render(
		request,
		'doll_sites/about.html',
		context
	)

def member(request):
	'''会员页面'''
	current_url = request.path
	redirect_url = request.GET.get('redirect_url')
	if redirect_url == None:
		redirect_url = '/accounts/profile/'
	photo_id = redirect_url[7:]
	try:
		photo_detail = Photo.objects.get(id=photo_id)
		photo_detail.increase_views_count(5)
	except:
		photo_detail = None
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
	redirect = 'http://test.lolizhan.com' + str(redirect_url)
	notify_url = 'http://test.lolizhan.com/payment_response'
	month_order_info = 'month_member'
	month_signature = make_signature(month_price.config_value,pay_type,redirect,order_id,month_order_info,notify_url)
	season_order_info = 'season_member'
	season_signature = make_signature(season_price.config_value,pay_type,redirect,order_id_season,season_order_info,notify_url)
	year_order_info = 'year_member'
	year_signature = make_signature(year_price.config_value,pay_type,redirect,order_id_year,year_order_info,notify_url)
	#SEO
	title = '会员购买-小熊社-自由的萝莉图库|U15|白丝|Candydoll|Silverstar|Imouto.tv'
	keywords = '萝莉图库,萝莉写真,Silverstar,Candydoll,EvaR,ElonaV,LauraB,U15,金子美穗,河西莉子,牧原香鱼,稚名桃子,工口小学生赛高酱'
	description = '小熊社是自由的萝莉图库,提供包括Candydoll、Silverstar、Imouto、U15等多个品牌的写真图集,涵盖了包括EvaR,ElonaV,LauraB,金子美穗,河西莉子,牧原香鱼,稚名桃子,工口小学生赛高酱等海内外知名萝莉'
	context = {
		'title':title,
		'keywords':keywords,
		'description':description,
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
		'current_url':current_url,
		'nbar':'member',	#导航标志
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

#定时任务
try:
	# 实例化调度器
	scheduler = BackgroundScheduler()
	# 调度器使用DjangoJobStore()
	scheduler.add_jobstore(DjangoJobStore(), "default")
	
	# 循环执行任务：
	# @register_job(scheduler,'interval',seconds=60,id='task_time',replace_existing=True)
	# # 每天固定时间执行任务：
	@register_job(scheduler, 'cron', day_of_week='mon-sun', hour='04', minute='21', second='00',id='task_time')
	def temperature_count():
		# 这里写你要执行的任务
		conn = sqlite3.connect('db.sqlite3')
		# conn = psycopg2.connect(database="test_database", user="jasonpak", password="Fuck.ch1na", host="127.0.0.1", port="5432")
		c = conn.cursor()
		cursor = c.execute("SELECT views_count,history_views_count,id from doll_sites_photo")
		cursor = c.fetchall()
		today_his_count = list(cursor)
		today_static_count = []
		for static in today_his_count:
			today_views = static[0]-static[1]
			today_static = (today_views,static[2])
			updatesql = "UPDATE doll_sites_photo set yesterday_views_count = %i where ID = %i" % (today_static[0],today_static[1])
			cursor = c.execute(updatesql)
			updatesql = "UPDATE doll_sites_photo set history_views_count = %i where ID = %i" % (static[0],static[2])
			cursor = c.execute(updatesql)
			conn.commit()

		cursor = c.execute("SELECT temperature,yesterday_views_count,id from doll_sites_photo")
		cursor = c.fetchall()
		temperature = list(cursor)
		today_temperature = []
		for static in temperature:
			temper = static[0]*0.5632
			temper = round(temper,3)
			today_static = (temper+static[1],static[2])
			updatesql = "UPDATE doll_sites_photo set temperature = %f where ID = %i" % (today_static[0],today_static[1])
			cursor = c.execute(updatesql)
			conn.commit()
		conn.close()

	register_events(scheduler)
	scheduler.start()
except Exception as e:
	print(e)
	# 有错误就停止定时器
	scheduler.shutdown()