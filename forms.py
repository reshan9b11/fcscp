from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *

from accounts.models import UserProfile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        )

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user

class EditProfileForm(UserChangeForm):
    template_name='/omething/else'

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'password'
            
        )   


class TransferFundsForm(forms.Form):
    # from_account=forms.IntegerField(required=True)
    to_account=forms.IntegerField(required=True)
    amount=forms.IntegerField(required=True)
    publickey=forms.CharField(required=True,widget=forms.Textarea)

class ViewTransactionsForm(forms.Form):
    from_account=forms.IntegerField(required=True)


#class SearchTransactionForm(forms.Form):
    #amount=forms.IntegerField(required=True)
    
class SearchTransactionInternalForm(forms.Form):
    from_account=forms.IntegerField(required=True)
    
class SubmitRequestForm(forms.Form):
    from_account=forms.IntegerField(required=True)
    amount=forms.IntegerField(required=True)             