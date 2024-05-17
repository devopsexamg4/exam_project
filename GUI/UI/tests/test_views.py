from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from frontend.models import User, Assignments, StudentSubmissions
from django.utils import timezone
from django.urls import reverse
from django.contrib.messages import get_messages, test
from django.contrib.messages.storage.base import Message


class HomeViewTest(TestCase):
    def test_home_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

class AdminViewTest(test.MessagesTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.user_student = User.objects.create_user(username='user_student', password='12345', type=User.TypeChoices.STUDENT)
        self.user_teacher = User.objects.create_user(username='user_teacher', password='12345', type=User.TypeChoices.TEACHER)
        self.user_admin = User.objects.create_user(username='user_admin', password='12345', type=User.TypeChoices.ADMIN)


    def test_admin_access(self):
        self.client.login(username='user_admin', password='12345')
        response = self.client.get(reverse('admin'))
        self.assertEqual(response.status_code, 200)

    def test_non_admin_access(self):
        self.client.login(username='user_student', password='12345')
        response = self.client.get(reverse('admin'))
        self.assertEqual(response.status_code, 302)

    def test_post_request(self):
        self.client.login(username='user_admin', password='12345')
        response = self.client.post(reverse('admin'), {'pk': self.user_student.pk, 'type': User.TypeChoices.TEACHER})
        self.user_student.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user_student.type, User.TypeChoices.TEACHER)

        response2 = self.client.post(reverse('admin'), {'pk': self.user_student.pk, 'type': "invalid"})
        self.assertMessages(response2, [Message(level=40, message={'type': ['Select a valid choice. invalid is not one of the available choices.']})])

class StudentViewTest(test.MessagesTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.assignment = Assignments.objects.create(
            title="Test Assignment",
            dockerfile=SimpleUploadedFile("file.txt", b"file_content"),
            status=Assignments.StatusChoices.ACTIVE
        )
        self.user_student = User.objects.create_user(username='user_student', password='12345', type=User.TypeChoices.STUDENT)
        self.user_teacher = User.objects.create_user(username='user_teacher', password='12345', type=User.TypeChoices.TEACHER)
        self.user_student.assignments.add(self.assignment)
        self.user_student.save()


    def test_student_access(self):
        self.client.login(username='user_student', password='12345')
        response = self.client.get(reverse('student'))
        self.assertEqual(response.status_code, 200)

    def test_non_student_access(self):
        self.client.login(username='user_teacher', password='12345')
        response = self.client.get(reverse('student'))
        self.assertEqual(response.status_code, 302)

    def test_valid_form_submission(self):
        self.client.login(username='user_student', password='12345')
        response = self.client.post(reverse('student'), {'student-pk' : self.user_student.pk, 
                                                         'assignment' : self.assignment.pk, 
                                                         'File' : SimpleUploadedFile("file.txt", b"file_content")})
        self.assertEqual(response.status_code, 200)
        self.assertMessages(response, [Message(level=20, message='submission received')])


class ViewStudentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_student = User.objects.create_user(username='user_student', password='12345', type=User.TypeChoices.STUDENT)
        self.assignment = Assignments.objects.create(
            title="Test Assignment",
            status=Assignments.StatusChoices.ACTIVE,
            dockerfile=SimpleUploadedFile("file.txt", b"file_content"),
        )
        self.submission = StudentSubmissions.objects.create(
            student=self.user_student,
            result=StudentSubmissions.ResChoices.PENDING,
            File=SimpleUploadedFile("file.txt", b"file_content"),
            assignment=self.assignment,
            uploadtime=timezone.now()
        )
    def test_viewstudent(self):
        response = self.client.post('/studentdetails/', {'student-pk': self.user_student.pk, 'assignment-pk': self.assignment.pk})
        self.assertEqual(response.status_code, 302)
        self.client.login(username='user_student', password='12345')
        response = self.client.post('/studentdetails/', {'student-pk': self.user_student.pk, 'assignment-pk': self.assignment.pk})
        self.assertEqual(response.status_code, 200)

class TeacherViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher_user = User.objects.create_user(username='teacher', password='12345', type=User.TypeChoices.TEACHER)
        self.student_user = User.objects.create_user(username='student', password='12345', type=User.TypeChoices.STUDENT)
        self.assignment = Assignments.objects.create(
            title="Test Assignment",
            status=Assignments.StatusChoices.ACTIVE,
            dockerfile=SimpleUploadedFile("file.txt", b"file_content"),
        )
        self.teacher_user.assignments.add(self.assignment)

    def test_teacher_view_with_teacher_user(self):
        self.client.login(username='teacher', password='12345')
        response = self.client.get(reverse('teacher'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Assignment')

    def test_teacher_view_with_student_user(self):
        self.client.login(username='student', password='12345')
        response = self.client.get(reverse('teacher'))
        self.assertEqual(response.status_code, 302)  # Expecting a redirect



class UserLoginViewTest(TestCase):
    def test_user_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

class SignupViewTest(TestCase):
    def test_signup_view(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

class UserLogoutViewTest(TestCase):
    def test_user_logout_view(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)