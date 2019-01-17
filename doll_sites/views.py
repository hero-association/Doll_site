from django.shortcuts import render
from .models import Series,upload_location,Photo,PhotoFile,PhotoLink,Company,Tag,Actress,SiteConfig
from django.views import generic
from django.core.paginator import Paginator

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