from django.test import TestCase, Client
from frontend.views import viewstudent
from django.core.files.uploadedfile import SimpleUploadedFile
from frontend.models import User, Assignments, StudentSubmissions
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse

class AdminViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_student = User.objects.create(username='user_student', type=User.TypeChoices.STUDENT)
        self.user_teacher = User.objects.create(username='user_teacher', type=User.TypeChoices.TEACHER)
        self.user_admin = User.objects.create(username='user_admin', type=User.TypeChoices.ADMIN)
        self.user_student.set_password('12345')
        self.user_teacher.set_password('12345')
        self.user_admin.set_password('12345')
        self.user_student.save()
        self.user_teacher.save()
        self.user_admin.save()


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

class StudentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_student = User.objects.create(username='user_student', type=User.TypeChoices.STUDENT)
        self.user_student.set_password('12345')   
        self.user_student.save() 
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