from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Problem, CustomUser, ProblemType
from django.core.validators import FileExtensionValidator
import os

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[field].label
            })

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)

class ProblemForm(forms.ModelForm):
    images = MultipleFileField(
        required=False,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
        ],
        help_text='Максимум 3 фото в формате JPG/PNG (до 5MB каждое)'
    )

    class Meta:
        model = Problem
        fields = ['problem_type', 'short_description', 'full_description', 'address']
        widgets = {
            'problem_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'problem-type'
            }),
            'short_description': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '200',
                'placeholder': 'Краткое описание (до 200 символов)'
            }),
            'full_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'maxlength': '1000',
                'placeholder': 'Подробное описание (до 1000 символов)'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_address',
                'placeholder': 'Введите адрес...',
                'autocomplete': 'off',
                'data-yandex-geocode': 'true'  # Новый атрибут для JS
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ProblemType.create_default_types()

    def clean_images(self):
        images = self.cleaned_data.get('images', [])
        if not isinstance(images, list):
            images = [images]

        if len(images) > 3:
            raise forms.ValidationError("Можно загрузить не более 3 изображений!")

        for img in images:
            ext = os.path.splitext(img.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png']:
                raise forms.ValidationError("Поддерживаются только JPG/PNG файлы!")
            if img.size > 5 * 1024 * 1024:
                raise forms.ValidationError(f"Файл {img.name} слишком большой (макс. 5MB)!")
        return images