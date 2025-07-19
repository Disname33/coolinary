from django.conf import settings  # Для связи с моделью пользователя
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name='Категория')
    name = models.CharField(max_length=200, db_index=True, verbose_name='Название')
    slug = models.SlugField(max_length=200, db_index=True, verbose_name='Уникальный URL')
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, verbose_name='Фото товара')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    available = models.BooleanField(default=True, verbose_name='В наличии')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    stock = models.PositiveIntegerField(default=0, verbose_name='Количество товара на складе')

    class Meta:
        ordering = ('name',)
        index_together = (('id', 'slug'),)
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])


class Color(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Уникальный URL')

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Уникальный URL')

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Цвет')
    size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Размер')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Цена')
    stock = models.PositiveIntegerField(default=0, verbose_name='Количество на складе')
    available = models.BooleanField(default=True, verbose_name='Возможность заказа')

    class Meta:
        # Убедимся, что комбинация продукта, цвета и размера уникальна
        unique_together = ('product', 'color', 'size')

    def __str__(self):
        variant_name = str(self.product.name)
        if self.color:
            variant_name += f", Цвет: {self.color.name}"
        if self.size:
            variant_name += f", Размер: {self.size.name}"
        return variant_name

    def get_price(self):
        # Возвращает цену варианта, если она установлена, иначе цену продукта
        return self.price if self.price > 0 else self.product.price


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True)  # Для анонимных пользователей
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.name}"
        return f"Anonymous Cart ({self.session_key[:5]}...)"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)  # Если есть варианты
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        # Уникальность товара/варианта в пределах одной корзины
        unique_together = ('cart', 'product', 'variant')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_item_price(self):
        # Используем цену варианта, если он есть, иначе цену продукта
        return self.variant.get_price() if self.variant else self.product.price

    def get_total_price(self):
        return self.get_item_price() * self.quantity


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Кто оставил отзыв
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)],
                                         verbose_name='Рейтинг')  # Рейтинг от 1 до 5
    text = models.TextField(blank=True, verbose_name='Отзыв о товаре')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        ordering = ('-created_at',)
        # Можно добавить уникальность: один отзыв от пользователя на товар
        unique_together = ('product', 'user')

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.name}"
