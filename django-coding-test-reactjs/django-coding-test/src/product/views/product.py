from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator
from product.models import Variant, Product, ProductImage, ProductVariant, ProductVariantPrice
from django.views import View
from django.db.models import Q
from product.forms import ProductForm
from django.db import IntegrityError


class ListProductView(View):
    template_name = 'products/list.html'

    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        paginator = Paginator(products, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'products': page_obj,
        }
        return render(request, self.template_name, context)
class EditProductView(View):
    template_name = 'products/edit.html'
    list_template = 'products/list.html'

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product_variant = ProductVariant.objects.filter(product=product).first()
        product_variant_price = ProductVariantPrice.objects.filter(product=product).first()

        form_data = {
            'product_title': product.product_title,
            'sku': product.sku,
            'product_description': product.product_description,
            'variant_input': product_variant.variant_title if product_variant else '',
            'price': product_variant_price.price if product_variant_price else '',
            'stock': product_variant_price.stock if product_variant_price else ''
        }

        form = ProductForm(initial=form_data)
        return render(request, self.template_name, {'form': form, 'product': product})

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(request.POST)
        if form.is_valid():
            product.product_title = form.cleaned_data['product_title']
            product.sku = form.cleaned_data['sku']
            product.product_description = form.cleaned_data['product_description']
            product.save()

            variant = ProductVariant.objects.filter(product=product).first()
            if not variant:
                variant = ProductVariant(product=product)
                variant.variant_title = form.cleaned_data['variant_input']
                variant.save()

                variant_price = ProductVariantPrice.objects.filter(product=product).first()
            if not variant_price:
                variant_price = ProductVariantPrice(product=product, product_variant_one=variant)
                variant_price.price = form.cleaned_data['price']
                variant_price.stock = form.cleaned_data['stock']
                variant_price.save()

              # Redirect to the product list view
            products = Product.objects.all()
            paginator = Paginator(products, 5)  # Show 5 products per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {
            'products': page_obj,
            
               }
            
            return render(request, self.list_template, context)
        return render(request, self.template_name, {'form': form, 'product': product})

        

class CreateProductView(View):
    create_template = 'products/create.html'

    def get(self, request):
        form = ProductForm()
        return render(request, self.create_template, {'form': form, 'product': True, 'variants': Variant.objects.filter(active=True)})

    def post(self, request):
        form = ProductForm(request.POST)
        if form.is_valid():
            try:
                product = Product(
                    product_title=form.cleaned_data['product_title'],
                    sku=form.cleaned_data['sku'],
                    product_description=form.cleaned_data['product_description']
                )
                product.save()

                variant = Variant(
                    title=request.POST.get('variant_color', ''),
                    description=request.POST.get('variant_style', ''),
                    active=True
                )
                variant.save()

                product_variant = ProductVariant(
                    variant_title=request.POST.get('variant_input', ''),
                    variant=variant,
                    product=product
                )
                product_variant.save()

                product_variant_price = ProductVariantPrice(
                    product_variant_one=product_variant,
                    price=form.cleaned_data['price'],
                    stock=form.cleaned_data['stock'],
                    product=product
                )
                product_variant_price.save()
                
                # Reset the form
                form = ProductForm()
                return render(request, self.create_template, {
                    'form': form,
                    'product': True,
                    'variants': Variant.objects.filter(active=True),
                    'success_message': 'Product created successfully!'
                })

            except IntegrityError:
                form.add_error(None, 'A product with this SKU or a product variant with this title already exists.')
        
        return render(request, self.create_template, {
            'form': form,
            'product': True,
            'variants': Variant.objects.filter(active=True)
        })
class FilterProductView(View):
    filter_template = 'products/filter.html'
    list_template = 'products/list.html'

    def get(self, request):
        variants = ProductVariant.objects.all()
        
        context = {
            'variants': variants
        }
        
        return render(request, self.filter_template, context)

    def post(self, request):
        products = Product.objects.all()
        variants = ProductVariant.objects.all()

        product_title = request.POST.get('title')
        variant_title = request.POST.get('variant')
        price_from = request.POST.get('price_from')
        price_to = request.POST.get('price_to')

        # Apply filters
        if product_title:
            products = products.filter(product_title__icontains=product_title)

        if variant_title and variant_title != " -- Select a Variant --":
            products = products.filter(productvariant__variant_title__icontains=variant_title).distinct()

        if price_from or price_to:
            try:
                price_from = float(price_from) if price_from else 0
                price_to = float(price_to) if price_to else float('inf')
                product_ids = ProductVariantPrice.objects.filter(
                    price__gte=price_from, price__lte=price_to
                ).values_list('product_id', flat=True)
                products = products.filter(id__in=product_ids)
            except ValueError:
                pass  # Handle invalid price range input

        # Implement pagination
        paginator = Paginator(products, 10)  # Show 10 products per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'products': page_obj,
            'variants': variants,
            'product_title': product_title,
            'variant_title': variant_title,
            'price_from': price_from,
            'price_to': price_to,
        }

        return render(request, self.list_template, context)
