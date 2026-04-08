# -*- coding: utf-8 -*-
"""
Автотесты по чек-листу технического аудита (autopark-audit.html).

Покрывают: формы /zakaz/ и /contacts/, юр. ссылки, meta description, Schema.org,
счётчики (fallback в HTML), навигация, WhiteNoise, локальные шрифты.
"""
import json
import re

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from leads.models import Lead


def _extract_ld_json_blocks(html):
    """Все объекты из script type=application/ld+json."""
    out = []
    for m in re.finditer(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.DOTALL | re.IGNORECASE,
    ):
        raw = m.group(1).strip()
        if not raw:
            continue
        try:
            out.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return out


class AuditComplianceTest(TestCase):
    """Тесты соответствия рекомендациям аудита AUTOPARK."""

    def setUp(self):
        # POST форм: CSRF в юнит-тестах не цель проверки
        self.client = Client(enforce_csrf_checks=False)

    # --- Срочно: /zakaz/ телефон, маска, required, валидация ---

    def test_zakaz_form_phone_field_attributes(self):
        r = self.client.get(reverse("order_quiz"))
        self.assertEqual(r.status_code, 200)
        content = r.content.decode("utf-8")
        self.assertIn('id="id_phone"', content)
        self.assertIn('type="tel"', content)
        self.assertIn('inputmode="tel"', content)
        self.assertIn("required", content)
        self.assertIn("data-phone-mask", content)
        self.assertIn('id="id_name"', content)

    def test_zakaz_post_rejects_empty_phone(self):
        self.client.get(reverse("order_quiz"))
        data = {
            "country": "korea",
            "budget": "3 000 000",
            "body_type": "",
            "urgency": "normal",
            "name": "Тест",
            "phone": "",
            "contact": "",
            "comment": "",
            "vehicle_type": "car",
            "hp_company": "",
        }
        r = self.client.post(reverse("order_quiz"), data)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "errorlist", status_code=200)
        self.assertContains(r, 'id="id_phone_error"', status_code=200)
        self.assertEqual(Lead.objects.count(), 0)

    def test_zakaz_post_rejects_invalid_phone(self):
        self.client.get(reverse("order_quiz"))
        data = {
            "country": "korea",
            "budget": "3 000 000",
            "body_type": "",
            "urgency": "normal",
            "name": "Тест",
            "phone": "123",
            "contact": "",
            "comment": "",
            "vehicle_type": "car",
            "hp_company": "",
        }
        r = self.client.post(reverse("order_quiz"), data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Lead.objects.count(), 0)

    def test_zakaz_post_accepts_valid_lead(self):
        self.client.get(reverse("order_quiz"))
        data = {
            "country": "korea",
            "budget": "3 000 000",
            "body_type": "",
            "urgency": "normal",
            "name": "Тест Клиент",
            "phone": "+7 (999) 123-45-67",
            "contact": "",
            "comment": "",
            "vehicle_type": "car",
            "hp_company": "",
        }
        r = self.client.post(reverse("order_quiz"), data)
        self.assertEqual(r.status_code, 302)
        self.assertRedirects(
            r,
            f"{reverse('thanks')}?s=order",
            fetch_redirect_response=False,
        )
        self.assertEqual(Lead.objects.count(), 1)
        lead = Lead.objects.first()
        self.assertEqual(lead.name, "Тест Клиент")
        self.assertTrue(lead.phone.startswith("+7"))

    def test_thanks_page_renders(self):
        r = self.client.get(reverse("thanks"), {"s": "order"})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Спасибо за заявку", status_code=200)

    # --- Срочно: /contacts/ телефон ---

    def test_contacts_form_phone_field_attributes(self):
        r = self.client.get(reverse("contacts"))
        self.assertEqual(r.status_code, 200)
        content = r.content.decode("utf-8")
        self.assertIn('id="id_expert_phone"', content)
        self.assertIn('inputmode="tel"', content)
        self.assertIn("data-phone-mask", content)

    # --- Срочно: /cases/ без ссылок на Google Drive в юр. блоке ---

    def test_cases_page_no_google_drive_in_legal_links(self):
        r = self.client.get(reverse("cases"))
        self.assertEqual(r.status_code, 200)
        content = r.content.decode("utf-8").lower()
        self.assertNotIn("drive.google.com", content)
        self.assertIn(reverse("privacy_policy"), content)

    # --- Важно: meta description ---

    def test_home_has_meta_description(self):
        r = self.client.get(reverse("home"))
        self.assertEqual(r.status_code, 200)
        content = r.content.decode("utf-8")
        self.assertRegex(content, r'<meta[^>]+name=["\']description["\']', re.IGNORECASE)
        m = re.search(
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
            content,
            re.IGNORECASE,
        )
        self.assertIsNotNone(m, msg="meta description с content")
        desc = m.group(1)
        self.assertGreaterEqual(len(desc), 80)
        self.assertLessEqual(len(desc), 400)

    def test_key_pages_have_meta_description(self):
        names = [
            "about",
            "services",
            "cases",
            "team",
            "contacts",
            "order_quiz",
            "thanks",
            "process",
            "blog",
            "catalog",
            "privacy_policy",
            "data_processing_policy",
            "terms_of_use",
        ]
        for name in names:
            with self.subTest(url=name):
                r = self.client.get(reverse(name))
                self.assertEqual(r.status_code, 200)
                self.assertContains(r, 'name="description"', status_code=200)

    # --- После HTTPS: Schema.org ---

    def test_home_has_localbusiness_json_ld(self):
        r = self.client.get(reverse("home"))
        self.assertEqual(r.status_code, 200)
        blocks = _extract_ld_json_blocks(r.content.decode("utf-8"))
        self.assertTrue(blocks, msg="должен быть хотя бы один блок ld+json")
        found = any(
            b.get("@type") == "LocalBusiness" or b.get("@type") == ["LocalBusiness"]
            for b in blocks
        )
        self.assertTrue(found, msg="LocalBusiness на главной")
        lb = next(b for b in blocks if b.get("@type") == "LocalBusiness")
        self.assertEqual(lb.get("name"), "AUTOPARK")
        self.assertIn("telephone", lb)

    def test_cases_has_itemlist_json_ld(self):
        r = self.client.get(reverse("cases"))
        self.assertEqual(r.status_code, 200)
        blocks = _extract_ld_json_blocks(r.content.decode("utf-8"))
        found = any(b.get("@type") == "ItemList" for b in blocks)
        self.assertTrue(found, msg="ItemList на странице кейсов")

    # --- Важно: счётчики — не «0» в исходном HTML ---

    def test_home_hero_stats_not_bare_zero(self):
        r = self.client.get(reverse("home"))
        self.assertEqual(r.status_code, 200)
        content = r.content.decode("utf-8")
        self.assertIn("hero-stat-value", content)
        self.assertRegex(content, r'data-value="450"[^>]*>\s*450\+')
        self.assertRegex(content, r'data-value="870"[^>]*>\s*870\s*000\s*₽')

    def test_about_stats_not_bare_zero(self):
        r = self.client.get(reverse("about"))
        self.assertEqual(r.status_code, 200)
        content = r.content.decode("utf-8")
        self.assertIn("abt-stat-value", content)
        self.assertRegex(content, r'data-value="450"[^>]*>\s*450\+')

    # --- Важно: навигация хедер ↔ футер (бургер содержит услуги, каталог, процесс) ---

    def test_burger_menu_includes_services_catalog_process(self):
        r = self.client.get(reverse("home"))
        self.assertEqual(r.status_code, 200)
        content = r.content.decode("utf-8")
        self.assertIn(reverse("services"), content)
        self.assertIn(reverse("catalog"), content)
        self.assertIn(reverse("process"), content)

    # --- Инфра / аудит «после HTTPS» ---

    def test_whitenoise_static_max_age_one_year(self):
        self.assertEqual(getattr(settings, "WHITENOISE_MAX_AGE", None), 31536000)

    def test_no_google_fonts_stylesheet_in_base(self):
        r = self.client.get(reverse("home"))
        self.assertEqual(r.status_code, 200)
        content = r.content.decode("utf-8")
        self.assertNotIn("fonts.googleapis.com", content)
        self.assertIn("fonts-montserrat.css", content)
