import json

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from django.shortcuts import render, get_object_or_404
# Create your views here.
from django.template.loader import render_to_string
from sqlalchemy.sql.functions import current_user

from home.forms import SearchForm
from home.models import Setting, ContactForm, ContactMessage
from order.models import ShopCart
from product.models import Category, Product, Images,Comment

from django.db.models import Q,Count

def index(request):
    category = Category.objects.all()
    setting =Setting.objects.get(pk=1)

    category_slide = Category.objects.all().order_by('-id')[:3]
    products_slider = Product.objects.all().order_by('-id')[:3]
    # products_latest = Product.objects.all().order_by('-id')[:5]
    products_latest = Product.objects.filter(Q(category__slug='laptop-asus') | Q(category__slug='laptop-lenovo')|Q(category__slug='laptop-acer') ).order_by('?')[:6]
    pk_latest = Product.objects.filter(
        Q(category__slug='chut') | Q(category__slug='ban-phim') | Q(category__slug='tai-nghe')).order_by(
        '?')[:6]
    lk_latest = Product.objects.filter(
        Q(category__slug='cpu') | Q(category__slug='mainboard') | Q(category__slug='psu') |Q(category__slug='vga')
    |Q(category__slug='ram') | Q(category__slug='cng')).order_by(
        '?')[:6]
    products_picked = Product.objects.all().order_by('?')[:5]
    products_chunks = [products_latest[i:i + 3] for i in range(0, len(products_latest), 3)]
    pk_chunks = [pk_latest[i:i + 3] for i in range(0, len(pk_latest ), 3)]
    lk_chunks = [lk_latest[i:i + 3] for i in range(0, len(lk_latest), 3)]

    current_user = request.user  # Access User Session information
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    total = 0
    totalqty=0
    for rs in shopcart:
        total += rs.product.price * rs.quantity
        totalqty+=rs.quantity
    page='home'
    context={'setting':setting,'page':page,'category':category,
             'products_slider': products_slider,
             'category_slide': category_slide,
             'products_latest': products_latest,
             'products_picked': products_picked,'shopcart': shopcart,"totalqty":totalqty,
               'total': total,'products_chunks':products_chunks,'pk_chunks':pk_chunks,'lk_chunks':lk_chunks,
             }
    return render(request,'index.html',context)

def aboutus(request):
    category = Category.objects.all()
    setting = Setting.objects.get(pk=1)
    context = {'setting': setting,'category':category}
    return render(request, 'about.html', context)

def contact(request):

    category = Category.objects.all()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data = ContactMessage()  # create relation with model
            data.name = form.cleaned_data['name']  # get form input data
            data.email = form.cleaned_data['email']
            data.subject = form.cleaned_data['subject']
            data.message = form.cleaned_data['message']
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()  # save data to table
            messages.success(request, "Tin của bạn đã được gửi.Cảm ơn về phản hồi của bạn.")
            return HttpResponseRedirect('/contact')
    setting = Setting.objects.get(pk=1)
    form = ContactForm
    context = {'setting': setting, 'form': form, 'category': category}
    return render(request, 'contact.html', context)
def category_products(request,id,slug):
    category = Category.objects.all()
    products=Product.objects.filter(category_id=id)
    products_mo = Product.objects.all().order_by('?')[:3]

    category_all = get_object_or_404(Category, id=id, slug=slug)
    categories_all = category_all.get_descendants(include_self=True)
    products_fil = Product.objects.filter(category__in=categories_all)

    current_user = request.user  # Access User Session information
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    total = 0
    totalqty = 0
    for rs in shopcart:
        total += rs.product.price * rs.quantity
        totalqty += rs.quantity

    context = {'products': products, 'category': category,'category_all':category_all,'categories_all':categories_all ,
                'products_mo':products_mo,'products_fil':products_fil,'shopcart': shopcart,"totalqty":totalqty,
               'total': total,
               }
    return render(request,'category_product.html',context)

def search(request):
    products_mo = Product.objects.all().order_by('?')[:3]
    current_user = request.user  # Access User Session information
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    total = 0
    totalqty = 0
    for rs in shopcart:
        total += rs.product.price * rs.quantity
        totalqty += rs.quantity
    if request.method == 'POST': # check post
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query'] # get form input data
            catid = form.cleaned_data['catid']
            if catid==0:
                products=Product.objects.filter(title__icontains=query)  #SELECT * FROM product WHERE title LIKE '%query%'
            else:
                products = Product.objects.filter(title__icontains=query,category_id=catid)

            category = Category.objects.all()
            context = {'products': products, 'query':query,
                       'category': category,'products_mo':products_mo ,'shopcart': shopcart,"totalqty":totalqty,
               'total': total,}
            return render(request, 'search_products.html', context)

    return HttpResponseRedirect('/')

def search_auto(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        products = Product.objects.filter(title__icontains=q)

        results = []
        for rs in products:
            product_json = {}
            product_json = rs.title
            results.append(product_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def product_detail(request,id,slug):
    current_user = request.user  # Access User Session information
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    total = 0
    totalqty = 0
    for rs in shopcart:
        total += rs.product.price * rs.quantity
        totalqty += rs.quantity
    query = request.GET.get('q')
    category = Category.objects.all()
    product=Product.objects.get(pk=id)
    products_picked = Product.objects.all().order_by('?')[:4]
    images=Images.objects.filter(product_id=id)
    comments = Comment.objects.filter(product_id=id, status="New")

    context = {'product': product, 'category': category,
                'products_picked':products_picked,
                'images':images,'comments':comments,'shopcart': shopcart,"totalqty":totalqty,
               'total': total,

               }
    if product.variant != "None":  # Product have variants
        if request.method == 'POST':  # if we select color
            variant_id = request.POST.get('productid')
            variant = Product.objects.get(id=variant_id)  # selected product by click color radio
            colors = Product.objects.filter(product_id=id, size_id=variant.size_id)
            sizes = Product.objects.raw('SELECT * FROM  product_variants  WHERE product_id=%s GROUP BY size_id', [id])
            query += variant.title + ' Size:' + str(variant.size) + ' Color:' + str(variant.color)
        else:
            variants = Product.objects.filter(product_id=id)
            colors = Product.objects.filter(product_id=id, size_id=variants[0].size_id)
            sizes = Product.objects.raw('SELECT * FROM  product_variants  WHERE product_id=%s GROUP BY size_id', [id])
            variant =Product.objects.get(id=variants[0].id)
        context.update({'sizes': sizes, 'colors': colors,
                        'variant': variant, 'query': query
                        })
    return render(request,'product_detail.html',context)

