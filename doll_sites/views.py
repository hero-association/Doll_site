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
				'num_pic':num_pic,
				'num_photo':num_photo,
				'recommend_european':recommend_european,
				'recommend_japanese':recommend_japanese,
				'recommend_chinese':recommend_chinese,
				'recommend_newest':recommend_newest,
				'recommend_hotest':recommend_hotest,
				'recommend_person':recommend_person,
				'company_list':company_list,
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

def photolist(request):
	"""列表页"""
	photo_list = Photo.objects.all()
	context = {
		'photo_list':photo_list,
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
	context = {
		'photo_detail':photo_detail,
	}
	return render(
		request,
		'doll_sites/photo_detail.html',
		context
	)

def actresslist(request,pageid):
	"""演员列表页"""
	actress_list = Actress.objects.all().order_by('id')
	limit = 10
	paginator = Paginator(actress_list,limit)
	page = request.GET.get('page','1')

	result = paginator.page(page)
	context = {
		'page' : result,
		'actress_list' : actress_list,
	}

	return render(
		request,
		'doll_sites/actress_list.html',
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