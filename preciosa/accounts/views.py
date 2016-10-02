from .forms import SignupForm

# from newsletter.models import Subscription, Newsletter

import account.views


class SignupView(account.views.SignupView):
    form_class = SignupForm

    def after_signup(self, form):

        if form.cleaned_data["subscribe_to_newsletter"]:
            pass 

            # if not Subscription.objects.filter(
            #     email_field=form.cleaned_data['email']
            # ).exists():
            #     Subscription.objects.create(
            #         user=self.created_user,
            #         newsletter=Newsletter.objects.first(),
            #         subscribed=True
            #     )
        super(SignupView, self).after_signup(form)
