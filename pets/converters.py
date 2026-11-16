from django.urls.converters import SlugConverter


class UnicodeSlugConverter(SlugConverter):
    regex = r"[-\w]+"
