# -*- coding:UTF-8 -*-
import unittest
from app import create_app, db
from app.models import User, Role, Permission, AnonymousUser, Follow, Post


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _make_user(self, email='john@example.com', password='cat'):
        u = User(email=email, password=password)
        db.session.add(u)
        db.session.commit()
        return u

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_roles_and_permissions(self):
        u = self._make_user()
        self.assertTrue(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.is_administrator())

    def test_admin_role_assignment(self):
        self.app.config['FLASKY_ADMIN'] = 'admin@example.com'
        u = User(email='admin@example.com', password='cat')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(u.is_administrator())

    def test_confirmation_token(self):
        u = self._make_user()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))
        self.assertTrue(u.confirmed)
        db.session.commit()

    def test_confirmation_token_expires(self):
        u = self._make_user()
        token = u.generate_confirmation_token(expiration=-1)
        self.assertFalse(u.confirm(token))

    def test_confirmation_token_invalid(self):
        u = self._make_user()
        self.assertFalse(u.confirm('not-a-valid-token'))

    def test_reset_password_token(self):
        u = self._make_user()
        token = u.generate_reset_token()
        self.assertTrue(User.reset_password(token, 'new-password'))
        self.assertTrue(u.verify_password('new-password'))

    def test_email_change_token(self):
        u = self._make_user()
        token = u.generate_email_change_token('new@example.com')
        self.assertTrue(u.change_email(token))
        db.session.commit()
        self.assertEqual(u.email, 'new@example.com')

    def test_auth_token(self):
        u = self._make_user()
        token = u.generate_auth_token(expiration=3600)
        self.assertIs(User.verify_auth_token(token), u)
        expired = u.generate_auth_token(expiration=-1)
        self.assertIsNone(User.verify_auth_token(expired))

    def test_follows(self):
        u = self._make_user(email='john@example.com')
        v = self._make_user(email='susan@example.com')
        # 构造函数已包含自我关注
        self.assertTrue(u.is_following(u))
        p = Post(body='hello', author=v)
        db.session.add(p)
        db.session.commit()
        u.follow(v)
        db.session.commit()
        self.assertTrue(u.is_following(v))
        self.assertTrue(v.is_followed_by(u))
        self.assertIn(p.id, [post.id for post in u.followed_posts])
        u.unfollow(v)
        db.session.commit()
        self.assertFalse(u.is_following(v))
