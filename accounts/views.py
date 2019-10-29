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

from .forms import TransferFundsForm, ViewTransactionsForm, DebitFromAccountForm, SearchTransactionForm, SearchTransactionInternalForm, SubmitRequestForm



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
        #IF THE EMPLOYEE ROLE IS 'Y'
        # if role=='C':
        #     return HttpResponseRedirect(reverse('accounts:dashboard'))
        if role=='P':
            return HttpResponseRedirect(reverse('accounts:managerdashboard'))        
        if role=='E':
            return HttpResponseRedirect(reverse('accounts:merchantdashboard'))        

        # #IF THE EMPLOYEE ROLE IS 'A'
        if role=='C':
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

        
class ManagerDashboard(LoginRequiredMixin, TemplateView):
    template_name='manager_dashboard.html'
    login_url='login'

    def get(self,request):
        role=who_is(request)
        # if role=='C':
        #     return HttpResponseRedirect(reverse('accounts:managerdashboard'))     
        # elif role=='P':
        #     return HttpResponseRedirect(reverse('accounts:merchantdashboard'))

        return render(request,'accounts/manager_dashboard.html')

class MerchantDashboard(LoginRequiredMixin,TemplateView):
     template_name='merchant_dashboard.html'
     login_url='login'

     def get(self,request):
        role=who_is(request)
        #IF THE EMPLOYEE ROLE IS 'Y'
        if role=='E':
            return HttpResponseRedirect(reverse('accounts:admindashboard'))
        if role=='P':
            return HttpResponseRedirect(reverse('accounts:managerdashboard'))
        if role=='C':
            return HttpResponseRedirect(reverse('accounts:dashboard'))     

        # #IF THE EMPLOYEE ROLE IS 'B'
        if role=='B':
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
class SubmitRequest(LoginRequiredMixin,TemplateView):
    template_name='merchant_dashboard.html'
    login_url='login'

    def get(self,request):
        role=who_is(request)
        if role=='C':
            return HttpResponseRedirect(reverse('accounts:admindashboard'))
        if role=='P':
            return HttpResponseRedirect(reverse('accounts:managerdashboard'))
        accounts = models.Account.objects.all()
        user_accounts=[]
        for account in accounts:
            if account.user.role=='C':
                user_accounts.append(account)
        form=SubmitRequestForm
        return render(request,'accounts/submit_request.html',context={
            'submit_form':form,
            'user_accounts':user_accounts
        })

    def post(self,request):
        accounts = models.Account.objects.all()
        user_id=request.user.id
        form=SubmitRequestForm(request.POST)
        if form.is_valid():
            from_account=form.cleaned_data['from_account']
            amount=form.cleaned_data['amount']
        if int(amount)<0:
            return render(request,'invalid_input.html')
        flag=0
        for account in accounts:
            if account.accountid==from_account: 
                flag=1
                actualAccount=account
                request=models.Request.create(user_id,actualAccount,amount)
                return HttpResponseRedirect(reverse('accounts:merchantdashboard'))
        if flag==0:
            return render(request,'accounts/invalid_account.html')

