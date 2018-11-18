import json
import unittest

from project.tests.base import BaseTestCase
from project.tests.utils import add_user


class TestUserService(BaseTestCase):
    def test_users(self):
        response = self.client.get("/users/ping")
        data = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        self.assertIn("pong!", data["message"])
        self.assertIn("success", data["status"])

    def test_add_user(self):
        with self.client:
            response = self.client.post(
                "/users",
                data=json.dumps(
                    {
                        "username": "michael",
                        "email": "michael@mherman.org",
                        "password": "greaterthaneight",
                    }
                ),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 201)
            self.assertIn("michael@mherman.org was added!", data["message"])
            self.assertIn("success", data["status"])

    def test_add_user_invalid_json(self):
        with self.client:
            response = self.client.post(
                "/users", data=json.dumps({}), content_type="application/json"
            )
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("fail", data["status"])

    def test_add_user_invalid_json_keys(self):
        with self.client:
            response = self.client.post(
                "/users",
                data=json.dumps(
                    {"email": "michael@mherman.org", "password": "greaterthaneight"}
                ),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("fail", data["status"])

    def test_add_user_invalid_json_keys_no_password(self):
        with self.client:
            response = self.client.post(
                "/users",
                data=json.dumps({"email": "michael@mherman.org", "username": "michael"}),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("fail", data["status"])

    def test_add_user_duplicate_email(self):
        with self.client:
            self.client.post(
                "/users",
                data=json.dumps(
                    {
                        "username": "michael",
                        "email": "michael@mherman.org",
                        "password": "greaterthaneight",
                    }
                ),
                content_type="application/json",
            )
            response = self.client.post(
                "/users",
                data=json.dumps(
                    {
                        "username": "michael",
                        "email": "michael@mherman.org",
                        "password": "greaterthaneight",
                    }
                ),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 400)
            self.assertIn("Sorry. That email already exists.", data["message"])
            self.assertIn("fail", data["status"])

    def test_single_user(self):
        user = add_user("michael", "michael@mherman.org", "greaterthaneight")

        with self.client:
            response = self.client.get(f"/users/{user.id}")
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 200)
            self.assertIn("michael", data["data"]["username"])
            self.assertIn("michael@mherman.org", data["data"]["email"])
            self.assertIn("success", data["status"])

    def test_single_user_no_id(self):
        with self.client:
            response = self.client.get("/users/blah")
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 404)
            self.assertIn("User does not exist", data["message"])
            self.assertIn("fail", data["status"])

    def test_single_user_incorrect_id(self):
        with self.client:
            response = self.client.get("/users/999")
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 404)
            self.assertIn("User does not exist", data["message"])
            self.assertIn("fail", data["status"])

    def test_all_users(self):
        add_user("michael", "michael@herman.org", "greaterthaneight")
        add_user("fletcher", "fletcher@notreal.com", "greaterthaneight")

        with self.client:
            response = self.client.get("/users")
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data["data"]["users"]), 2)
            self.assertIn("michael", data["data"]["users"][0]["username"])
            self.assertIn("michael@herman.org", data["data"]["users"][0]["email"])
            self.assertIn("fletcher", data["data"]["users"][1]["username"])
            self.assertIn("fletcher@notreal.com", data["data"]["users"][1]["email"])
            self.assertIn("success", data["status"])

    def test_main_no_users(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"All Users", response.data)
        self.assertIn(b"<p>No users!</p>", response.data)

    def test_main_with_users(self):
        add_user("michael", "michael@herman.org", "greaterthaneight")
        add_user("fletcher", "fletcher@notreal.com", "greaterthaneight")
        with self.client:
            response = self.client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"All Users", response.data)
            self.assertNotIn(b"<p>No users!</p>", response.data)
            self.assertIn(b"michael", response.data)
            self.assertIn(b"fletcher", response.data)

    def test_main_add_user(self):
        with self.client:
            response = self.client.post(
                "/",
                data=dict(
                    username="michael",
                    email="michael@sonotreal.com",
                    password="greaterthaneight",
                ),
                follow_redirects=True,
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"All Users", response.data)
            self.assertNotIn(b"<p>No users!</p>", response.data)
            self.assertIn(b"michael", response.data)


if __name__ == "__main__":
    unittest.main()
