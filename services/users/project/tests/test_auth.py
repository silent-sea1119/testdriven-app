import json

from flask import current_app

from project import db
from project.api.models import User
from project.tests.base import BaseTestCase
from project.tests.utils import add_user


class TestAuthBlueprint(BaseTestCase):
    def register_user(self, username, email, password):
        response = self.client.post(
            "/auth/register",
            data=json.dumps({"username": username, "email": email, "password": password}),
            content_type="application/json",
        )
        return response

    def login_user(self, email, password):
        response = self.client.post(
            "/auth/login",
            data=json.dumps({"email": email, "password": password}),
            content_type="application/json",
        )
        return response

    def logout_user(self, token):
        return self.client.get("/auth/logout", headers={"Authorization": f"Bearer {token}"})

    def user_status(self, token):
        return self.client.get("/auth/status", headers={"Authorization": f"Bearer {token}"})

    def test_user_registration(self):
        response = self.register_user("justatest", "test@test.com", "123456")
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "success")
        self.assertTrue(data["message"] == "Successfully registered.")
        self.assertTrue(data["auth_token"])
        self.assertTrue(response.content_type == "application/json")
        self.assertEqual(response.status_code, 201)

    def test_user_registration_duplicate_email(self):
        add_user("test", "test@test.com", "test")
        with self.client:
            response = self.register_user("michael", "test@test.com", "test")
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Sorry. That user already exists", data["message"])
            self.assertIn("fail", data["status"])

    def test_user_registration_duplicate_username(self):
        add_user("test", "test@test.com", "test")
        with self.client:
            response = self.register_user("test", "test@test2.com", "test")
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Sorry. That user already exists", data["message"])
            self.assertIn("fail", data["status"])

    def test_user_registration_invalid_json(self):
        with self.client:
            response = self.client.post(
                "/auth/register", data=json.dumps({}), content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("fail", data["status"])

    def test_user_registration_invalid_json_keys_no_username(self):
        with self.client:
            response = self.client.post(
                "/auth/register",
                data=json.dumps({"email": "test@test.com", "password": "test"}),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("fail", data["status"])

    def test_user_registration_invalid_json_keys_no_email(self):
        with self.client:
            response = self.client.post(
                "/auth/register",
                data=json.dumps({"username": "justatest", "email": "test@test.com"}),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("fail", data["status"])

    def test_user_registration_invalid_json_keys_no_password(self):
        with self.client:
            response = self.client.post(
                "/auth/register",
                data=json.dumps({"username": "justatest", "email": "test@test.com"}),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("fail", data["status"])

    def test_registered_user_login(self):
        with self.client:
            add_user("test", "test@test.com", "test")
            response = self.login_user("test@test.com", "test")
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["message"] == "Successfully logged in.")
            self.assertTrue(data["auth_token"])
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 200)

    def test_not_registered_user_login(self):
        with self.client:
            response = self.login_user("test@test.com", "test")
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "fail")
            self.assertTrue(data["message"] == "User does not exist.")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 404)

    def test_valid_logout(self):
        add_user("test", "test@test.com", "test")
        with self.client:
            resp_login = self.login_user("test@test.com", "test")
            token = json.loads(resp_login.data.decode())["auth_token"]
            response = self.logout_user(token)
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["message"] == "Successfully logged out.")
            self.assertEqual(response.status_code, 200)

    def test_invalid_logout_expired_token(self):
        add_user("test", "test@test.com", "test")
        current_app.config["TOKEN_EXPIRATION_SECONDS"] = -1
        with self.client:
            resp_login = self.login_user("test@test.com", "test")

            token = json.loads(resp_login.data.decode())["auth_token"]
            response = self.logout_user(token)
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "fail")
            self.assertTrue(data["message"] == "Signature expired. Please log in again.")
            self.assertEqual(response.status_code, 401)

    def test_invalid_logout(self):
        with self.client:
            response = self.logout_user("Invalid")
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "fail")
            self.assertTrue(data["message"] == "Invalid token. Please log in again.")
            self.assertEqual(response.status_code, 401)

    def test_user_status(self):
        add_user("test", "test@test.com", "test")
        with self.client:
            resp_login = self.login_user("test@test.com", "test")
            token = json.loads(resp_login.data.decode())["auth_token"]

            reponse = self.user_status(token)
            data = json.loads(reponse.data.decode())
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["data"] is not None)
            self.assertTrue(data["data"]["username"] == "test")
            self.assertTrue(data["data"]["email"] == "test@test.com")
            self.assertTrue(data["data"]["active"] is True)
            self.assertEqual(reponse.status_code, 200)

    def test_invalid_status(self):
        with self.client:
            response = self.user_status("Invalid")
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "fail")
            self.assertTrue(data["message"] == "Invalid token. Please log in again.")
            self.assertEqual(response.status_code, 401)