class MerchantRequest(LoginRequiredMixin,TemplateView):
    template_name='merchant_request.html'
    login_url='login'

    def get(self,request):
        role=who_is(request)
        if role=='P':
            return HttpResponseRedirect(reverse('accounts:admindashboard'))
        if role=='C':
            return HttpResponseRedirect(reverse('accounts:managerdashboard'))
        requests=models.Request.objects.all()
        request_list=[]
        for req in requests:
            if req.from_account == None:
                continue
            if req.from_account.user.user.id==request.user.id:
                request_list.append(req)
        return render(request,'accounts/merchant_request.html',context={
            'request_list':request_list,
        })

    def post(self, request):
        requests=models.Request.objects.all()
        for req in requests:
            value="approve "+str(req.id)
            if value in request.POST: 
                if req.from_account.balance-req.amount>0:
                    req.from_account.balance-=req.amount
                    req.from_account.save()
                    req.delete()
                    return HttpResponseRedirect(reverse('accounts:merchantrequest'))
                else:
                    return HttpResponseRedirect(reverse('accounts:insufficientbalance'))
            value="decline "+str(req.id)
            if value in request.POST:
                req.delete()
                return HttpResponseRedirect(reverse('accounts:merchantrequest'))
            

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
        # if role=='P':
        #     return HttpResponseRedirect(reverse('accounts:admindashboard'))
        # if role=='C':
        #     return HttpResponseRedirect(reverse('accounts:managerdashboard'))
        form_class=TransferFundsForm
        # return render(request, 'dashboard.html')

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
        secretkey=publickey+current.privatekey
        if secretkey!=current.secretkey:
            return render(request,'accounts/pki_fail.html')

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
                transaction=models.Transaction.create(request.user.id,'S',from_account,to_account,amount,'T')
                return HttpResponseRedirect(reverse('accounts:transferfundcomplete'))
                # return render(request,'transfer_fund_complete.html')    

        else:
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
                        # account.balance-=amount
                        # print(account.balance)
                        # print(3)
                        # account.save()
                        for to in accounts:
                            if to.accountid==to_account:
                                to_account=to
                                # to.balance+=amount
                                # print(4)
                                # to.save()
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
                transaction=models.Transaction.create(request.user.id,'P',from_account,to_account,amount,'T')
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
        role=who_is(request)
        if role=='P':
            return HttpResponseRedirect(reverse('accounts:admindashboard'))
        if role=='C':
            return HttpResponseRedirect(reverse('accounts:managerdashboard'))
        form_class=ViewTransactionsForm
        accounts=models.Account.objects.all()
        # accounts.refresh_from_db()
        # print(accounts)
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
            # print(user_accounts)
            #FOR INPUT VALIDATION
            # for char in raw_from_account:
            #     if ord(char)<48 or ord(char)>57:
            #         return render(request,'invalid_input.html')
            # if len(str(raw_from_account))!=6:
            #     return render(request,'invalid_account.html')            
            
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

class ApproveTransactions(LoginRequiredMixin,TemplateView):
    template_name='approve_transactions.html'
    login_url='login'
    
    def get(self,request):
        role=who_is(request)
        if role=='A':
            return HttpResponseRedirect(reverse('accounts:dashboard'))
        transactions=models.Transaction.objects.all()
        in_process=[]
        for process_transactions in transactions:
            if process_transactions.status=='P' and process_transactions.ttype=='T':
                in_process.append(process_transactions)
        return render(request,'accounts/approve_transactions.html',context={
            'in_process':in_process
        })
    
    def post(self,request):
        from_aux=""
        to_aux=""
        accounts = models.Account.objects.all()
        transactions=models.Transaction.objects.all()
        for trans in transactions:
            value="approve "+str(trans.id)
            if value in request.POST: #APPROVE OF WHICH TRANSACTION
                print(value)
                for account in accounts:
                    if trans.from_account.accountid==account.accountid:
                        from_aux=account
                        print(from_aux)
                    if trans.to_account.accountid==account.accountid:
                        to_aux=account
                # print(from_aux," dfgd")
                if int(from_aux.balance)-int(trans.amount)<0:
                    return render(request,'accounts/approve_account_balance_insufficient.html')
                from_aux.balance-=trans.amount
                to_aux.balance+=trans.amount
                trans.status='S'
                trans.save()
                from_aux.save()
                to_aux.save()
                in_process=[]
                for process_transactions in transactions:
                    if process_transactions.status=='PI':
                        in_process.append(process_transactions)
                return HttpResponseRedirect(reverse('accounts:approvetransactions'))
                # return render(request,'approve_transactions.html',context={
                #     'in_process':in_process
                # })

        for trans in transactions:
            value="decline "+str(trans.id)
            if value in request.POST: #APPROVE OF WHICH TRANSACTION            
                trans.status='R'
                trans.save()
                in_process=[]
                for process_transactions in transactions:
                    if process_transactions.status=='PI' and process_transactions.ttype=='T':
                        in_process.append(process_transactions)
                return HttpResponseRedirect(reverse('accounts:approvetransactions'))
                # return render(request,'approve_transactions.html',context={
                #     'in_process':in_process
                # })
                
        # if request.POST.get("approve"):
        #     transactions=models.Transaction.objects.all()
        #     in_process=[]
        #     for process_transactions in transactions:
        #         if process_transactions.status=='P':
        #             in_process.append(process_transactions)
            
        #     accounts = models.Account.objects.all()
            
            # for trans in in_process:
                
            #     for account in accounts:
            #         if trans.from_account==account.accountid:
            #             from_aux=account
            #         if trans.to_account==account.accountid:
            #             to_aux=account
            #             account.balance-=trans.amount

        # else:

