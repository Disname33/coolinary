# в views.py
from django.contrib.auth.decorators import login_required  # Если отзывы только для зарегистрированных
# в views.py
from django.contrib.auth.decorators import user_passes_test
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST  # Для POST запросов

from .forms import ProductForm, ProductVariantFormSet
from .models import Cart, CartItem, Review
from .models import Product, Category, ProductVariant


def is_admin(user):
    return user.is_staff or user.is_superuser


@user_passes_test(is_admin)
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = ProductVariantFormSet(request.POST, request.FILES, prefix='variants')
        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.instance = product  # Связываем варианты с созданным продуктом
            formset.save()
            return redirect('shop:product_detail', id=product.id, slug=product.slug)  # Редирект на страницу товара
    else:
        form = ProductForm()
        formset = ProductVariantFormSet(prefix='variants')

    return render(request, 'shop/product_form.html', {'form': form, 'formset': formset})


@user_passes_test(is_admin)
def edit_product(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ProductVariantFormSet(request.POST, request.FILES, instance=product, prefix='variants')
        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.save()  # Сохраняем изменения в вариантах
            return redirect('shop:product_detail', id=product.id, slug=product.slug)
    else:
        form = ProductForm(instance=product)
        formset = ProductVariantFormSet(instance=product, prefix='variants')

    return render(request, 'shop/product_form.html', {'form': form, 'formset': formset, 'product': product})


@login_required  # Отзывы могут оставлять только зарегистрированные пользователи
@require_POST
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    rating = request.POST.get('rating')
    text = request.POST.get('text')

    if not rating:
        # Обработать ошибку: рейтинг обязателен
        pass  # Пока просто проигнорируем

    try:
        rating = int(rating)
        if not (1 <= rating <= 5):
            # Обработать ошибку: некорректный рейтинг
            pass
    except (ValueError, TypeError):
        # Обработать ошибку: некорректный формат рейтинга
        pass

    # Проверка, оставлял ли пользователь уже отзыв на этот товар (опционально, если unique_together в модели)
    if Review.objects.filter(product=product, user=request.user).exists():
        # Обработать ошибку: пользователь уже оставлял отзыв
        pass

    review = Review.objects.create(
        product=product,
        user=request.user,
        rating=rating,
        text=text
    )
    # Редирект на страницу товара
    return redirect('shop:product_detail', id=product.id, slug=product.slug)


# Вспомогательная функция для получения или создания корзины
def _get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def cart_detail(request):
    cart = _get_or_create_cart(request)
    return render(request, 'shop/cart_detail.html', {'cart': cart})


@require_POST  # Обязательно POST запрос
def add_to_cart(request, product_id):
    cart = _get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    variant_id = request.POST.get('variant_id')
    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product)

    # Проверка наличия на складе (на уровне варианта или продукта)
    if variant:
        if quantity > variant.stock:
            # Обработать ошибку: недостаточно на складе
            pass  # Пока просто проигнорируем или выведем сообщение
    elif quantity > product.stock:
        # Обработать ошибку: недостаточно на складе
        pass  # Пока просто проигнорируем или выведем сообщение

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    else:
        cart_item.quantity = quantity
        cart_item.save()

    return redirect('shop:cart_detail')  # Редирект на страницу корзины или откуда пришел запрос


@require_POST
def update_cart(request, item_id):
    cart = _get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart_item.delete()
    else:
        # Добавить проверку наличия на складе при обновлении
        if cart_item.variant:
            if quantity > cart_item.variant.stock:
                # Обработать ошибку
                pass
            else:
                cart_item.quantity = quantity
                cart_item.save()
        else:
            if quantity > cart_item.product.stock:
                # Обработать ошибку
                pass
            else:
                cart_item.quantity = quantity
                cart_item.save()

    return redirect('shop:cart_detail')


@require_POST
def remove_from_cart(request, item_id):
    cart = _get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    return redirect('shop:cart_detail')


def search_results(request):
    query = request.GET.get('q')
    products = Product.objects.filter(available=True)  # Изначально все доступные товары

    if query:
        # Создаем векторы для полей, по которым ищем
        search_vector = SearchVector('name', 'description')
        # Создаем поисковый запрос
        search_query = SearchQuery(query)
        # Выполняем поиск и ранжируем результаты
        products = products.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query).order_by('-rank')
        # Можно также добавить fallback для других БД или более простого поиска:
        # products = Product.objects.filter(
        #     Q(name__icontains=query) | Q(description__icontains=query),
        #     available=True
        # )
    else:
        products = Product.objects.none()  # Если запрос пустой, не показываем ничего

    return render(request, 'shop/search_results.html', {'query': query, 'products': products})


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'shop/product_list.html', {'category': category,
                                                      'categories': categories,
                                                      'products': products})


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'shop/product_detail.html', {'product': product})


def main_page(request):
    categories = get_object_or_404(Category)
    return render(request, 'shop/shop_base.html', {'categories': categories})
