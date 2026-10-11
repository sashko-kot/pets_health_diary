from django.http import HttpResponse
from django.utils.html import escape


def page(title, content):
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
        "/dist/css/bootstrap.min.css"
    )
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)}</title>
    <link rel="icon" href="data:,">
    <link rel="stylesheet" href="{bootstrap}">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="/">ГрызЗдоровье</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">Главная</a>
                <a class="nav-link" href="/pets/">Питомцы</a>
                <a class="nav-link" href="/records/">Дневник</a>
            </div>
        </div>
    </nav>
    <main class="container">{content}</main>
</body>
</html>"""


def index(request):
    content = """
    <h1 class="display-4">Дневник здоровья грызунов</h1>
    <p class="lead">
        Система контроля самочувствия, веса и ухода за питомцами.
    </p>
    <hr class="my-4">
    <p>Основные разделы:</p>
    <a href="/pets/" class="btn btn-primary me-2">Мои питомцы</a>
    <a href="/records/" class="btn btn-secondary">Записи в дневнике</a>
    """
    return HttpResponse(page("Главная | Дневник грызунов", content))


def page_not_found(request, exception):
    content = """
    <h1 class="text-danger">404 — Страница не найдена</h1>
    <p>Проверьте правильность введенного адреса или вернитесь на главную.</p>
    <a href="/" class="btn btn-primary">На главную</a>
    """
    return HttpResponse(page("404 — Не найдено", content), status=404)
