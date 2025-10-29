from django.test import TestCase
from django.urls import reverse
from catalog.models import Author

class AuthorModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Author.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, 'first name')

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEqual(field_label, 'died')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEqual(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = '%s, %s' % (author.last_name, author.first_name)
        self.assertEqual(expected_object_name, str(author))

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(author.get_absolute_url(), '/catalog/author/1')

    from django.test import TestCase
    from django.urls import reverse
    from django.contrib.auth.models import Permission
    from catalog.models import Author

    class AuthorCreateViewTest(TestCase):

        def setUp(self):
            # Создание пользователей с разными правами
            self.test_user1 = User.objects.create_user(username='testuser1', password='12345')
            self.test_user1.save()

            self.test_user2 = User.objects.create_user(username='testuser2', password='12345')
            # Добавление разрешения can_mark_returned для test_user2
            permission = Permission.objects.get(codename='can_mark_returned')
            self.test_user2.user_permissions.add(permission)
            self.test_user2.save()

        def test_redirect_if_not_logged_in(self):
            """Тест: редирект на страницу входа если пользователь не авторизован"""
            resp = self.client.get(reverse('author-create'))
            self.assertRedirects(resp, '/accounts/login/?next=/catalog/author/create/')

        def test_forbidden_if_logged_in_but_not_correct_permission(self):
            """Тест: доступ запрещен если пользователь авторизован но без прав"""
            login = self.client.login(username='testuser1', password='12345')
            resp = self.client.get(reverse('author-create'))
            self.assertEqual(resp.status_code, 403)  # Forbidden

        def test_logged_in_with_permission_can_access_page(self):
            """Тест: доступ разрешен если пользователь авторизован и имеет права"""
            login = self.client.login(username='testuser2', password='12345')
            resp = self.client.get(reverse('author-create'))
            self.assertEqual(resp.status_code, 200)

        def test_uses_correct_template(self):
            """Тест: используется правильный шаблон"""
            login = self.client.login(username='testuser2', password='12345')
            resp = self.client.get(reverse('author-create'))
            self.assertEqual(resp.status_code, 200)
            self.assertTemplateUsed(resp, 'catalog/author_form.html')

        def test_initial_date_of_death(self):
            """Тест: проверка начальной даты смерти"""
            login = self.client.login(username='testuser2', password='12345')
            resp = self.client.get(reverse('author-create'))
            self.assertEqual(resp.status_code, 200)

            # Проверка начального значения date_of_death
            self.assertEqual(resp.context['form'].initial['date_of_death'], '12/10/2016')

        def test_redirects_to_author_detail_on_success(self):
            """Тест: редирект на детальную страницу автора после успешного создания"""
            login = self.client.login(username='testuser2', password='12345')

            # Данные для создания автора
            post_data = {
                'first_name': 'Test',
                'last_name': 'Author',
                'date_of_birth': '1980-01-01',
                'date_of_death': '2020-01-01',
            }

            resp = self.client.post(reverse('author-create'), post_data)

            # Проверка что автор создан
            self.assertEqual(Author.objects.count(), 1)
            author = Author.objects.first()

            # Проверка редиректа на детальную страницу автора
            self.assertRedirects(resp, reverse('author-detail', args=[author.id]))

        def test_form_fields(self):
            """Тест: проверка что форма содержит все поля модели"""
            login = self.client.login(username='test_user2', password='12345')
            resp = self.client.get(reverse('author-create'))
            self.assertEqual(resp.status_code, 200)

            # Проверка что форма содержит все поля (fields = '__all__')
            form = resp.context['form']
            expected_fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
            for field in expected_fields:
                self.assertIn(field, form.fields)

        def test_create_author_successfully(self):
            """Тест: успешное создание автора"""
            login = self.client.login(username='test_user2', password='12345')

            post_data = {
                'first_name': 'John',
                'last_name': 'Doe',
                'date_of_birth': '1975-05-15',
                'date_of_death': '2020-12-31',
            }

            resp = self.client.post(reverse('author-create'), post_data)

            # Проверка что автор создан в базе данных
            self.assertEqual(Author.objects.count(), 1)
            author = Author.objects.first()
            self.assertEqual(author.first_name, 'John')
            self.assertEqual(author.last_name, 'Doe')
            self.assertEqual(str(author.date_of_birth), '1975-05-15')
            self.assertEqual(str(author.date_of_death), '2020-12-31')