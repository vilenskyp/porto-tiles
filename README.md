# Azulejos — сайт-галерея португальской плитки

Локальный статический сайт: открой `index.html` в браузере (двойной клик).

## Структура
```
azulejos-gallery/
├── index.html          # сайт: сетка, фильтры (стиль/век/мотив), лайтбокс
├── data.js             # данные галереи (метаданные + категоризация)
├── attributions.csv    # атрибуция: source, page_url, author, license, filename
├── metadata.json       # сырые метаданные Wikimedia Commons API
├── classify.py         # скрипт черновой классификации (можно перезапустить)
└── images/
    ├── large/          # 1600px по длинной стороне — для лайтбокса
    └── thumb/          # 480px — для сетки
```

## Источник и лицензии
Все изображения — Wikimedia Commons (батч 1, скачан 2026-07-18).
Лицензии: CC BY / CC BY-SA / CC0 / Public Domain. Автор и лицензия каждого
изображения показаны в лайтбоксе и в `attributions.csv`.
Оригиналы (часто 4000–6000 px) доступны по ссылке «страница на Commons».

## Фильтр качества (по брифу COWORK-azulejo-gallery.md)
- ≥ 800 px по короткой стороне (мелкие отброшены на этапе выборки);
- дедуп по SHA1 (Commons API);
- только JPEG/PNG.

## Категоризация
Черновая, по категориям Commons + ключевым словам в названиях.
Правила — в `classify.py`; после ручных правок в `data.js` сайт подхватит их сам.

## Следующие батчи (по брифу)
Flickr (нужен API key), Pinterest/Tumblr, Google Arts & Culture (dezoomify-rs).
