from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.urls import reverse

class UserProfile(models.Model):

	ROLES=(
        ('C','Casual'),
        ('P','Premium'),
        ('V','Commercial'),
        
    )
	user=models.OneToOneField(User,on_delete=models.DO_NOTHING,)
	city=models.CharField(max_length=100,default='')
	website=models.CharField(max_length=100,default='')
	phone=models.IntegerField(default='0')
	role=models.CharField(max_length=1,choices=ROLES,editable=True)
	image = models.ImageField(upload_to='profile_image', blank=True)
	privatekey=models.TextField(editable=True,blank=True)
	secretkey=models.TextField(editable=True,blank=True)


	def __str__(self):
		return self.user.username

def create_profile(sender,**kwargs):
	if kwargs['created']:
		user_profile=UserProfile.objects.create(user=kwargs['instance'])

post_save.connect(create_profile,sender=User)


class Account(models.Model):

    

    

    user=models.ForeignKey(UserProfile, related_name=("users"), on_delete=models.DO_NOTHING,null=True,blank=True)
    balance=models.IntegerField(default=10000)
    accountid=models.IntegerField(default=3,primary_key=True, unique=True)
    
    
    def __str__(self):
        details=self.user.user.username+" : "+str(self.accountid)
        return str(details)


class Transaction(models.Model):

    
    TYPE=(
        ('T','Transfer'),
    )
    user=models.ForeignKey(UserProfile, null=True,blank=True, on_delete=models.DO_NOTHING)
    from_account=models.ForeignKey(Account, related_name="from_account", on_delete=models.DO_NOTHING,null=True,blank=True)
    to_account=models.ForeignKey(Account, related_name="to_account", on_delete=models.DO_NOTHING,null=True,blank=True)
    # LIMIT=10000
    amount=models.IntegerField(default=0)
    ttype=models.CharField(max_length=2,choices=TYPE,editable=False,blank=True)
    transaction_time=models.DateTimeField(auto_now=True)
    limit=models.IntegerField(default=15)

    def __str__(self):
        from_account="Money" if not self.from_account else str(self.from_account.accountid)
        to_account="Money" if not self.to_account else str(self.to_account.accountid)
        return str(self.id)+" : "+from_account+" "+to_account+" "+str(self.amount)+" "+self.get_status_display()

    @staticmethod
    
    def create(userid,from_account,to_account,amount,ttype):
        userobject=UserProfile.objects.all()
        for users in userobject:
            if users.user.id==userid:
                actualuser=users
                break
        transaction=Transaction(user=actualuser,from_account=from_account,to_account=to_account,amount=amount,ttype='T')
        transaction.save()
        return transaction        
# Create your models here.
