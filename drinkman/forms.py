from django import forms
from django.db.models.functions import Lower

from drinkman.models import User, Location


class DeliveryForm(forms.Form):
    def __init__(self, items, *args, **kwargs):
        super(DeliveryForm, self).__init__(*args, **kwargs)
        self.fields['user'] = forms.ChoiceField(label="Who are you?",
                                                widget=forms.Select(attrs={'class': 'form-control'}),
                                                choices=map(lambda u: (u.id, u.username),
                                                            User.objects.order_by(Lower('username')).all().order_by(
                                                                'username')))
        self.fields['location'] = forms.ChoiceField(label="Location",
                                                    widget=forms.Select(attrs={'class': 'form-control'}),
                                                    choices=map(lambda l: (l.id, l.name), Location.objects.all()))
        for item in items:
            self.fields["item_{}".format(item.id)] = forms.IntegerField(label=item.name, initial=0,
                                                                        widget=forms.NumberInput(
                                                                            attrs={'class': 'form-control'}),
                                                                        required=False)
        self.fields['check'] = forms.BooleanField(label='Input is correct', initial=False)
        self.fields['set'] = forms.BooleanField(label='Set instead of increase', initial=False, required=False)


class StockForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StockForm, self).__init__(*args, **kwargs)
        attributes = {'onchange': 'this.form.submit();',
                      'class': 'form-control mb-2 mr-sm-2'}
        self.fields['location'] = forms.ChoiceField(label="",
                                                    choices=map(lambda l: (l.id, l.name), Location.objects.all()),
                                                    widget=forms.Select(attrs=attributes))


class UserForm(forms.Form):
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="E-Mail", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    image_url = forms.CharField(label="Profilbild URL (optional)", widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)


class TransferForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(TransferForm, self).__init__(*args, **kwargs)
        self.fields['to_user'] = forms.ChoiceField(label="Who should receive money?",
                                                widget=forms.Select(attrs={'class': 'form-control'}),
                                                choices=map(lambda u: (u.id, u.username),
                                                            User.objects.order_by(Lower('username')).all().order_by(
                                                                'username')))

        self.fields['amount'] = forms.DecimalField(label='Amount in EUR', initial=5, required=True, decimal_places=2)
