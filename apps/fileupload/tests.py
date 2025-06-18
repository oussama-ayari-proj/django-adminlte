from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import UploadedFile

class FileUploadTests(TestCase):
    def test_file_upload(self):
        client = Client()
        file = SimpleUploadedFile('test.txt', b'file_content')
        response = client.post(reverse('fileupload:upload'), {'file': file})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UploadedFile.objects.filter(file='uploads/test.txt').exists())
