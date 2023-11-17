from django.db import models

class User(models.Model):
    login = models.CharField(unique=True, max_length=10)
    token = models.CharField(max_length=100)
    def __str__(self):
        return self.login