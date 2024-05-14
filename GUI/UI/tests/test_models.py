from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from frontend.models import Assignments, StudentSubmissions, User
from datetime import datetime, timedelta

class AssignmentModelTest(TestCase):
    def setUp(self):
        self.assignment = Assignments.objects.create(
            title="Test Assignment",
            status=Assignments.StatusChoices.ACTIVE,
            dockerfile=SimpleUploadedFile("file.txt", b"file_content"),
        )

    def test_assignment_creation(self):
        self.assertEqual(self.assignment.title, "Test Assignment")
        self.assertEqual(self.assignment.status, Assignments.StatusChoices.ACTIVE)
        self.assertEqual(self.assignment.maxmemory, 100)
        self.assertEqual(self.assignment.maxcpu, 1)
        self.assertEqual(self.assignment.timer, timedelta(seconds=120))
        self.assertEqual(self.assignment.maxsubs, 5)
        self.assertTrue(self.assignment.dockerfile)

class StudentSubmissionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.user.set_password('12345')
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

    def test_submission_creation(self):
        self.assertEqual(self.submission.student, self.user)
        self.assertEqual(self.submission.result, StudentSubmissions.ResChoices.PENDING)
        self.assertTrue(self.submission.File)
        self.assertEqual(self.submission.assignment, self.assignment)