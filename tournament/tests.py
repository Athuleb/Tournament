from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import College, Registration
from django.urls import reverse
import json

class RegistrationLimitTest(TestCase):
    def setUp(self):
        self.college = College.objects.create(name="Test College")
        self.client = Client()
        self.url = reverse('tournament:index')
        
    def test_registration_limit_enforced(self):
        """Test that only 18 students can register for a college."""
        
        # 1. Create 18 registrations
        for i in range(18):
            photo = SimpleUploadedFile("test_photo_%d.jpg" % i, b"file_content", content_type="image/jpeg")
            Registration.objects.create(
                college=self.college,
                name="Student %d" % i,
                prn="PRN_%d" % i,
                department="CS",
                photo=photo
            )
            
        self.assertEqual(self.college.registrations.count(), 18)
        
        # 2. Try to register the 19th student via POST request (simulating user registration)
        photo_19 = SimpleUploadedFile("test_photo_19.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(self.url, {
            'college': self.college.id,
            'name': 'Student 19',
            'prn': 'PRN_19',
            'department': 'CS',
            'photo': photo_19
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # 3. Verify the response
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertIn('limit for Test College has already been reached', data['message'])
        
        # 4. Double check database count remains 18
        self.assertEqual(self.college.registrations.count(), 18)

    def test_prn_uniqueness(self):
        """Test that duplicate PRNs are not allowed."""
        photo = SimpleUploadedFile("photo1.jpg", b"content", content_type="image/jpeg")
        Registration.objects.create(
            college=self.college,
            name="Student 1",
            prn="UNIQUE_PRN",
            department="CS",
            photo=photo
        )
        
        # Try to register another student with same PRN
        photo2 = SimpleUploadedFile("photo2.jpg", b"content", content_type="image/jpeg")
        response = self.client.post(self.url, {
            'college': self.college.id,
            'name': 'Student 2',
            'prn': 'UNIQUE_PRN',
            'department': 'EC',
            'photo': photo2
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertIn('Warning: A student with PRN "UNIQUE_PRN" is already registered', data['message'])
