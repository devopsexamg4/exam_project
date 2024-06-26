from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from django.core.exceptions import ValidationError
from frontend.models import Assignments, StudentSubmissions, User, dockerdir, subdir
from datetime import timedelta
from django.utils import timezone
from unittest.mock import Mock
from os.path import exists

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
        instance.file = SimpleUploadedFile("file.txt", b"file_content")
        result = subdir(instance, None)
        uuid_part = result.split('/')[1][4:9]
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
            start=timezone.now(),
            endtime=timezone.now() + timedelta(days=7),
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

    def test_str(self):
        self.assertEqual(str(self.assignment), "Test Assignment")

    def test_valid_interval(self):
        self.assignment.start = timezone.now() + timedelta(days=7)
        self.assignment.endtime = timezone.now()
        with self.assertRaises(ValidationError):
            self.assignment.save()

    def test_delete(self):
        file_path = self.assignment.dockerfile.path
        self.assignment.delete()
        self.assertFalse(exists(file_path), "File was not deleted")

class UserTest(TestCase):
    def setUp(self):
        self.assignment = Assignments.objects.create(
            title="Test Assignment",
            status=Assignments.StatusChoices.ACTIVE,
            dockerfile=SimpleUploadedFile("file.txt", b"file_content"),
        )
        self.user = User.objects.create_user(username='testuser', password='12345', user_type=User.TypeChoices.STUDENT)

    def test_create_user(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.user_type, User.TypeChoices.STUDENT)

    def test_str(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_assignments(self):
        self.user.assignments.add(self.assignment)
        self.assertIn(self.assignment, self.user.assignments.all())
    
    def test_type_choices(self):
        for choice in User.TypeChoices:
            self.user.user_type = choice
            self.user.save()
            self.assertEqual(User.objects.get(id=self.user.id).user_type, choice)

class StudentSubmissionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345', user_type=User.TypeChoices.STUDENT)
        self.assignment = Assignments.objects.create(
            title="Test Assignment",
            status=Assignments.StatusChoices.ACTIVE,
            dockerfile=SimpleUploadedFile("file.txt", b"file_content"),
        )
        self.submission = StudentSubmissions.objects.create(
            student=self.user,
            status=StudentSubmissions.ResChoices.PENDING,
            file=SimpleUploadedFile("file.txt", b"file_content"),
            assignment=self.assignment,
            uploadtime=timezone.now()
        )

    def test_submission_creation(self):
        self.assertEqual(self.submission.student, self.user)
        self.assertEqual(self.submission.status, StudentSubmissions.ResChoices.PENDING)
        self.assertTrue(self.submission.file)
        self.assertEqual(self.submission.assignment, self.assignment)

    def test_str(self):
        self.assertEqual(str(self.submission), f"{self.user} - {self.submission.uploadtime.strftime('%d/%m/%y, %H:%M')}")

    def test_valid_time(self):
        self.assignment.start = timezone.now() + timedelta(days=7)
        self.assignment.endtime = timezone.now() + timedelta(days=14)
        self.assignment.save()
        with self.assertRaises(ValidationError):
            self.submission.save()

    def test_valid_pending(self):
        self.assignment.maxsubs = 1
        self.assignment.save()
        with self.assertRaises(ValidationError):
            StudentSubmissions.objects.create(
                student=self.user,
                assignment=self.assignment,
                file=SimpleUploadedFile('test_file', b'file_content'),
            )

    def test_delete(self):
        file_path = self.submission.file.path
        self.submission.delete()
        self.assertFalse(exists(file_path), "File was not deleted")

    def test_result_choices(self):
        for choice in StudentSubmissions.ResChoices:
            self.submission.status = choice
            self.submission.save()
            self.assertEqual(StudentSubmissions.objects.get(id=self.submission.id).status, choice)
