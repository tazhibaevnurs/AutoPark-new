# -*- coding: utf-8 -*-
"""Базовые тесты приложения pages."""
from django.test import TestCase, Client
from django.urls import reverse


class HomePageTest(TestCase):
    """Проверка главной страницы."""

    def setUp(self):
        self.client = Client()

    def test_home_returns_200(self):
        """Главная страница открывается и возвращает 200."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
