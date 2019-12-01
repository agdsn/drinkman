from django import forms

from drinkman.models import User, Location


class DeliveryForm(forms.Form):
    def __init__(self, items, *args, **kwargs):
        super(DeliveryForm, self).__init__(*args, **kwargs)
        self.fields['user'] = forms.ChoiceField(label="Who are you?", choices=map(lambda u: (u.id, u.username),
                                                                                  User.objects.all().order_by(
                                                                                      'username')))
        self.fields['location'] = forms.ChoiceField(label="Location",
                                                    choices=map(lambda l: (l.id, l.name), Location.objects.all()))
        for item in items:
            self.fields["item_{}".format(item.id)] = forms.IntegerField(label=item.name, min_value=0, initial=0,
                                                                        required=False)
        self.fields['check'] = forms.BooleanField(label='Input is correct', initial=False)


class StockForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StockForm, self).__init__(*args, **kwargs)
        attributes = {'onchange': 'actionform.submit();',
                        'class':  'form-control mb-2 mr-sm-2'}
        self.fields['location'] = forms.ChoiceField(label="Location",
                                                    choices=map(lambda l: (l.id, l.name), Location.objects.all()),
                                                    widget=forms.Select(attrs=attributes))