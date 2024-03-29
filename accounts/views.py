from django.shortcuts import render ,HttpResponse ,redirect
from accounts.forms import RegistrationForm,EditProfileForm
from django.contrib.auth.forms import UserChangeForm,PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.decorators import login_required


from django.shortcuts import render
from django.views import generic 
from django.urls import reverse_lazy, reverse

from django.views.generic import ListView 
from . import models
from django.http import HttpResponseRedirect
# from django.urls import reverse
from django.shortcuts import render
from django.views.generic import TemplateView 

from django.views.generic import ListView, DetailView 
from django.views.generic.edit import UpdateView, DeleteView, CreateView

from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import TransferFundsForm, ViewTransactionsForm, SearchTransactionInternalForm, SubmitRequestForm



def register(request):
    if request.method =='POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('home:home'))
    else:
        form = RegistrationForm()

        args = {'form': form}
        return render(request, 'accounts/reg_form.html', args)

def view_profile(request, pk=None):
    if pk:
        user = User.objects.get(pk=pk)
    else:
        user = request.user
    args = {'user': user}
    return render(request, 'accounts/profile.html', args)

def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect(reverse('accounts:view_profile'))
    else:
        form = EditProfileForm(instance=request.user)
        args = {'form': form}
        return render(request, 'accounts/edit_profile.html', args)

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect(reverse('accounts:view_profile'))
        else:
            return redirect(reverse('accounts:change_password'))
    else:
        form = PasswordChangeForm(user=request.user)

        args = {'form': form}
        return render(request, 'accounts/change_password.html', args)




#E-wallet
class Dashboard(LoginRequiredMixin, TemplateView):
    template_name='dashboard.html'
    # model=models.Account
    # context_object_name='account'
    login_url='login'
    

    def get(self,request):
        transaction=models.Transaction.objects.all()
        for trans in transaction:
            if trans.from_account == None:
                trans.delete()
        role=who_is(request)
        if role=='C':
            return HttpResponseRedirect(reverse('accounts:merchantdashboard'))        
        if role=='E':
            return HttpResponseRedirect(reverse('accounts:merchantdashboard'))        
        if role=='V':
            accounts = models.Account.objects.all()
            user_id = request.user.id
            selected_accounts=[]
            
           

            for account in accounts:
                # print(account,userx,account.user)
                if account.user.user.id == user_id:
                    selected_accounts.append(account)
            args={'selected_accounts':selected_accounts}       

            return render(request, 'accounts/dashboard.html', args) 
        else:
            return render(request, 'accounts/dashboard.html') 
        


            #print(len(selected_accounts))

class MerchantDashboard(LoginRequiredMixin,TemplateView):
     template_name='merchant_dashboard.html'
     login_url='login'

     def get(self,request):
        role=who_is(request)
        #IF THE EMPLOYEE ROLE IS 'Y'
        if role=='E':
            return HttpResponseRedirect(reverse('accounts:merchantdashboard'))
        if role=='P':
            return HttpResponseRedirect(reverse('accounts:merchantdashboard'))
        if role=='V':
            return HttpResponseRedirect(reverse('accounts:merchantdashboard'))     

        # #IF THE EMPLOYEE ROLE IS 'B'
        
        accounts = models.Account.objects.all()
        user_id = request.user.id
            
        selected_accounts = []

        for account in accounts:
                # print(account,userx,account.user)
            if account.user.user.id == user_id:
                selected_accounts.append(account)

            # print(len(selected_accounts))

        return render(request, 'accounts/merchant_dashboard.html', context = {
                'selected_accounts': selected_accounts,
            })
        # return render(request,'merchant_dashboard.html')


            

class InsufficientBalance(LoginRequiredMixin,TemplateView):
    template_name='insufficient_balance.html'
    login_url='login'
    def get(self,request):
        return render(request,'accounts/insufficient_balance.html')


