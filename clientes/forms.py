from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User

from .models import Cliente, Divida


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.update({'class': css_class})


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.update({'class': css_class})


class ClienteForm(BootstrapModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'telefone', 'observacao']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex: João Silva'}),
            'telefone': forms.TextInput(attrs={'placeholder': 'Ex: 81 99999-9999'}),
            'observacao': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Observação opcional'}),
        }


class DividaForm(BootstrapModelForm):
    class Meta:
        model = Divida
        fields = ['cliente', 'valor', 'descricao']
        widgets = {
            'valor': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': 'Ex: 35.00'}),
            'descricao': forms.TextInput(attrs={'placeholder': 'Ex: Corte + barba'}),
        }


class FuncionarioSenhaForm(BootstrapFormMixin, SetPasswordForm):
    """Formulário usado pelo administrador para redefinir a senha de funcionários."""


class FuncionarioForm(BootstrapFormMixin, forms.ModelForm):
    password1 = forms.CharField(
        label='Senha inicial',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text='Use uma senha simples para o funcionário trocar depois, se necessário.',
    )
    password2 = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']
        labels = {
            'username': 'Usuário',
            'first_name': 'Nome',
            'email': 'E-mail',
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('As senhas não conferem.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_staff = False
        if commit:
            user.save()
        return user


class RelatorioPeriodoForm(BootstrapFormMixin, forms.Form):
    data_inicio = forms.DateField(
        label='Data inicial',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    data_fim = forms.DateField(
        label='Data final',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
