from django.db import models


class complaintboxregister(models.Model):
    name=models.CharField(max_length=200)
    phone=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    image=models.CharField(max_length=200)
    password=models.CharField(max_length=200)


class complaintboxfaculty(models.Model):
    designation=models.CharField(max_length=200)
    name=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    password=models.CharField(max_length=200)


class complaintboxcomplaint(models.Model):
    userid=models.IntegerField()
    complaintto=models.CharField(max_length=200)
    date=models.CharField(max_length=200)
    name=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    complaintmesg=models.CharField(max_length=200)
    status=models.CharField(max_length=200)

class complaintboxacknowledgement(models.Model):
    replyto=models.IntegerField()
    date=models.CharField(max_length=200)
    name=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    ackmesg=models.CharField(max_length=200)


class complaintboxackadmfac(models.Model):
    ackto=models.IntegerField()
    date=models.CharField(max_length=200)
    name=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    ackmesg=models.CharField(max_length=200)
