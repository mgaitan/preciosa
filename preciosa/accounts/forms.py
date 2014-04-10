from django import forms

import account.forms


class SignupForm(account.forms.SignupForm):
    subscribe_to_newsletter = forms.BooleanField(
        required=False
    )
