Поместите сюда hero.mp4 для фонового видео на главной.

Чтобы видео отображалось на сайте и в Git:
  1. Скопируйте файл: cp /путь/к/hero.mp4 static/video/hero.mp4
  2. Закоммитьте: git add static/video/hero.mp4 && git commit -m "Add hero video"
  3. На сервере: git pull && docker compose build --no-cache && docker compose up -d

Видео раздаётся по /video/hero.mp4 с поддержкой перемотки (Range).
