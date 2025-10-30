import datetime

from django.test import TestCase

# Create your tests here.

from catalog.models import Author

class AuthorModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Set up non-modified objects used by all test methods
        Author.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author=Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label,'first name')

    def test_date_of_death_label(self):
        author=Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEquals(field_label,'died')

    def test_first_name_max_length(self):
        author=Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEquals(max_length,100)

    def test_object_name_is_last_name_comma_first_name(self):
        author=Author.objects.get(id=1)
        expected_object_name = '%s, %s' % (author.last_name, author.first_name)
        self.assertEquals(expected_object_name,str(author))

    def test_get_absolute_url(self):
        author=Author.objects.get(id=1)
        #This will also fail if the urlconf is not defined.
        self.assertEquals(author.get_absolute_url(),'/catalog/author/1')

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = '%s, %s' % (author.last_name, author.first_name)
        self.assertEquals(expected_object_name, str(author))

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEquals(author.get_absolute_url(), '/catalog/author/1')

class AuthorModelTest(TestCase):

    def setUp(self):
        self.author = Author.objects.create(
            first_name='John',
            last_name='Doe',
            date_of_birth=datetime.date(1980, 1, 1),
            date_of_death=datetime.date(2020, 1, 1)
        )

    def test_author_creation(self):
        """Тест создания автора"""
        self.assertEqual(self.author.first_name, 'John')
        self.assertEqual(self.author.last_name, 'Doe')
        self.assertTrue(isinstance(self.author.date_of_birth, datetime.date))

    def test_author_str_representation(self):
        """Тест строкового представления автора"""
        self.assertEqual(str(self.author), 'Doe, John')

    def test_author_get_absolute_url(self):
        """Тест метода get_absolute_url"""
        url = self.author.get_absolute_url()
        self.assertEqual(url, f'/catalog/author/{self.author.id}/')