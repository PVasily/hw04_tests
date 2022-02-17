from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/about.html'


class TechView(TemplateView):
    template_name = 'about/tech.html'
