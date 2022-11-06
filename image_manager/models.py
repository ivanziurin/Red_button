import os

from django.db import models
from django.utils import timezone


class SparePartModel(models.Model):
    item_number = models.CharField(max_length=20)
    name = models.CharField(max_length=100, default='object description')
    min_value = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Spare part"
        verbose_name_plural = "Spare parts"


class StockModel(models.Model):
    title = models.CharField(max_length=100)
    raw_img = models.ImageField(null=True, blank=True, upload_to='images')
    result_img = models.ImageField(null=True, blank=True, upload_to='yolo_out')
    datetime = models.DateTimeField(default=timezone.now)
    all_spare_parts = models.ManyToManyField(SparePartModel, related_name='all_parts', through='Relationship')

    def __str__(self):
        return self.title


class Relationship(models.Model):
    SparePart = models.ForeignKey(SparePartModel, on_delete=models.CASCADE, related_name='StockOnDate')
    Stock = models.ForeignKey(StockModel, on_delete=models.CASCADE, related_name='SpareParts')
    quantity = models.IntegerField()
