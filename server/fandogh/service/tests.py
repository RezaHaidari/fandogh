from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase

from service.serializers import ManagedServiceSerializer


class ManagedService(TestCase):
    def test_managed_service_serializer_with_invalid_config_item(self):
        sut = ManagedServiceSerializer(data={
            "name": "mysql",
            "version": "9.4",
            "config": {
                "invalid_key": "true"
            }
        })
        result = sut.is_valid()
        self.assertEqual(result, False)


    def test_managed_service_serializer_with_valid_config_item(self):
        sut = ManagedServiceSerializer(data={
            "name": "mysql",
            "version": "9.4",
            "config": {
                "mysql_root_password": "some-password"
            }
        })
        result = sut.is_valid()
        self.assertEqual(result, True)


