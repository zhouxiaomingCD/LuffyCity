from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from Course.models import *
import hashlib


class AccountSerializers(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"

    def create(self, validated_data):
        salt = "LuffyCity"
        data = salt + validated_data["pwd"]
        pwd = hashlib.md5(data.encode()).hexdigest()
        validated_data["pwd"] = pwd
        obj = Account.objects.create(**validated_data)
        return obj