class TransferFunds(LoginRequiredMixin, TemplateView):
    # form_class=CustomUserCreationForm 

    template_name='transfer_funds.html'
    login_url='login'
    
    def get(self,request):
        role=who_is(request)
        
        form_class=TransferFundsForm
        

        accounts=models.Account.objects.all()
        # accounts.refresh_from_db()
        # print(accounts)
        user_id=request.user.id
        user_accounts=[]
        for account in accounts:
        #     print(account,account.user.id,user_id)
            if account.user.user.id==user_id:
                user_accounts.append(account)
        print(user_accounts)

        return render(request,'accounts/transfer_funds.html',context={
            'user_accounts':user_accounts,
            'transact_form':form_class,
        })

    def post(self,request):
        accounts = models.Account.objects.all()
        user_id=request.user.id
        form=TransferFundsForm(request.POST)
        if form.is_valid():
            print (form.cleaned_data['from_account'])
            from_account=form.cleaned_data['from_account']
            to_account=form.cleaned_data['to_account']
            amount=form.cleaned_data['amount']
            publickey=form.cleaned_data['publickey']

        if int(amount)<0:
            return render(request,'invalid_input.html')
        
        #IF FROM ACCOUNT IS OF CURRENTLY LOGGED IN USER
        all_user_account_ids=[]
        for account in accounts:
            if account.user.user.id==user_id:
                # print(account.accountid,raw_from_account)
                all_user_account_ids.append(account.accountid)
        # print(all_user_account_ids)
        if from_account not in all_user_account_ids:
            print("from account error")
            return render(request,'accounts/invalid_account.html')
        
        #IF 'TO ACCOUNT' IS PART OF ALL LIST OF ACCOUNTS
        all_accounts=[]
        for account in accounts:
            
            all_accounts.append(account.accountid)
        # print(all_accounts,raw_to_account,account.balance)
        if to_account not in all_accounts:
            # print("to account error")
            return render(request,'accounts/invalid_account.html')

        #PKI IMPLEMENTATION
        current=who_is_user(request)
        # secretkey=publickey+current.privatekey
        # if secretkey!=current.secretkey:
        #     return render(request,'accounts/pki_fail.html')

        #IF EVERYTHING'S RIGHT
        flag=0
        if amount<=10000:            
            for account in accounts:
                # print(account.balance,raw_amount)
                if account.accountid==from_account: 
                    from_account=account
                    # print(account.balance,raw_amount)
                    # print(1)
                    if account.balance>=amount:
                        # print(account.balance,raw_amount)
                        # print(2)
                        flag=1
                        account.balance-=amount
                        # print(account.balance)
                        # print(3)
                        account.save()
                        for to in accounts:
                            if to.accountid==to_account:
                                to_account=to
                                to.balance+=amount
                                # print(4)
                                to.save()
                                break
                    break
            if flag==0: #ACCOUNT BALANCE IS LESS THAN THE AMOUNT 
                return render(request,'accounts/insufficient_balance.html')
            else:
            
            #IF EVERYTHING WAS SUCCESSFUL
            # accounts.update()
            # models.Account.objects.save()
            # for account in accounts:
            #     account.save()

                # transaction=models.Transaction.create(from_account,to_account,int(raw_amount),request.user,'S')
                transaction=models.Transaction.create(request.user.id,from_account,to_account,amount,'T')
                return HttpResponseRedirect(reverse('accounts:transferfundcomplete'))
                # return render(request,'transfer_fund_complete.html')    

        else:
            for account in accounts:
                # print(account.balance,raw_amount)
                if account.accountid==from_account: 
                    from_account=account
                    
                    if account.balance>=amount:
                       
                        flag=1
                        
                        for to in accounts:
                            if to.accountid==to_account:
                                to_account=to
                                
                                break
                    break
            if flag==0: 
                return render(request,'accounts/insufficient_balance.html')
            else:
            
           
                transaction=models.Transaction.create(request.user.id,from_account,to_account,amount,'T')
                return HttpResponseRedirect(reverse('accounts:transferfundprocess'))
                # return render(request,'transfer_fund_process.html')

            # print(blah)
            return render(request, 'accounts/dashboard.html')
        
class TransferFundComplete(LoginRequiredMixin, TemplateView):
    template_name='transfer_fund_complete.html'
    login_url='login'

    def get(self,request):
        return render(request,'accounts/transfer_fund_complete.html')

def who_is(request):
    role=request.user.id 
    for all_users in models.UserProfile.objects.all():
        if all_users.user.id==role:
            actual_user=all_users
    return actual_user.role

def who_is_user(request):
    role=request.user.id 
    for all_users in models.UserProfile.objects.all():
        if all_users.user.id==role:
            actual_user=all_users
    return actual_user
    # print(actual_user.role)


