from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from frontend.models import User, Assignments, StudentSubmissions
from django.utils import timezone
from django.urls import reverse
from django.contrib import auth
from django.contrib.messages import get_messages, test
from django.contrib.messages.storage.base import Message
from datetime import timedelta

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
    def setUp(self):
        self.client = Client()
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'
        }
        User.objects.create_user(**self.credentials)

    def test_login_view(self):
        # Test if login page is accessible
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

        # Test if user can login
        response = self.client.post(reverse('login'), self.credentials, follow=True)
        user = auth.get_user(self.client)
        # Check if user is logged in
        self.assertTrue(user.is_authenticated)
        # Check if response is redirected to the index page
        self.assertRedirects(response, reverse('index'), status_code=302)

    def test_invalid_login(self):
        # Test if login fails with invalid credentials
        self.credentials['password'] = 'wrong_password'
        response = self.client.post(reverse('login'), self.credentials, follow=True)
        user = auth.get_user(self.client)
        # Check if user is not logged in
        self.assertFalse(user.is_authenticated)
        # Check if response is still on the login page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

class SignupViewTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password1': 'd62jndic62b',
            'password2': 'd62jndic62b'
        }

    def test_signup_view(self):
        # Test if signup page is accessible
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

        # Test if user can signup
        response = self.client.post(reverse('signup'), self.credentials, follow=True)
        # Check if user is created
        self.assertTrue(User.objects.filter(username=self.credentials['username']).exists())
        # Check if response is redirected to the login page
        self.assertRedirects(response, reverse('login'), status_code=302)

class UserLogoutViewTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'
        }
        User.objects.create_user(**self.credentials)
        self.client.login(username='testuser', password='secret')

    def test_logout_view(self):
        # Test if user can logout
        response = self.client.get(reverse('logout'), follow=True)
        user = auth.get_user(self.client)
        # Check if user is logged out
        self.assertFalse(user.is_authenticated)
        # Check if response is redirected to the index page
        self.assertRedirects(response, reverse('index'), status_code=302)

class AssignmentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher_credentials = {
            'username': 'teacher',
            'password': 'secret',
            'type': User.TypeChoices.TEACHER
        }
        self.student_credentials = {
            'username': 'student',
            'password': 'secret',
            'type': User.TypeChoices.STUDENT
        }
        self.teacher = User.objects.create_user(**self.teacher_credentials)
        self.student = User.objects.create_user(**self.student_credentials)
        self.assignment = Assignments.objects.create(title="Test Assignment", dockerfile=SimpleUploadedFile("file.txt", b"file_content"))
        self.teacher.assignments.add(self.assignment)

    def test_assignment_view_teacher(self):
        self.client.login(username='teacher', password='secret')
        response = self.client.post(reverse('assignment_detail'), {'pk': self.assignment.pk}, follow=True)
        # Check if teacher can access the assignment
        self.assertEqual(response.status_code, 200)

    def test_assignment_view_student(self):
        self.client.login(username='student', password='secret')
        response = self.client.post(reverse('assignment_detail'), {'pk': self.assignment.pk}, follow=True)
        # Check if student is redirected
        self.assertRedirects(response, reverse('index'), status_code=302)

    def test_assignment_view_unauthenticated(self):
        response = self.client.post(reverse('assignment_detail'), {'pk': self.assignment.pk}, follow=True)
        # Check if unauthenticated user is redirected to login
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('assignment_detail'), status_code=302)

class EditAssignmentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher_credentials = {
            'username': 'teacher',
            'password': 'secret',
            'type': User.TypeChoices.TEACHER
        }
        self.student_credentials = {
            'username': 'student',
            'password': 'secret',
            'type': User.TypeChoices.STUDENT
        }
        self.teacher = User.objects.create_user(**self.teacher_credentials)
        self.student = User.objects.create_user(**self.student_credentials)
        self.assignment = Assignments.objects.create(title="Test Assignment", dockerfile=SimpleUploadedFile("file.txt", b"file_content"))
        self.teacher.assignments.add(self.assignment)

    def test_edit_assignment_view_teacher(self):
        self.client.login(username='teacher', password='secret')
        response = self.client.post(reverse('edit_assignment'), {'pk': self.assignment.pk, 'title': 'New Title'}, follow=True)
        # Check if teacher can edit the assignment
        self.assertEqual(response.status_code, 200)
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.title, 'Test Assignment')

    def test_edit_assignment_view_student(self):
        self.client.login(username='student', password='secret')
        response = self.client.post(reverse('edit_assignment'), {'pk': self.assignment.pk, 'title': 'New Title'}, follow=True)
        # Check if student is redirected
        self.assertRedirects(response, reverse('index'), status_code=302)

    def test_edit_assignment_view_unauthenticated(self):
        response = self.client.post(reverse('edit_assignment'), {'pk': self.assignment.pk, 'title': 'New Title'}, follow=True)
        # Check if unauthenticated user is redirected to login
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('edit_assignment'), status_code=302)

class CreateAssignmentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher_credentials = {
            'username': 'teacher',
            'password': 'secret',
            'type': User.TypeChoices.TEACHER
        }
        self.student_credentials = {
            'username': 'student',
            'password': 'secret',
            'type': User.TypeChoices.STUDENT
        }
        self.teacher = User.objects.create_user(**self.teacher_credentials)
        self.student = User.objects.create_user(**self.student_credentials)
        self.assignment_input = {
            'title':"Test Assignment",
            'status':Assignments.StatusChoices.ACTIVE,
            'dockerfile':SimpleUploadedFile("file.txt", b"file_content"),
            'maxmemory':200,
            'maxcpu':2,
            'timer':timedelta(seconds=300),
            'start':timezone.now(),
            'end':timezone.now() + timedelta(days=7),
            'students': [self.student.pk]
        }

    def test_create_assignment_view_teacher(self):
        self.client.login(username='teacher', password='secret')
        response = self.client.post(reverse('new_assignment'), self.assignment_input, follow=True)
        # Check if teacher can create the assignment
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Assignments.objects.filter(title='Test Assignment').exists())

    def test_create_assignment_view_student(self):
        self.client.login(username='student', password='secret')
        response = self.client.post(reverse('new_assignment'), {'title': 'Test Assignment', 'students': [self.student.pk]}, follow=True)
        # Check if student is redirected
        self.assertRedirects(response, reverse('index'), status_code=302)

    def test_create_assignment_view_unauthenticated(self):
        response = self.client.post(reverse('new_assignment'), {'title': 'Test Assignment', 'students': [self.student.pk]}, follow=True)
        # Check if unauthenticated user is redirected to login
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('new_assignment'), status_code=302)

class SubmissionViewTest(TestCase):
    def setUp(self):
        self.teacher_credentials = {
            'username': 'teacher',
            'password': 'secret',
            'type': User.TypeChoices.TEACHER
        }
        self.student_credentials = {
            'username': 'student',
            'password': 'secret',
            'type': User.TypeChoices.STUDENT
        }
        self.admin_credentials = {
            'username': 'admin',
            'password': 'secret',
            'type': User.TypeChoices.ADMIN
        }
        self.client = Client()
        self.teacher = User.objects.create_user(**self.teacher_credentials)
        self.student = User.objects.create_user(**self.student_credentials)
        self.admin = User.objects.create_user(**self.admin_credentials)
        self.assignment = Assignments.objects.create(
            title="Test Assignment",
            status=Assignments.StatusChoices.ACTIVE,
            dockerfile=SimpleUploadedFile("file1.txt", b"file_content"),
        )
        self.submission = StudentSubmissions.objects.create(
            student=self.student,
            result=StudentSubmissions.ResChoices.PENDING,
            File=SimpleUploadedFile("file2.txt", b"file_content"),
            assignment=self.assignment,
            uploadtime=timezone.now()
        )

    def test_submission_view_student(self):
        self.client.login(username='student', password='secret') 
        response = self.client.post(reverse('sub_details'), {'pk': self.submission.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Details')

    def test_submission_view_teacher(self):
        self.client.login(username='teacher', password='secret')
        response = self.client.post(reverse('sub_details'), {'pk': self.submission.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Details')

    def test_submission_view_unauthorized(self):
        self.client.login(username='admin', password='secret')
        response = self.client.post(reverse('sub_details'), {'pk': self.submission.pk}, follow=True)
        self.assertRedirects(response, reverse('index'), status_code=302)

class ReevalViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher_credentials = {
            'username': 'teacher',
            'password': 'secret',
            'type': User.TypeChoices.TEACHER
        }
        self.teacher = User.objects.create_user(**self.teacher_credentials)
        self.student = User.objects.create_user(username='student', password='secret', type=User.TypeChoices.STUDENT)
        self.assignment = Assignments.objects.create(title="Test Assignment", dockerfile=SimpleUploadedFile("file.txt", b"file_content"))
        self.submission = StudentSubmissions.objects.create(
            student=self.student,
            result=StudentSubmissions.ResChoices.PASSED,
            File=SimpleUploadedFile("file.txt", b"file_content"),
            assignment=self.assignment,
            uploadtime=timezone.now()
        )

    def test_reeval_view(self):
        self.client.login(username='teacher', password='secret')
        response = self.client.post(reverse('reeval'), {'mode': 'single', 'pk': self.assignment.pk, 'subpk': self.submission.pk})
        self.assertEqual(response.status_code, 302)
        self.submission.refresh_from_db()
        # Assuming that the reeval view updates the result to PASSED
        self.assertEqual(self.submission.result, StudentSubmissions.ResChoices.PENDING)