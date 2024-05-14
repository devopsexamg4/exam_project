from django.test import TestCase, Client
from frontend.views import viewstudent
from django.core.files.uploadedfile import SimpleUploadedFile
from frontend.models import User, Assignments, StudentSubmissions
from datetime import datetime, timedelta

class ViewStudentTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='testuser')
        self.user.set_password('12345')
        self.user.save()
        self.assignment = Assignments.objects.create(
            title="Test Assignment",
            status=Assignments.StatusChoices.ACTIVE,
            dockerfile=SimpleUploadedFile("file.txt", b"file_content"),
        )
        self.submission = StudentSubmissions.objects.create(
            student=self.user,
            result=StudentSubmissions.ResChoices.PENDING,
            File=SimpleUploadedFile("file.txt", b"file_content"),
            assignment=self.assignment,
            uploadtime=datetime.now()
        )

    def test_viewstudent(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post('/studentdetails/', {'student-pk': self.user.pk, 'assignment-pk': self.assignment.pk})
        self.assertEqual(response.status_code, 200)