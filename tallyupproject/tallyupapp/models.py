# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.urls import reverse
from django.db import models
import uuid
# Create your models here.

class User(models.Model):
    #Fields
    userID = models.IntegerField(primary_key=True,unique=True, null=False)

    # Metadata
    class Meta:
        ordering = ["-userID"]

    # # Methods
    def get_absolute_url(self):
        """
        Returns the url to access a particular instance of the model.
        """
        return reverse('model-detail-view', args=[str(self.id)]) # this probably won't work
        # need to create a URL mapper to pass the response and id to a "model detail view"

    def __unicode__(self):
        """
        String for representing the MyModelName object (in Admin site etc.)
        """
        return self.userID

class Snapshot(models.Model):
    snapshotID = models.IntegerField(primary_key=True,unique=True, null=False)
    sport = models.CharField(max_length=5, primary_key=True,unique=True, null=False)
    gameID = models.IntegerField(unique=True, null=False)
    time = models.DateTimeField(null=False)
    bet_sender = models.ForeignKey(User, related_name='sender')
    bet_receiver = models.ForeignKey(User, related_name='receiver')
    # Metadata
    class Meta:
        ordering = ["-time"]
    # Methods
    # def get_absolute_url(self):
    #     """
    #     Returns the url to access a particular instance of MyModelName.
    #     """
    #     return reverse('model-detail-view', args=[str(self.id)]) # Methods
    def get_absolute_url(self):
        # Returns the url to access a particular instance of the model.
        return reverse('model-detail-view', args=[str(self.id)])
    def __unicode__(self):
        # String for representing the MyModelName object (in Admin site etc.)
        return self.snapshotID

# model representing a specific instance of a snapshot
class SnapshotInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular bet")
    expiration = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-expiration"]

    def __unicode__(self):
        return '%s (%s)' % (self.id, self.expiration)