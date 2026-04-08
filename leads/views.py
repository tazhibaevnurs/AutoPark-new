import time

from django.shortcuts import redirect
from django.views.generic import FormView
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from .antispam import SESSION_TS_KEY
from .forms import (
    LeadForm,
    CarSearchForm,
    BuyoutForm,
    DeliveryForm,
    RegistrationForm,
    ExpertQuestionForm,
    MotorcycleSalesForm,
)


class LeadFormViewMixin:
    """Сессия для антиспама (время открытия формы) и request в форме."""

    thanks_source = 'order'

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            request.session[SESSION_TS_KEY] = time.time()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        return f"{reverse('thanks')}?s={self.thanks_source}"


@method_decorator(ensure_csrf_cookie, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class OrderQuizView(LeadFormViewMixin, FormView):
    """Отображение формы заявки и сохранение в БД при валидном POST."""
    template_name = 'pages/order_quiz.html'
    form_class = LeadForm
    thanks_source = 'order'

    def form_valid(self, form):
        form.instance.vehicle_type = 'car'
        form.save()
        return super().form_valid(form)


def order_quiz_success_view(request):
    """Совместимость: старый URL перенаправляет на общую страницу «Спасибо»."""
    return redirect(f"{reverse('thanks')}?s=order")


class CarSearchView(LeadFormViewMixin, FormView):
    """Страница «Поиск авто»: React-интерфейс в стиле Million Miles, форма заявки на персональный подбор."""
    template_name = 'pages/car_search_react.html'
    form_class = CarSearchForm
    thanks_source = 'search'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_action'] = reverse('car_search')
        ctx['success_url'] = self.get_success_url()
        form = ctx.get('form')
        ctx['form_errors'] = dict(form.errors) if form and form.errors else None
        return ctx

    def form_valid(self, form):
        form.instance.vehicle_type = 'car'
        form.save()
        return super().form_valid(form)


def car_search_success_view(request):
    return redirect(f"{reverse('thanks')}?s=search")


class BuyoutView(LeadFormViewMixin, FormView):
    """Страница «Выкуп»: заявка на выкуп автомобиля (дизайн как Import/Export)."""
    template_name = 'pages/vykup_react.html'
    form_class = BuyoutForm
    thanks_source = 'buyout'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_action'] = reverse('buyout')
        ctx['success_url'] = self.get_success_url()
        form = ctx.get('form')
        ctx['form_errors'] = dict(form.errors) if form and form.errors else None
        return ctx

    def form_valid(self, form):
        form.instance.vehicle_type = 'car'
        form.save()
        return super().form_valid(form)


def buyout_success_view(request):
    return redirect(f"{reverse('thanks')}?s=buyout")


class DeliveryView(LeadFormViewMixin, FormView):
    """Страница «Доставка авто»: заявка на доставку (дизайн как логистика)."""
    template_name = 'pages/delivery_react.html'
    form_class = DeliveryForm
    thanks_source = 'delivery'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_action'] = reverse('delivery')
        ctx['success_url'] = self.get_success_url()
        form = ctx.get('form')
        ctx['form_errors'] = dict(form.errors) if form and form.errors else None
        return ctx

    def form_valid(self, form):
        form.instance.vehicle_type = 'car'
        form.save()
        return super().form_valid(form)


def delivery_success_view(request):
    return redirect(f"{reverse('thanks')}?s=delivery")


class RegistrationView(LeadFormViewMixin, FormView):
    """Страница «Постановка на учёт»: заявка на постановку (дизайн как Million Miles)."""
    template_name = 'pages/postanovka_react.html'
    form_class = RegistrationForm
    thanks_source = 'registration'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_action'] = reverse('registration')
        ctx['success_url'] = self.get_success_url()
        form = ctx.get('form')
        ctx['form_errors'] = dict(form.errors) if form and form.errors else None
        return ctx

    def form_valid(self, form):
        form.instance.vehicle_type = 'car'
        form.save()
        return super().form_valid(form)


def registration_success_view(request):
    return redirect(f"{reverse('thanks')}?s=registration")


@method_decorator(ensure_csrf_cookie, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class ExpertQuestionView(LeadFormViewMixin, FormView):
    """Страница контактов с формой «вопрос эксперту»."""
    template_name = 'pages/contacts.html'
    form_class = ExpertQuestionForm
    thanks_source = 'contacts'

    def form_valid(self, form):
        form.instance.vehicle_type = 'car'
        form.save()
        return super().form_valid(form)


def contacts_success_view(request):
    return redirect(f"{reverse('thanks')}?s=contacts")


@method_decorator(ensure_csrf_cookie, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class MotorcycleSalesView(LeadFormViewMixin, FormView):
    """Страница «Продажа мотоциклов» с формой заявки."""
    template_name = 'pages/motorcycle_sales.html'
    form_class = MotorcycleSalesForm
    thanks_source = 'moto'

    def form_valid(self, form):
        form.instance.vehicle_type = 'moto'
        form.save()
        return super().form_valid(form)


def motorcycle_sales_success_view(request):
    return redirect(f"{reverse('thanks')}?s=moto")
