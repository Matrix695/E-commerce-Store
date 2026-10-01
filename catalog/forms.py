from django import forms


class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={"autocomplete": "name"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    address = forms.CharField(max_length=220, widget=forms.TextInput(attrs={"autocomplete": "street-address"}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"autocomplete": "address-level2"}))
    postal_code = forms.CharField(max_length=20, label="ZIP / postal code", widget=forms.TextInput(attrs={"autocomplete": "postal-code"}))
