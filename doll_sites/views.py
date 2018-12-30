from django.shortcuts import render
from .models import Series,upload_location,Photo,PhotoFile,PhotoLink,Company,Tag,Actress
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
	recommend_newest = Photo.objects.order_by('date_added')[:5]
	recommend_hotest = Photo.objects.order_by('?')[:5]
	recommend_persons = Photo.objects.order_by('?')[6:16:2]
	recommend_person = recommend_persons[:4]
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
	paginator = Paginator(photo_list,limit)
	# page = request.GET.get('page','1')
	current_photo_list = paginator.page(pageid)
	context = {
		'current_photo_list':current_photo_list,		#分页的相册列表
		'photo_list':photo_list,		#未分页的相册列表
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
	photo_detail = Photo.objects.filter(id=photoid).all()[0]
	photo_detail.increase_views_count()
	context = {
		'photo_detail':photo_detail,		#当前相册下的，所有照片列表
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
	paginator = Paginator(actress_list,limit)
	# page = request.GET.get('page','1')

	current_actress_list = paginator.page(pageid)
	context = {
		'current_actress_list' : current_actress_list,		#分页的偶像列表
		'actress_list' : actress_list,		#未分页的偶像列表
	}

	return render(
		request,
		'doll_sites/actress_list.html',
		context
	)

def actressdetail(request,actressid):
	"""演员详情页"""
	current_actress = Actress.objects.filter(id=actressid)
	related_album = Photo.objects.filter(actress=actressid)

	context = {
		'related_album' : related_album,	#当前偶像的相册列表
		'current_actress' : current_actress_list,		#当前偶像
	}

	return render(
		request,
		'doll_sites/actress_detail.html',
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