class DebitFromAccount(LoginRequiredMixin,TemplateView):
    template_name='debit_from_account.html'
    login_url='login'

    def get(self,request):
        role=who_is(request)
        # if role=='C':
        #     return HttpResponseRedirect(reverse('admindashboard'))
        if role=='P':
            return HttpResponseRedirect(reverse('accounts:dashboard'))
        accounts = get_accounts(request)
        # account=model
        form=DebitFromAccountForm
        return render(request,'accounts/debit_from_account.html',context={
            'debit_form':form,
            'user_accounts':accounts,
        })
    
    def post(self,request):
        # accounts = models.Account.objects.all()
        user_id=request.user.id
        form=DebitFromAccountForm(request.POST)
        if form.is_valid():
            # print (form.cleaned_data['from_account'])
            from_account=form.cleaned_data['from_account']
            amount=form.cleaned_data['amount']
            option=form.cleaned_data['option']
            publickey=form.cleaned_data['publickey']

        if int(amount)<0:
            return render(request,'accounts/invalid_input.html')
        
        
        accounts=get_accounts(request)
        flag=0
        for account in accounts:
            if account.accountid==from_account: 
                from_account=account

                flag=1
                break
        if flag==0:
            return render(request,'accounts/invalid_account.html')
        else:
            #PKI IMPLEMENTATION
            current=who_is_user(request)
            secretkey=publickey+current.privatekey
            # if secretkey!=current.secretkey:
            #     return render(request,'accounts/pki_fail.html')
            if amount<10000:
                if option=='Debit':
                    if from_account.balance-amount>0:
                        from_account.balance-=amount
                        from_account.save()
                        transaction=models.Transaction.create(request.user.id,'S',from_account,from_account,amount,'D')
                        return HttpResponseRedirect(reverse('accounts:debitcomplete'))
                        # return render(request,'debit_complete.html')
                    else:
                        return render(request,'accounts/insufficient_balance.html')
                elif option=='Credit':
                    from_account.balance+=amount
                    from_account.save()
                    transaction=models.Transaction.create(request.user.id,'S',from_account,from_account,amount,'CR')
                    return HttpResponseRedirect(reverse('accounts:creditcomplete'))
                    # return render(request,'credit_complete.html')
                else:
                    return render(request,'accounts/invalid_input.html')
            else:     
                if option=='Debit':
                    transaction=models.Transaction.create(request.user.id,'PI',from_account,from_account,amount,'D')
                    return HttpResponseRedirect(reverse('accounts:transferfundprocess'))
                    # return render(request,'transfer_fund_process.html')
                    
                elif option=='Credit':
                    transaction=models.Transaction.create(request.user.id,'PI',from_account,from_account,amount,'CR')
                    return HttpResponseRedirect(reverse('accounts:transferfundprocess'))

                    return render(request,'accounts/transfer_fund_process.html')
                else:
                    return render(request,'accounts/invalid_input.html')

class TransferFundProcess(LoginRequiredMixin,TemplateView):
    template_name='transfer_fund_process.html'
    login_url='login'

    def get(self,request):
        return HttpResponseRedirect(reverse('accounts:transferfundprocess'))
        # return render(request,'transfer_fund_process.html')


class DebitComplete(LoginRequiredMixin,TemplateView):
    template_name='debit_complete.html'            
    login_url='login'

    def get(self,request):
        return render(request,'accounts/debit_complete.html')
            
class CreditComplete(LoginRequiredMixin,TemplateView):
    template_name='credit_complete.html'            
    login_url='login'

    def get(self,request):
        return render(request,'accounts/credit_complete.html')
            
