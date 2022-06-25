from django import forms
from django.contrib.auth.forms import UserChangeForm

from authapp.models import SNUser
from blogapp.models import SNPosts, SNSections


class SNSectionForm(forms.ModelForm):
    class Meta:
        model = SNSections
        fields = ('name', 'title', 'description')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''


class SNPostAdminForm(forms.ModelForm):
    class Meta:
        model = SNPosts
        fields = ('name', 'text', 'section', 'image', 'user')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''


class SNUserAdminEditForm(UserChangeForm):
    class Meta:
        model = SNUser
        fields = ('username', 'first_name', 'last_name', 'patronymic', 'avatar', 'email', 'age', 'is_moderator')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''
            if field_name == 'password':
                field.widget = forms.HiddenInput()
            if field_name == 'is_moderator':
                field.widget = forms.CheckboxInput()

