from django import forms

from drinkman.models import User, Location


class DeliveryForm(forms.Form):
    def __init__(self, items, *args, **kwargs):
        super(DeliveryForm, self).__init__(*args, **kwargs)
        self.fields['user'] = forms.ChoiceField(label="Who are you?",
                                                widget=forms.Select(attrs={'class': 'form-control'}),
                                                choices=map(lambda u: (u.id, u.username),
                                                            User.objects.all().order_by(
                                                                'username')))
        self.fields['location'] = forms.ChoiceField(label="Location",
                                                    widget=forms.Select(attrs={'class': 'form-control'}),
                                                    choices=map(lambda l: (l.id, l.name), Location.objects.all()))
        for item in items:
            self.fields["item_{}".format(item.id)] = forms.IntegerField(label=item.name, min_value=0, initial=0,
                                                                        widget=forms.NumberInput(
                                                                            attrs={'class': 'form-control'}),
                                                                        required=False)
        self.fields['check'] = forms.BooleanField(label='Input is correct', initial=False)


class StockForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StockForm, self).__init__(*args, **kwargs)
        attributes = {'onchange': 'actionform.submit();',
                      'class': 'form-control mb-2 mr-sm-2'}
        self.fields['location'] = forms.ChoiceField(label="Location",
                                                    choices=map(lambda l: (l.id, l.name), Location.objects.all()),
                                                    widget=forms.Select(attrs=attributes))

class NewUserForm(forms.Form):
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="E-Mail", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
