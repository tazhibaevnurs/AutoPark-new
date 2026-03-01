from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.urls import reverse_lazy

from .forms import LeadForm


class OrderQuizView(FormView):
    """Отображение формы заявки и сохранение в БД при валидном POST."""
    template_name = 'pages/order_quiz.html'
    form_class = LeadForm
    success_url = reverse_lazy('order_quiz_success')

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())


def order_quiz_success_view(request):
    """Страница успешной отправки заявки."""
    return render(request, 'pages/order_quiz_success.html')
