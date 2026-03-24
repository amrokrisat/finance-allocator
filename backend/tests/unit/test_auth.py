import unittest

from app.core.auth import hash_password, verify_password


class AuthTests(unittest.TestCase):
    def test_hash_and_verify_password(self) -> None:
        password_hash = hash_password("correct horse battery staple")
        self.assertTrue(verify_password("correct horse battery staple", password_hash))
        self.assertFalse(verify_password("wrong password", password_hash))


if __name__ == "__main__":
    unittest.main()
