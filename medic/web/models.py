from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Official_Diagnosis(models.Model):
    illness = models.CharField(max_length=250)
    diagnosis = models.CharField( max_length=500)
    offical = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self) -> str:
        return self.offical.username+"("+self.illness+")"