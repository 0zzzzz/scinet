from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from authapp.models import SNUser, SNUserProfile, SNMessage


class SNUserLoginForm(AuthenticationForm):
    class Meta:
        model = SNUser
        fields = ('username', 'password')


    def __init__(self, *args, **kwargs):
        super(SNUserLoginForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''


class SNUserRegisterForm(UserCreationForm):
    class Meta:
        model = SNUser
        fields = ('username', 'first_name', 'last_name', 'avatar', 'email', 'age', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''

    def save(self, *args, **kwargs):
        user = super().save(*args, **kwargs)
        user.is_active = True
        user.save()
        return user


class SNUserEditForm(UserChangeForm):
    class Meta:
        model = SNUser
        fields = ('username', 'first_name', 'last_name', 'patronymic', 'avatar', 'email', 'age',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''
            if field_name == 'password':
                field.widget = forms.HiddenInput()


class SNUserProfileEditForm(forms.ModelForm):
    class Meta:
        model = SNUserProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''


class MessageForm(forms.ModelForm):
    class Meta:
        model = SNMessage
        fields = ['message']
        labels = {'message': ""}
