import datetime

from django.test import TestCase

# Create your tests here.

from catalog.models import Author, BookInstance, Book, Genre, Language
from django.urls import reverse
from django.contrib.auth.models import Permission, \
    User  # Required to grant the permission needed to set a book as returned.

class RenewBookInstancesViewTest(TestCase):

    def setUp(self):
        #Создание пользователя
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()

        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        #Создание книги
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(title='Book Title', summary = 'My book summary', isbn='ABCDEFG', author=test_author, language=test_language,)
        #Создание жанра Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre=genre_objects_for_book
        test_book.save()

        #Создание объекта BookInstance для для пользователя test_user1
        return_date= datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1=BookInstance.objects.create(book=test_book,imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=test_user1, status='o')

        #Создание объекта BookInstance для для пользователя test_user2
        return_date= datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2=BookInstance.objects.create(book=test_book,imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=test_user2, status='o')


class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Create 13 authors for pagination tests
        number_of_authors = 13
        for author_num in range(number_of_authors):
            Author.objects.create(first_name='Christian %s' % author_num, last_name = 'Surname %s' % author_num,)

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/catalog/authors/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue( len(resp.context['author_list']) == 10)

    def test_lists_all_authors(self):
        #Get second page and confirm it has (exactly) remaining 3 items
        resp = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue( len(resp.context['author_list']) == 3)

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        # Проверка, что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Проверка, что изначально у нас нет книг в списке
        self.assertTrue('bookinstance_list' in resp.context)
        self.assertEqual(len(resp.context['bookinstance_list']), 0)

        # Теперь все книги "взяты на прокат"
        get_ten_books = BookInstance.objects.all()[:10]

        for copy in get_ten_books:
            copy.status = 'o'
            copy.save()

        # Проверка, что все забронированные книги в списке
        resp = self.client.get(reverse('my-borrowed'))
        # Проверка, что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Проверка успешности ответа
        self.assertEqual(resp.status_code, 200)

        self.assertTrue('bookinstance_list' in resp.context)

        # Подтверждение, что все книги принадлежат testuser1 и взяты "на прокат"
        for bookitem in resp.context['bookinstance_list']:
            self.assertEqual(resp.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):

        # Изменение статуса на "в прокате"
        for copy in BookInstance.objects.all():
            copy.status = 'o'
            copy.save()

        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        # Пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Подтверждение, что из всего списка показывается только 10 экземпляров
        self.assertEqual(len(resp.context['bookinstance_list']), 10)

        last_date = 0
        for copy in resp.context['bookinstance_list']:
            if last_date == 0:
                last_date = copy.due_back
            else:
                self.assertTrue(last_date <= copy.due_back)


class AuthorCreateViewTest(TestCase):

    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Создаем суперпользователя для тестов с полными правами
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

        # Получаем разрешение can_mark_returned
        content_type = ContentType.objects.get_for_model(Author)
        self.permission = Permission.objects.get(
            codename='can_mark_returned',
            content_type=content_type,
        )

    def test_author_create_url_exists_at_desired_location(self):
        """Тест: URL отображения создания автора существует"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/catalog/author/create/')
        self.assertEqual(response.status_code, 200)

    def test_author_create_view_accessible_by_name(self):
        """Тест: Отображение доступно по имени"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)

    def test_author_create_uses_correct_template(self):
        """Тест: Используется правильный шаблон"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_form.html')

    def test_author_create_requires_permission(self):
        """Тест: Требуется разрешение для доступа"""
        # Пользователь без разрешения
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 302)  # Перенаправление на логин

        # Пользователь с разрешением
        self.user.user_permissions.add(self.permission)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)

    def test_author_create_has_initial_date_of_death(self):
        """Тест: Начальное значение даты смерти установлено"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)

        # Проверяем, что начальное значение присутствует в форме
        self.assertContains(response, '12/10/2016')

    def test_author_create_form_submission(self):
        """Тест: Успешное создание автора через форму"""
        self.client.login(username='admin', password='adminpass123')

        form_data = {
            'first_name': 'Test',
            'last_name': 'Author',
            'date_of_birth': '1980-01-01',
            'date_of_death': '2020-01-01',
        }

        response = self.client.post(reverse('author-create'), data=form_data)

        # Проверяем редирект после успешного создания
        self.assertEqual(response.status_code, 302)

        # Проверяем, что автор создан в базе данных
        self.assertTrue(Author.objects.filter(first_name='Test', last_name='Author').exists())

    def test_author_create_redirects_to_author_detail_on_success(self):
        """Тест: Перенаправление на детальную страницу автора после создания"""
        self.client.login(username='admin', password='adminpass123')

        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1975-05-15',
            'date_of_death': '2020-01-01',
        }

        response = self.client.post(reverse('author-create'), data=form_data)

        # Получаем созданного автора
        author = Author.objects.get(first_name='John', last_name='Doe')

        # Проверяем, что произошел редирект на детальную страницу автора
        self.assertRedirects(response, reverse('author-detail', kwargs={'pk': author.pk}))

    def test_author_create_invalid_form_submission(self):
        """Тест: Неудачная попытка создания автора (невалидные данные)"""
        self.client.login(username='admin', password='adminpass123')

        # Отправляем пустую форму
        form_data = {}
        response = self.client.post(reverse('author-create'), data=form_data)

        # Должны остаться на той же странице с ошибками
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'first_name', 'This field is required.')
        self.assertFormError(response, 'form', 'last_name', 'This field is required.')

    def test_author_create_view_uses_permission_required_mixin(self):
        """Тест: Отображение использует PermissionRequiredMixin"""
        from catalog.views import AuthorCreate
        self.assertEqual(AuthorCreate.permission_required, 'catalog.can_mark_returned')

    def test_author_create_view_uses_correct_model(self):
        """Тест: Отображение использует правильную модель"""
        from catalog.views import AuthorCreate
        from catalog.models import Author
        self.assertEqual(AuthorCreate.model, Author)

    def test_author_create_view_fields(self):
        """Тест: Отображение включает все поля"""
        from catalog.views import AuthorCreate
        self.assertEqual(AuthorCreate.fields, '__all__')