class ApproveDebitTransactions(LoginRequiredMixin, TemplateView):
    template_name='approve_debit_transactions.html'
    login_url='login'
    
    def get(self,request):
        role=who_is(request)
        if role=='X':
            return HttpResponseRedirect(reverse('accounts:dashboard'))
        transactions=models.Transaction.objects.all()
        in_process=[]
        for process_transactions in transactions:
            if process_transactions.status=='PI' and (process_transactions.ttype=='CR' or process_transactions.ttype=='D'):
                in_process.append(process_transactions)
        return render(request,'accounts/approve_debit_transactions.html',context={
            'in_process':in_process
        })
    
    def post(self,request):
        from_aux=""
        to_aux=""
        accounts = models.Account.objects.all()
        transactions=models.Transaction.objects.all()
        role=who_is(request)
        print(role)
        # return HttpResponseRedirect(reverse('approvedebittransactions'))
        for trans in transactions:
            value="approve "+str(trans.id)
            if value in request.POST: #APPROVE OF WHICH TRANSACTION
                print(value)
                if role=='X':
                    return render(request,'accounts/not_sys_manager.html')
                for account in accounts:
                    if trans.from_account.accountid==account.accountid:
                        from_aux=account
                        
                # print(from_aux," dfgd")
                if trans.ttype=='C':
                    from_aux.balance+=trans.amount
                    from_aux.save()
                    trans.status='S'
                    trans.save()
                    return HttpResponseRedirect(reverse('approvedebittransactions'))

                else:
                    if int(from_aux.balance)-int(trans.amount)<0:
                        return render(request,'accounts/approve_account_balance_insufficient.html')
                    from_aux.balance-=trans.amount
                    # to_aux.balance+=trans.amount
                    trans.status='S'
                    trans.save()
                    from_aux.save()
                    return HttpResponseRedirect(reverse('accounts:approvedebittransactions'))

        for trans in transactions:
            value="decline "+str(trans.id)
            if value in request.POST: #APPROVE OF WHICH TRANSACTION            
                if role=='C':
                    return render(request,'not_sys_manager.html')
                trans.status='R'
                trans.save()
                return HttpResponseRedirect(reverse('accounts:approvedebittransactions'))

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

class SearchTransactions(LoginRequiredMixin,TemplateView):
    template_name='search_transactions.html'
    login_url='login'

    def get(self,request):
        role=who_is(request)
        if role=='P':
            return HttpResponseRedirect(reverse('accounts:admindashboard'))
        form=SearchTransactionForm
        accounts=get_accounts(request)
        return render(request,'accounts/search_transactions.html',context={
            'search_form':form,
            'user_accounts':accounts,
        })

    def post(self,request):
        search_form=SearchTransactionForm
        form=SearchTransactionForm(request.POST)
        if form.is_valid():
            amount=form.cleaned_data['amount']
            option=form.cleaned_data['option']
        user_id=request.user.id
        accounts=get_accounts(request)
        if amount<0:
            return render(request,'accounts:invalid_input.html')
        transactions=models.Transaction.objects.all()
        if option=='Lower':
            trans_list=[]
            for trans in transactions:
                if (trans.from_account.user.user.id==user_id or trans.to_account.user.user.id==user_id) and trans.amount<amount:
                    trans_list.append(trans)
            return render(request,'accounts/search_transactions.html',context={
                'transaction_list':trans_list,
                'user_accounts':accounts,
                'search_form':form,
            })

        elif option=='Greater':
            trans_list=[]
            for trans in transactions:
                if (trans.from_account.user.user.id==user_id or trans.to_account.user.user.id==user_id) and trans.amount>=amount:
                    trans_list.append(trans)
            return render(request,'accounts/search_transactions.html',context={
                'transaction_list':trans_list,
                'user_accounts':accounts,
                'search_form':form,
            })
        else:
            return render(request,'accounts/invalid_input.html')

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

class ArticleListView(LoginRequiredMixin,ListView):
    model=models.Article 
    template_name='article_list.html'
    login_url='login'

    # def my_view(request):
    #     current=self.request.user
    #     return render_to_response('article_list.html',{'current':current})

class ArticleDetailView(LoginRequiredMixin,DetailView):
    model = models.Article
    template_name = 'article_detail.html'
    login_url='login'

class ArticleUpdateView(LoginRequiredMixin,UpdateView):
    model = models.Article
    fields = ['title', 'body', ]
    template_name = 'article_edit.html'
    login_url='login'

class ArticleDeleteView(LoginRequiredMixin,DeleteView):
    model = models.Article
    template_name = 'article_delete.html'
    success_url=reverse_lazy('article_list')
    login_url='login'

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = models.Article
    template_name = 'article_new.html'
    fields = ['title', 'body',]
    login_url='login'

    def form_valid(self,form):
        form.instance.author=self.request.user
        return super().form_valid(form)

# Create your views here.
