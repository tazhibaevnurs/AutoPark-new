# -*- coding: utf-8 -*-
"""Запуск проверки продакшена с DEBUG=False (чтобы не было предупреждений W004, W008, ...)."""
import os
import subprocess
import sys
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Проверка настроек для продакшена (вызывает check --deploy с DEBUG=False)'

    def handle(self, *args, **options):
        env = os.environ.copy()
        env['DEBUG'] = 'False'
        result = subprocess.run(
            [sys.executable, '-X', 'utf8', 'manage.py', 'check', '--deploy'],
            env=env,
            cwd=os.getcwd(),
        )
        sys.exit(result.returncode)
