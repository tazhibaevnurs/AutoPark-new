# -*- coding: utf-8 -*-
"""Базовые тесты приложения pages."""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import reverse
from django.core.cache import cache
from unittest.mock import patch
import json

from core.models import BlogPost, Case, CatalogCar
from pages.views import check_ai_generation_quota


class HomePageTest(TestCase):
    """Проверка главной страницы."""

    def setUp(self):
        self.client = Client()

    def test_home_returns_200(self):
        """Главная страница открывается и возвращает 200."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)


class AuthSecurityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="security-user",
            email="security@example.com",
            password="S3curePass!123",
            is_active=True,
        )

    def test_profile_requires_auth(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_login_rate_limit_after_five_attempts(self):
        for _ in range(5):
            response = self.client.post(
                reverse("login"),
                {"username": self.user.username, "password": "wrong-password"},
            )
            self.assertEqual(response.status_code, 200)

        blocked = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": "wrong-password"},
        )
        self.assertEqual(blocked.status_code, 429)

    def test_logout_requires_post(self):
        self.client.login(username=self.user.username, password="S3curePass!123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)


class ContentAccessControlTest(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("pages.views._serve_video_with_range", return_value=HttpResponse("ok"))
    def test_catalog_video_hidden_for_inactive_cars(self, mocked_serve):
        active = CatalogCar.objects.create(
            title="Active car",
            is_active=True,
            video="catalog/test-active.mp4",
        )
        inactive = CatalogCar.objects.create(
            title="Inactive car",
            is_active=False,
            video="catalog/test-inactive.mp4",
        )

        ok_response = self.client.get(reverse("serve_catalog_video", kwargs={"public_id": active.public_id}))
        self.assertEqual(ok_response.status_code, 200)
        self.assertEqual(mocked_serve.call_count, 1)

        forbidden_response = self.client.get(reverse("serve_catalog_video", kwargs={"public_id": inactive.public_id}))
        self.assertEqual(forbidden_response.status_code, 404)
        self.assertEqual(mocked_serve.call_count, 1)

    @patch("pages.views._serve_video_with_range", return_value=HttpResponse("ok"))
    def test_case_video_hidden_for_inactive_cases(self, mocked_serve):
        active = Case.objects.create(
            title="Active case",
            media_type="video",
            is_active=True,
            video="cases/test-active.mp4",
        )
        inactive = Case.objects.create(
            title="Inactive case",
            media_type="video",
            is_active=False,
            video="cases/test-inactive.mp4",
        )

        ok_response = self.client.get(reverse("serve_case_video", kwargs={"public_id": active.public_id}))
        self.assertEqual(ok_response.status_code, 200)
        self.assertEqual(mocked_serve.call_count, 1)

        forbidden_response = self.client.get(reverse("serve_case_video", kwargs={"public_id": inactive.public_id}))
        self.assertEqual(forbidden_response.status_code, 404)
        self.assertEqual(mocked_serve.call_count, 1)

    @patch("pages.views._serve_video_with_range", return_value=HttpResponse("ok"))
    def test_blog_video_hidden_for_unpublished_posts(self, mocked_serve):
        published = BlogPost.objects.create(
            title="Published post",
            slug="published-post",
            content="test content",
            is_published=True,
            video="blog/test-published.mp4",
        )
        unpublished = BlogPost.objects.create(
            title="Draft post",
            slug="draft-post",
            content="draft content",
            is_published=False,
            video="blog/test-draft.mp4",
        )

        ok_response = self.client.get(reverse("serve_blog_video", kwargs={"public_id": published.public_id}))
        self.assertEqual(ok_response.status_code, 200)
        self.assertEqual(mocked_serve.call_count, 1)

        forbidden_response = self.client.get(reverse("serve_blog_video", kwargs={"public_id": unpublished.public_id}))
        self.assertEqual(forbidden_response.status_code, 404)
        self.assertEqual(mocked_serve.call_count, 1)


class ApiValidationTest(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_cookie_consent_rejects_extra_fields(self):
        response = self.client.post(
            reverse("api_cookie_consent"),
            data=json.dumps({"action": "accept", "unexpected": "x"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Разрешено только поле", response.json()["error"])

    def test_cookie_consent_rejects_invalid_action(self):
        response = self.client.post(
            reverse("api_cookie_consent"),
            data=json.dumps({"action": "maybe"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_cookie_consent_requires_json_content_type(self):
        response = self.client.post(
            reverse("api_cookie_consent"),
            data='{"action":"accept"}',
            content_type="text/plain",
        )
        self.assertEqual(response.status_code, 415)

    def test_api_rate_limit_works(self):
        for _ in range(100):
            response = self.client.post(
                reverse("api_cookie_consent"),
                data=json.dumps({"action": "accept"}),
                content_type="application/json",
            )
            self.assertNotEqual(response.status_code, 429)

        blocked = self.client.post(
            reverse("api_cookie_consent"),
            data=json.dumps({"action": "accept"}),
            content_type="application/json",
        )
        self.assertEqual(blocked.status_code, 429)


class AbuseQuotaTest(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="quota-user",
            email="quota@example.com",
            password="S3curePass!123",
            is_active=True,
        )

    def test_ai_free_plan_daily_limit(self):
        for idx in range(5):
            allowed = check_ai_generation_quota(self.user, "free")
            self.assertTrue(allowed.allowed, msg=f"Attempt {idx+1} should be allowed")

        blocked = check_ai_generation_quota(self.user, "free")
        self.assertFalse(blocked.allowed)
