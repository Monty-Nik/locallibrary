from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.urls.base import reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.models import User
from django.views.generic import View, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from .forms import RenewBookForm  # Импорт из forms.py



@permission_required('catalog.can_edit')


class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class MyView(LoginRequiredMixin, View):
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    # Или с явным указанием tuple
    permission_required = tuple(['catalog.can_mark_returned', 'catalog.can_edit'])
    login_url = '/login/'
    redirect_field_name = 'redirect_to'


class AllBorrowedBooksListView(PermissionRequiredMixin, generic.ListView):
    """View for all borrowed books, librarian only"""
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_all_borrowed.html'
    context_object_name = 'bookinstance_list'

    def get_queryset(self):
        # Получаем ВСЕ взятые книги, включая информацию о заемщике
        return BookInstance.objects.filter(status__exact='o').select_related('book', 'borrower').order_by('due_back')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import BookInstance



class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
@login_required
def profile_view(request):
    return render(request, 'catalog/profile.html')

# Просмотр всех пользователей
users = User.objects.all()
for user in users:
    print(user.username, user.email)




class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # В первую очередь получаем базовую реализацию контекста
        context = super(BookListView, self).get_context_data(**kwargs)
        # Добавляем новую переменную к контексту и инициализируем её некоторым значением
        context['some_data'] = 'This is just some data'
        return context
def index(request):
    """
    Функция отображения для домашней страницы сайта.
    """
    # Генерация "количеств" некоторых главных объектов
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    # Доступные книги (статус = 'a')
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()  # Метод 'all()' применён по умолчанию.

    # Отрисовка HTML-шаблона index.html с данными внутри
    # переменной контекста context
    return render(
        request,
        'index.html',
        context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors},
    )

class BookDetailView(generic.DetailView):
    model = Book


def book_detail_view(request,pk):
    try:
        book_id=Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        raise Http404("Book does not exist")

    #book_id=get_object_or_404(Book, pk=pk)

    return render(
        request,
        'catalog/book_detail.html',
        context={'book':book_id,}
    )
class AuthorListView(generic.ListView):
    """Представление списка всех авторов."""
    model = Author
    paginate_by = 10
    template_name = 'catalog/author_list.html'
    context_object_name = 'author_list'

class AuthorDetailView(generic.DetailView):
    """Представление детальной информации об авторе."""
    model = Author
    template_name = 'catalog/author-detail.html'

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'12/10/2016',}
    permission_required = 'catalog.can_mark_returned'

def index(request):
    # не забывай объявлять переменные
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1

    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        'index.html',
        context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors,
            'num_visits':num_visits}, # num_visits appended
    )




@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst = get_object_or_404(BookInstance, pk=pk)

    # Если это POST запрос - обрабатываем данные формы
    if request.method == 'POST':
        # Создаем экземпляр формы и заполняем данными из запроса
        form = RenewBookForm(request.POST)

        # Проверяем валидность формы
        if form.is_valid():
            # Обрабатываем данные из form.cleaned_data
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # Перенаправляем на страницу всех взятых книг
            return HttpResponseRedirect(reverse('all-borrowed'))

    # Если это GET (или другой метод) - создаем форму по умолчанию
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst': book_inst})

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'12/10/2016',}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')