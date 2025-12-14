from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime
from django.forms import ModelForm
from .models import Book, BookInstance  # ← Импортируйте модели из вашего приложения!

class BookCreateForm(ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'summary', 'isbn', 'language']

class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(
        help_text="Enter a date between now and 4 weeks (default 3).",
        widget=forms.SelectDateWidget()
    )

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        return data