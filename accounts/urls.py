from django.conf.urls import url
#from django.core.urlresolvers import reverse
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
#from django.contrib.auth.views import password_reset_done
from django.contrib.auth.views import PasswordResetView,PasswordResetDoneView,PasswordResetConfirmView,PasswordResetCompleteView

from django.urls import path

app_name = 'accounts'
urlpatterns = [
#url(r'^$',views.home),
url(r'^login/$',auth_views.LoginView.as_view(template_name='accounts/login.html'),name='login'),
url(r'^logout/$',auth_views.LogoutView.as_view(template_name='accounts/logout.html'),name='logout'),
url(r'^register/$',views.register,name='register'),
url(r'^profile/$',views.view_profile,name='view_profile'),
url(r'^profile/(?P<pk>\d+)/$', views.view_profile, name='view_profile_with_pk'),
url(r'^profile/edit/$',views.edit_profile,name='edit_profile'),
url(r'^change-password/$',views.change_password,name='change_password'),
path(
        'reset-password/',
        PasswordResetView.as_view(template_name='accounts/reset_password.html'),
        name='reset_password'
    ),
path('reset-password/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
url(r'^reset-password/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
path('reset-password/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),




path('admin/',views.Dashboard.as_view(),name='admindashboard'),
path('dashboard/',views.Dashboard.as_view(template_name='accounts/dashboard.html'),name='dashboard'),
path('transferfunds/',views.TransferFunds.as_view(template_name='transfer_funds.html'),name='transferfunds'),
path('viewtransactions/',views.ViewTransactions.as_view(),name='viewtransactions'),
#path('approve_transactions.html/',views.ApproveTransactions.as_view(),name='approvetransactions'),
#path('debit_from_account.html/',views.DebitFromAccount.as_view(template_name='accounts/debit_from_account.html'),name='debitfromaccount'),
#path('approve_debit_transactions.html/',views.ApproveDebitTransactions.as_view(),name='approvedebittransactions'),
path('search_transactions.html/',views.SearchTransactions.as_view(),name='searchtransactions'),
path('search_transactions_internal.html/',views.SearchTransactionsInternal.as_view(),name='searchtransactionsinternal'),
path('merchant_dashboard.html/',views.MerchantDashboard.as_view(),name='merchantdashboard'),
#path('submit_request.html/',views.SubmitRequest.as_view(),name='submitrequest'),
#path('merchant_request.html/',views.MerchantRequest.as_view(),name='merchantrequest'),
path('insufficient_balance.html/',views.InsufficientBalance.as_view(),name='insufficientbalance'),
path('transfer_fund_complete.html/',views.TransferFundComplete.as_view(),name='transferfundcomplete'),
path('transfer_fund_process.html/',views.TransferFundProcess.as_view(),name='transferfundprocess'),
#path('debit_complete.html/',views.DebitComplete.as_view(),name='debitcomplete'),
#path('credit_complete.html/',views.CreditComplete.as_view(),name='creditcomplete'),
]