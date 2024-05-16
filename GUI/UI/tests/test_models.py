from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from django.core.exceptions import ValidationError
from frontend.models import Assignments, StudentSubmissions, User, dockerdir, subdir
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

class DockerdirTest(TestCase):
    """Test the dockerdir function in models.py"""
    def test_dockerdir(self):
        instance = Mock()
        instance.dockerfile = SimpleUploadedFile("file.txt", b"file_content")
        result = dockerdir(instance, None)
        uuid_part = result.split('/')[1][0:5]
        self.assertEqual(len(uuid_part), 5)
        # Check that the UUID part only contains hexadecimal characters
        self.assertTrue(all(c in '0123456789abcdef' for c in uuid_part))
        self.assertTrue(result.startswith("assignments/"))
        self.assertTrue("file.txt" in result)

class SubdirTest(TestCase):
    """Test the subdir function in models.py"""
    def test_subdir(self):
        instance = Mock()
        instance.File = SimpleUploadedFile("file.txt", b"file_content")
        result = subdir(instance, None)
        uuid_part = result.split('/')[1][0:5]
        self.assertEqual(len(uuid_part), 5)
        # Check that the UUID part only contains hexadecimal characters
        self.assertTrue(all(c in '0123456789abcdef' for c in uuid_part))
        self.assertTrue(result.startswith("submissions/"))
        self.assertTrue("file.txt" in result)

class AssignmentModelTest(TestCase):
    """Test the Assignments model in models.py"""
    def setUp(self):
        self.assignment = Assignments.objects.create(
            title="Test Assignment",
            status=Assignments.StatusChoices.ACTIVE,
            dockerfile=SimpleUploadedFile("file.txt", b"file_content"),
            maxmemory=200,
            maxcpu=2,
            timer=timedelta(seconds=300),
            start=datetime.now(tz=timezone.utc),
            end=datetime.now(tz=timezone.utc) + timedelta(days=7),
            maxsubs=10,
        )

    def test_assignment_creation(self):
        self.assertEqual(self.assignment.title, "Test Assignment")
        self.assertEqual(self.assignment.status, Assignments.StatusChoices.ACTIVE)
        self.assertEqual(self.assignment.maxmemory, 200)
        self.assertEqual(self.assignment.maxcpu, 2)
        self.assertEqual(self.assignment.timer, timedelta(seconds=300))
        self.assertEqual(self.assignment.maxsubs, 10)
        self.assertTrue(self.assignment.dockerfile)

    def test_valid_interval(self):
        self.assignment.start = datetime.now(tz=timezone.utc) + timedelta(days=7)
        self.assignment.end = datetime.now(tz=timezone.utc)
        with self.assertRaises(ValidationError):
            self.assignment.save()

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
            uploadtime=datetime.now(tz=timezone.utc)
        )

    def test_submission_creation(self):
        self.assertEqual(self.submission.student, self.user)
        self.assertEqual(self.submission.result, StudentSubmissions.ResChoices.PENDING)
        self.assertTrue(self.submission.File)
        self.assertEqual(self.submission.assignment, self.assignment)