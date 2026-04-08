# -*- coding: utf-8 -*-
"""
Контрактные тесты UI: hero (главная), бургер-меню/шапка, статические CSS.

Проверяют, что ключевая разметка и стили (то, что настраивалось вручную)
остались на месте — без снимков визуального регресса.
"""
from pathlib import Path

from django.conf import settings
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse


def _read_static_css(rel_path: str) -> str:
    path = Path(settings.BASE_DIR) / "static" / rel_path
    return path.read_text(encoding="utf-8")


class HomeHeroMarkupContractTest(TestCase):
    """Главная: hero-блок, двухстрочный H1, подзаголовок, подключение home.css."""

    def setUp(self):
        self.client = Client()

    def test_home_200_and_hero_structure(self):
        r = self.client.get(reverse("home"))
        self.assertEqual(r.status_code, 200)
        html = r.content.decode("utf-8")
        self.assertIn('class="hero"', html)
        self.assertIn('class="hero-content"', html)
        self.assertIn('class="hero-eyebrow"', html)
        self.assertIn('class="hero-title"', html)
        self.assertIn('class="hero-title-line"', html)
        self.assertIn('class="hero-subtitle"', html)
        self.assertIn("напрямую", html)
        self.assertIn("из США, Китая или Кореи", html)
        self.assertIn("Экономия до", html)

    def test_home_links_home_css(self):
        r = self.client.get(reverse("home"))
        self.assertEqual(r.status_code, 200)
        html = r.content.decode("utf-8")
        self.assertRegex(html, r'href=["\']/static/css/home\.css\?v=[^"\']+["\']')

    def test_home_two_title_lines_in_h1(self):
        r = self.client.get(reverse("home"))
        html = r.content.decode("utf-8")
        self.assertEqual(html.count('class="hero-title-line"'), 2)


class HeaderBurgerMarkupContractTest(TestCase):
    """Шапка и выезжающее меню (include header_burger)."""

    def setUp(self):
        self.client = Client()

    def test_home_has_header_burger_glass_drawer(self):
        r = self.client.get(reverse("home"))
        self.assertEqual(r.status_code, 200)
        html = r.content.decode("utf-8")
        self.assertIn('class="header"', html)
        self.assertIn('class="logo-img"', html)
        self.assertIn('class="burger"', html)
        self.assertIn('id="burger-overlay"', html)
        self.assertIn('class="burger-menu burger-menu--left"', html)
        self.assertIn('class="burger-menu-header"', html)
        self.assertIn('class="burger-close"', html)
        self.assertIn('class="burger-menu-list"', html)
        self.assertIn('class="burger-menu-buttons"', html)
        self.assertIn('class="burger-menu-legal"', html)
        self.assertIn('autopark-logo-v2.svg', html)

    def test_thanks_page_includes_same_header(self):
        r = self.client.get(reverse("thanks"), {"s": "order"})
        self.assertEqual(r.status_code, 200)
        html = r.content.decode("utf-8")
        self.assertIn('class="burger-menu-header"', html)


class StaticCssContractsTest(SimpleTestCase):
    """Проверка содержимого static/css (без изменения логики)."""

    def test_base_css_glass_header_and_burger_menu(self):
        css = _read_static_css("css/base.css")
        self.assertIn(".header", css)
        self.assertIn("backdrop-filter", css)
        self.assertIn(".burger-menu", css)
        self.assertIn("blur(18px)", css)
        self.assertIn(".burger-menu-header", css)

    def test_home_css_hero_premium_typography_tokens(self):
        css = _read_static_css("css/home.css")
        self.assertIn(".hero-content", css)
        self.assertIn("max-width: 920px", css)
        self.assertIn(".hero-title", css)
        self.assertIn("text-shadow:", css)
        self.assertIn("@media (min-width: 1024px)", css)
        self.assertIn("52px", css)
        self.assertIn("max-width: 780px", css)
        self.assertIn(".hero-subtitle", css)
        self.assertIn("max-width: 640px", css)
