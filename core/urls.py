from django.urls import path

from core.forms import CustomPasswordChangeForm
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    #Perfil usuarios
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/alterar/', views.alterar_perfil, name='alterar_perfil'),
    path('perfil/excluir/', views.excluir_conta, name='excluir_conta'),
    
    path('trocar-senha/', auth_views.PasswordChangeView.as_view(
    form_class=CustomPasswordChangeForm,
    template_name='registration/password_change_form.html',
    success_url='/senha-alterada/'
    ), name='trocar_senha_usuario'),

    path('senha-alterada/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),


    #Relatorios
    path('relatorio/', views.gerar_relatorio, name='gerar_relatorio'),

    #Contas bancárias
    path('bancos/', views.listar_contas, name='listar_contas'),
    path('bancos/nova/', views.criar_conta, name='criar_conta'),
    path('bancos/<int:conta_id>/editar/', views.editar_conta, name='editar_conta'),
    path('bancos/<int:conta_id>/excluir/', views.excluir_conta, name='excluir_conta'),

    
    #Login
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),


    #Lançamentos
    path("lancar/", views.lancar_movimento, name="lancar"),
    path("lancamentos/", views.listar_lancamentos, name="listar_lancamentos"),
    path('lancamento/novo/', views.criar_lancamento, name='criar_lancamento'),
    path('lancamento/<int:lancamento_id>/editar/', views.editar_lancamento, name='editar_lancamento'),
    path('lancamentos/<int:pk>/excluir/', views.excluir_lancamento, name='excluir_lancamento'),
    path("lancamento/<int:lancamento_id>/comprovante/", views.visualizar_comprovante, name="visualizar_comprovante"),
    
    
    #Categorias
    path('categorias/', views.listar_categorias, name='listar_categorias'),
    path('categorias/nova/', views.cadastrar_categoria, name='cadastrar_categoria'),
    path('categorias/<int:id>/editar/', views.editar_categoria, name='editar_categoria'),
    path("categorias/<int:id>/excluir/", views.excluir_categoria, name="excluir_categoria"),

]
