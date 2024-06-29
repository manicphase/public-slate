from django.db import models

# Create your models here.
class Constituency(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Constituencies"


class Party(models.Model):
    name = models.CharField(max_length=200)
    manifesto = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Parties"


class Candidate(models.Model):
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Voter(models.Model):
    ip_address = models.CharField(max_length=100)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)

    def __str__(self):
        return self.ip_address

class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    preference = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.voter.ip_address} - vote {self.preference}"