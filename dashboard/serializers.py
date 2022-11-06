from rest_framework import serializers


class SparePartModelSerializer(serializers.Serializer):
    item_number = serializers.CharField()
    min_value = serializers.IntegerField()