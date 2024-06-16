from django import forms
from django.forms import ModelForm, TextInput, Textarea, CheckboxInput
from product.models import Variant, ProductVariant

class VariantForm(ModelForm):
    class Meta:
        model = Variant
        fields = '__all__'
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'form-control'}),
            'active': CheckboxInput(attrs={'class': 'form-check-input', 'id': 'active'})
        }

class ProductForm(forms.Form):
    product_title = forms.CharField(
        label='Product Title',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    sku = forms.CharField(
        label='SKU',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    product_description = forms.CharField(
        label='Description',
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )
    variant_input = forms.CharField(
        label='Variant Input',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'variantInput'})
    )
    price = forms.DecimalField(
        label='Price',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    stock = forms.IntegerField(
        label='Stock',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def clean_sku(self):
        sku = self.cleaned_data.get('sku')
        if Product.objects.filter(sku=sku).exists():
            raise forms.ValidationError('A product with this SKU already exists.')
        return sku

    def clean_variant_input(self):
        variant_input = self.cleaned_data.get('variant_input')
        if ProductVariant.objects.filter(variant_title=variant_input).exists():
            raise forms.ValidationError
