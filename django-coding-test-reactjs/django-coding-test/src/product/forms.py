from django.forms import forms, ModelForm, CharField, TextInput, Textarea, BooleanField, CheckboxInput

from product.models import Variant,  Product, ProductVariant



class VariantForm(ModelForm):
    class Meta:
        model = Variant
        fields = '__all__'
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'form-control'}),
            'active': CheckboxInput(attrs={'class': 'form-check-input', 'id': 'active'})
        }


from django import forms
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
    variant_color = forms.CharField(
        label='Color',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    variant_style = forms.CharField(
        label='Style',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    variant_size = forms.CharField(
        label='Size',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
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

    def clean(self):
        cleaned_data = super().clean()
        sku = cleaned_data.get('sku')
        product_title = cleaned_data.get('product_title')
        variant_color = cleaned_data.get('variant_color')
        variant_style = cleaned_data.get('variant_style')
        variant_size = cleaned_data.get('variant_size')

        variant_input = f"{variant_color}-{variant_style}-{variant_size}"
        cleaned_data['variant_input'] = variant_input

        if Product.objects.filter(sku=sku).exists():
            self.add_error('sku', 'A product with this SKU already exists.')
        
        return cleaned_data