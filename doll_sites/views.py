from django.shortcuts import render
from .models import Series,upload_location,Photo,PhotoFile,PhotoLink,Company,Tag,Actress,SiteConfig,SlideBanner
from django.views import generic
from django.core.paginator import Paginator
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
import sqlite3
import psycopg2
import random

# Create your views here.

def index(request):
	"""网站主页"""
	num_pic = PhotoLink.objects.all().count()
	num_photo = Photo.objects.all().count()
	company_list = Company.objects.all()[:5]
	silde_banner = SlideBanner.objects.all()
	recommend_european = Photo.objects.filter(series=1).order_by('?')[:5]
	recommend_japanese = Photo.objects.filter(series=2).order_by('?')[:5]
	recommend_chinese = Photo.objects.filter(series=3).order_by('?')[:5]
	recommend_newest = Photo.objects.order_by('-date_added')[:5]
	recommend_hotest = Photo.objects.order_by('-views_count')[:5]
	recommend_person = Actress.objects.order_by('?')[:4]
	context = {
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

# class PhotoIndexView(generic.ListView):
# 	model = Photo
# 	template_name = 'doll_sites/index.html'
# 	# queryset = Photo.objects.order_by('-date_added')
# 	context_object_name = 'Photo_index'

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
	hot_actress = Actress.objects.all().order_by('?')[:6]
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

	context = {
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

# class PhotoListView(generic.ListView):
# 	model = Photo
# 	template_name = 'doll_sites/photo_list.html'
# 	# queryset = Photo.objects.order_by('date_added')
# 	context_object_name = 'Photo_list'

# 	ordering = ['-id'] 

# 	def get_right_recommend(self):
# 		right_recommend = Photo_list[0:3]
# 		return right_recommend

def photodetail(request,photoid):
	"""详情页"""
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
	#查询当前演员的相关图集
	current_actress = photo_detail.model_name.all().order_by('pk')
	related_album = []
	for actress in current_actress:
		p = Photo.objects.filter(model_name = Actress.objects.get(actress_name_ch = actress)).order_by('-views_count')
		related_album += p
	current_album = Photo.objects.filter(id=photoid)
	related_album = list(set(related_album) - set(current_album))[:10]
	#热搜标签
	hot_actress = Actress.objects.all().order_by('?')[:6]
	#相册标签
	photo_tag = photo_detail.photo_tag.all()
	# photo_tag = list(set(photo_tag))

	context = {
		'buy_links':buy_links,		#购买链接列表
		'bundle_links':bundle_links,		#Bundle链接列表
		'photo_detail':photo_detail,		#当前相册
		'related_album':related_album,		#当前演员的相关图集
		'current_actress':current_actress,		
		'hot_actress':hot_actress,		#热搜标签
		'photo_tag':photo_tag,		#相册标签
	}

	return render(
		request,
		'doll_sites/photo_detail.html',
		context
	)

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
	@register_job(scheduler, 'interval', second='10',id='task_time')
	# # 每天固定时间执行任务：
	# @register_job(scheduler, 'cron', day_of_week='mon-sun', hour='18', minute='31', second='40',id='task_time')
	def temperature_count():
		# 这里写你要执行的任务
		# conn = sqlite3.connect('db.sqlite3')
		conn = psycopg2.connect(database="really_test_database", user="jasonpak", password="Fuck.ch1na", host="127.0.0.1", port="5432")
		c = conn.cursor()
		#截至当日总计
		cursor = c.execute("SELECT views_count,id from doll_sites_photo")
		cursor = list(cursor)
		now_view = []
		for row in cursor:
			now_view.append((row))
		#截至昨日总计
		cursor = c.execute("SELECT history_views_count,id from doll_sites_photo")
		cursor = list(cursor)
		history_view = []
		for row in cursor:
			history_view.append(row)
		#今日统计
		today_counts = []
		today_pk = []
		n = 0
		for view in now_view:
			today_pk.append(view[1])
			view = view[0] - history_view[n][0]
			today_counts.append(view)
			n += 1
		#当前热度
		cursor = c.execute("SELECT temperature,id from doll_sites_photo")
		cursor = list(cursor)
		temperature = []
		for row in cursor:
			temperature.append(row)
		n = 0
		for temper in temperature:
			pk = temper[1]
			temper = temper[0]*0.5632 + today_counts[n]
			temper = round(temper,3)
			updatesql = "UPDATE doll_sites_photo set temperature = %f where ID = %i" % (temper,pk)
			cursor = c.execute(updatesql)
			conn.commit()
			n += 1
		#更新history_view
		for view in now_view:
			pk = view[1]
			view = view[0]
			updatesql = "UPDATE doll_sites_photo set history_views_count = %f where ID = %i" % (view,pk)
			cursor = c.execute(updatesql)
			conn.commit()
		conn.close()

	register_events(scheduler)
	scheduler.start()
except Exception as e:
	print(e)
	# 有错误就停止定时器
	scheduler.shutdown()

# class PhotoDetailView(generic.DetailView):
# 	model = Photo
# 	template_name = 'doll_sites/photo_detail.html'
# 	context_object_name = 'Photo_detail'

# def photo_detail(request,pk):
#     try:
#         photo_id = Photo.objects.get(pk=pk)
#     except Photo.DoesNotExist:
#         raise Http404("Photo does not exist")

#     # photo_details = models.Photo.objects.get(Photo, pk=pk)
    
#     return render(
#         request,
#         'doll_sites/photo_detail.html',
#         context = {'photo_details':photo_id,}
#     )