from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from .models import Category
from .filters import ProductFilter
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver

from .forms import ProductForm
from .models import Product
from django.http import HttpResponse
from django.views import View
from .tasks import printer
from datetime import datetime, timedelta
from django.contrib.auth import logout
from django.shortcuts import redirect


class ProductsList(ListView):
    model = Product
    ordering = 'name'
    template_name = 'shop/products.html'
    context_object_name = 'products'
    # paginate_by = 2

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     self.filterset = ProductFilter(self.request.GET, queryset)
    #     return self.filterset.qs
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['filterset'] = self.filterset
    #     return context


class ProductDetail(DetailView):
    model = Product
    template_name = 'shop/product.html'
    context_object_name = 'product'


class ProductCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('shop.add_product',)
    form_class = ProductForm
    model = Product
    template_name = 'shop/product_edit.html'


class ProductUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('shop.change_product',)
    form_class = ProductForm
    model = Product
    template_name = 'shop/product_edit.html'


class ProductDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('shop.delete_product',)
    model = Product
    template_name = 'shop/product_delete.html'
    success_url = reverse_lazy('product_list')



class IndexView(View):
    def get(self, request):
        printer.apply_async([10], eta = datetime.now() + timedelta(seconds=5))
        hello.delay()
        return HttpResponse('Hello!')



@receiver(post_save, sender=Product)
def product_created(instance, created, **kwargs):
    if not created:
        return

    emails = User.objects.filter().values_list('email', flat=True)

    subject = f'Новый товар в категории {instance.category}'

    text_content = (
        f'Товар: {instance.name}\n'
        f'Цена: {instance.price}\n\n'
        f'Ссылка на товар: http://127.0.0.1:8000{instance.get_absolute_url()}'
    )
    html_content = (
        f'Товар: {instance.name}<br>'
        f'Цена: {instance.price}<br><br>'
        f'<a href="http://127.0.0.1{instance.get_absolute_url()}">'
        f'Ссылка на товар</a>'
    )
    for email in emails:
        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()