from unittest import mock

from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from user.models import ActivationCode, RecoveryToken


class RegisterTestCase(APITestCase):
    def test_create_user_with_duplicate_email_address_should_return_400(self):
        response = self.client.post("/api/accounts", {
            "username": "mahdi",
            "email": "mahdi@test.co",
            "password": "some",
            "namespace": "ns1",
        })
        self.assertEqual(response.status_code, 201)
        response = self.client.post("/api/accounts", {
            "email": "mahdi@test.co",
            "password": "some",
            "namespace": "ns1",
        })
        self.assertEqual(response.status_code, 400)

    def test_create_user_invalid_username(self):
        response = self.client.post("/api/accounts", {
            "username": "some_invalid-username",
            "email": "mahdi@test.co",
            "password": "some",
            "namespace": "ns1",
        })
        self.assertEqual(response.status_code, 400)


    def test_create_user_invalid_namespace(self):
        response = self.client.post("/api/accounts", {
            "username": "valid-username",
            "email": "mahdi@test.co",
            "password": "some",
            "namespace": "ns1_invalid",
        })
        self.assertEqual(response.status_code, 400)


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


class AccountRecovery(APITestCase):
    @mock.patch("user.views.send_recovery_token")
    def test_create_account_recovery_token(self, send_recovery_token: mock.MagicMock):
        u = User.objects.create_user(
            username="mahdi",
            password="testtset",
            email="mahdi@test.tset",
        )
        response = self.client.post("/api/users/recovery-tokens", data={"identifier": "mahdi@test.tset"})
        self.assertEqual(response.status_code, 200)
        response = self.client.post("/api/users/recovery-tokens", data={"identifier": "mahdi"})
        self.assertEqual(response.status_code, 200)
        send_recovery_token.assert_has_calls([
            mock.call(u),
            mock.call(u),
        ])


    def test_use_account_recovery_token(self):
        u = User.objects.create_user(
            username="mahdi",
            password="testtset",
            email="mahdi@test.tset",
        )
        rt = RecoveryToken.objects.create(user=u)
        r = self.client.patch("/api/users/recovery-tokens/{}".format(rt.code),
                              data={"id": 1, "new_password": "new_test"})
        self.assertEqual(r.status_code, 200)
        response = self.client.post("/api/tokens", data=dict(username="mahdi", password="new_test"))
        self.assertEqual(response.status_code, 200)
