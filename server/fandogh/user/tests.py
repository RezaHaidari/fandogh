from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from user.models import ActivationCode


class AccountActivation(APITestCase):
    def test_activate_an_account(self):
        u = User.objects.create_user(
            username="mahdi",
            password="testtset",
            email="mahdi@test.tset",
        )
        c = ActivationCode.objects.create(user=u)
        res = self.client.patch("/api/users/activation-codes/{}".format(c.code), data=dict(id=1))
        self.assertEqual(res.status_code, 200)

    def test_activate_an_account_with_invalid_req_body(self):
        u = User.objects.create_user(
            username="mahdi",
            password="testtset",
            email="mahdi@test.tset",
        )
        c = ActivationCode.objects.create(user=u)
        res = self.client.patch("/api/users/activation-codes/{}".format(c.code), data=dict(typo_field=1))
        self.assertEqual(res.status_code, 400)

    def test_activate_an_account_with_invalid_code(self):
        u = User.objects.create_user(
            username="mahdi",
            password="testtset",
            email="mahdi@test.tset",
        )
        c = ActivationCode.objects.create(user=u)
        res = self.client.patch("/api/users/activation-codes/1111{}".format(c.code), data=dict(id=1))
        self.assertEqual(res.status_code, 404)