class ViewTransactions(LoginRequiredMixin,TemplateView):
    template_name='view_transactions.html'
    login_url='login'

    def get(self,request):
        form_class=ViewTransactionsForm
        accounts=models.Account.objects.all()
        user_id=request.user.id
        user_accounts=[]
        for account in accounts:
            # print(account,account.user.id,user_id)
            if account.user.user.id==user_id:
                user_accounts.append(account)
        print(user_accounts)

        return render(request,'accounts/view_transactions.html',context={
            'user_accounts':user_accounts,
            'view_transactions':form_class,
        })

    def post(self,request):
        accounts = models.Account.objects.all()
        user_id=request.user.id
        form=ViewTransactionsForm(request.POST)
        if form.is_valid():
            # print (form.cleaned_data['from_account'])
            from_account=form.cleaned_data['from_account']
            # raw_from_account=request.POST.get('from_account_number')            
            user_id=request.user.id
            user_accounts=[]
            for account in accounts:
                # print(account,account.user.id,user_id)
                if account.user.user.id==user_id:
                    user_accounts.append(account)
        
            all_user_account_ids=[]
            for account in accounts:
                if account.user.user.id==user_id:
                    # print(account.accountid,raw_from_account)
                    all_user_account_ids.append(account.accountid)
            # print(all_user_account_ids)
            if from_account not in all_user_account_ids:
                print("from account error")
                return render(request,'accounts/invalid_account.html')
        
            transactions=models.Transaction.objects.all()
            print(transactions)
            trans_to_show=[]
            for trans in transactions:
                if trans.from_account==None:
                    continue
                if from_account==trans.from_account.accountid:
                    print("success")
                    trans_to_show.append(trans)
            print(trans_to_show)
            return render(request,'accounts/view_transactions.html',context={
                'transaction_list':trans_to_show,
                'user_accounts':user_accounts,
                'view_transactions':form,
            })
        return render(request, 'accounts/invalid_account.html') #MEANS THERE'S AN ERROR IN FORM 





class TransferFundProcess(LoginRequiredMixin,TemplateView):
    template_name='transfer_fund_process.html'
    login_url='login'

    def get(self,request):
        return HttpResponseRedirect(reverse('accounts:transferfundprocess'))
        # return render(request,'transfer_fund_process.html')


            

            


class SearchTransactions(LoginRequiredMixin,TemplateView):
    template_name='search_transactions.html'
    login_url='login'

    def get(self,request):
        form=SearchTransactionForm
        accounts=get_accounts(request)
        return render(request,'accounts/search_transactions.html',context={
            'search_form':form,
            'user_accounts':accounts,
        })

    def post(self,request):
        search_form=SearchTransactionForm
        form=SearchTransactionForm(request.POST)
        #if form.is_valid():
            #amount=form.cleaned_data['amount']
            #option=form.cleaned_data['option']
        user_id=request.user.id
        accounts=get_accounts(request)
        if amount<0:
            return render(request,'accounts:invalid_input.html')
        transactions=models.Transaction.objects.all()
        trans_list=[]
        for trans in transactions:
            if (trans.from_account.user.user.id==user_id or trans.to_account.user.user.id==user_id) and trans.amount<amount:
                trans_list.append(trans)
        return render(request,'accounts/search_transactions.html',context={
                'transaction_list':trans_list,
                'user_accounts':accounts,
                'search_form':form,
            })
            

        
       

class SearchTransactionsInternal(LoginRequiredMixin, TemplateView):
    template_name='search_transactions_internal.html'
    login_url='login'

    def get(self,request):
        role=who_is(request)
        if role=='P':
            return HttpResponseRedirect(reverse('accounts:admindashboard'))
        form=SearchTransactionInternalForm
        accounts=models.Account.objects.all()
        return render(request,'accounts/search_transactions_internal.html',context={
            'search_form':form,
            'user_accounts':accounts,
        })

    def post(self,request):
        form=SearchTransactionInternalForm(request.POST)
        if form.is_valid():
            from_account=form.cleaned_data['from_account']
            accounts=models.Account.objects.all()        
            trans_list=[]
            transactions=models.Transaction.objects.all()
            for trans in transactions:
                if trans.from_account.accountid==from_account:
                    trans_list.append(trans)
            return render(request,'accounts/search_transactions_internal.html',context={
                'transaction_list':trans_list,
                'user_accounts':accounts,
                'search_form':form,
            })
        else:
            return render(request,'accounts/invalid_input.html')


class SignUp(generic.CreateView):
    # form_class=CustomUserCreationForm 
    template_name='signup.html'

    success_url=reverse_lazy('login')
    #template_name='signup.html'

class HomePageView(TemplateView):
    template_name='home.html'

def get_accounts(request):
    accounts = models.Account.objects.all()
    user_id=request.user.id
    user_accounts=[]
    for account in accounts:
        # print(account,account.user.id,user_id)
        if account.user.user.id==user_id:
            user_accounts.append(account)
    # print(user_accounts)
    return user_accounts    


