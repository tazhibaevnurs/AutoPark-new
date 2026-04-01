from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from .forms import (
    LeadForm,
    CarSearchForm,
    BuyoutForm,
    DeliveryForm,
    RegistrationForm,
    ExpertQuestionForm,
    MotorcycleSalesForm,
)


@method_decorator(ensure_csrf_cookie, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class OrderQuizView(FormView):
    """Отображение формы заявки и сохранение в БД при валидном POST."""
    template_name = 'pages/order_quiz.html'
    form_class = LeadForm
    success_url = reverse_lazy('order_quiz_success')

    def form_valid(self, form):
        form.instance.vehicle_type = 'car'
        form.save()
        return redirect(self.get_success_url())


def order_quiz_success_view(request):
    """Страница успешной отправки заявки."""
    return render(request, 'pages/order_quiz_success.html')


class CarSearchView(FormView):
    """Страница «Поиск авто»: React-интерфейс в стиле Million Miles, форма заявки на персональный подбор."""
    template_name = 'pages/car_search_react.html'
    form_class = CarSearchForm
    success_url = reverse_lazy('car_search_success')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_action'] = reverse('car_search')
        ctx['success_url'] = reverse('car_search_success')
        form = ctx.get('form')
        ctx['form_errors'] = dict(form.errors) if form and form.errors else None
        return ctx

    def form_valid(self, form):
        form.instance.vehicle_type = 'car'
        form.save()
        return redirect(self.get_success_url())


def car_search_success_view(request):
    """Успешная отправка заявки на поиск авто."""
    return render(request, 'pages/car_search_success.html')


class BuyoutView(FormView):
    """Страница «Выкуп»: заявка на выкуп автомобиля (дизайн как Import/Export)."""
    template_name = 'pages/vykup_react.html'
    form_class = BuyoutForm
    success_url = reverse_lazy('buyout_success')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_action'] = reverse('buyout')
        ctx['success_url'] = reverse('buyout_success')
        form = ctx.get('form')
        ctx['form_errors'] = dict(form.errors) if form and form.errors else None
        return ctx

    def form_valid(self, form):
        form.instance.vehicle_type = 'car'
        form.save()
        return redirect(self.get_success_url())


def buyout_success_view(request):
    """Успешная отправка заявки на выкуп."""
    return render(request, 'pages/buyout_success.html')


class DeliveryView(FormView):
    """Страница «Доставка авто»: заявка на доставку (дизайн как логистика)."""
    template_name = 'pages/delivery_react.html'
    form_class = DeliveryForm
    success_url = reverse_lazy('delivery_success')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_action'] = reverse('delivery')
        ctx['success_url'] = reverse('delivery_success')
        form = ctx.get('form')
        ctx['form_errors'] = dict(form.errors) if form and form.errors else None
        return ctx

    def form_valid(self, form):
        form.instance.vehicle_type = 'car'
        form.save()
        return redirect(self.get_success_url())


def delivery_success_view(request):
    """Успешная отправка заявки на доставку."""
    return render(request, 'pages/delivery_success.html')


class RegistrationView(FormView):
    """Страница «Постановка на учёт»: заявка на постановку (дизайн как Million Miles)."""
    template_name = 'pages/postanovka_react.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('registration_success')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_action'] = reverse('registration')
        ctx['success_url'] = reverse('registration_success')
        form = ctx.get('form')
        ctx['form_errors'] = dict(form.errors) if form and form.errors else None
        return ctx

    def form_valid(self, form):
        form.instance.vehicle_type = 'car'
        form.save()
        return redirect(self.get_success_url())


def registration_success_view(request):
    """Успешная отправка заявки на постановку на учёт."""
    return render(request, 'pages/registration_success.html')


class ExpertQuestionView(FormView):
    """Страница контактов с формой «вопрос эксперту»."""
    template_name = 'pages/contacts.html'
    form_class = ExpertQuestionForm
    success_url = reverse_lazy('contacts_success')

    def form_valid(self, form):
        form.instance.vehicle_type = 'car'
        form.save()
        return redirect(self.get_success_url())


def contacts_success_view(request):
    """Страница успешной отправки заявки с контактов."""
    return render(request, 'pages/contacts_success.html')


@method_decorator(ensure_csrf_cookie, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class MotorcycleSalesView(FormView):
    """Страница «Продажа мотоциклов» с формой заявки."""
    template_name = 'pages/motorcycle_sales.html'
    form_class = MotorcycleSalesForm
    success_url = reverse_lazy('motorcycle_sales_success')

    def form_valid(self, form):
        form.instance.vehicle_type = 'moto'
        form.save()
        return redirect(self.get_success_url())


def motorcycle_sales_success_view(request):
    """Успешная отправка заявки на мотоцикл."""
    return render(request, 'pages/motorcycle_sales_success.html')
