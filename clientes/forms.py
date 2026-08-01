from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import Cliente, Divida


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                css_class = 'form-select'
            else:
                css_class = 'form-control'
            field.widget.attrs.update({'class': css_class})


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                css_class = 'form-select'
            else:
                css_class = 'form-control'
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.order_by('nome')
        self.fields['cliente'].label_from_instance = self._rotulo_cliente
        self.fields['cliente'].widget.attrs.update({
            'data-client-select': 'true',
            'autocomplete': 'off',
        })

    @staticmethod
    def _rotulo_cliente(cliente):
        telefone = cliente.telefone.strip() if cliente.telefone else 'sem telefone'
        return f'{cliente.nome} — {telefone}'

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
        help_text='Use uma senha forte e exclusiva para o funcionário.',
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
        if password1:
            validate_password(password1, self.instance)
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_staff = False
        if commit:
            user.save()
        return user


class FuncionarioEdicaoForm(BootstrapModelForm):
    password1 = forms.CharField(
        label='Nova senha',
        required=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text='Deixe em branco para manter a senha atual.',
    )
    password2 = forms.CharField(
        label='Confirmar nova senha',
        required=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'is_active', 'is_superuser']
        labels = {
            'username': 'Usuário',
            'first_name': 'Nome',
            'email': 'E-mail',
            'is_active': 'Conta ativa',
            'is_superuser': 'Administrador',
        }
        help_texts = {
            'is_active': 'Desmarque para impedir o login sem apagar o usuário.',
            'is_superuser': 'Administrador pode gerenciar funcionários, backups e configurações administrativas.',
        }

    def __init__(self, *args, actor=None, **kwargs):
        self.actor = actor
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 or password2:
            if password1 != password2:
                self.add_error('password2', 'As senhas não conferem.')
            elif password1:
                validate_password(password1, self.instance)

        if self.actor and self.instance.pk == self.actor.pk:
            if cleaned_data.get('is_superuser') is False:
                self.add_error('is_superuser', 'Você não pode remover seu próprio acesso de administrador.')
            if cleaned_data.get('is_active') is False:
                self.add_error('is_active', 'Você não pode desativar sua própria conta.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = bool(user.is_superuser)
        password1 = self.cleaned_data.get('password1')
        if password1:
            user.set_password(password1)
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
