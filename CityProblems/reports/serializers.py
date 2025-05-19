from rest_framework import serializers
from .models import Problem, ProblemImage


class ProblemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemImage
        fields = ['id', 'image']  # Порядок полей можно менять


class ProblemSerializer(serializers.ModelSerializer):
    problem_type = serializers.StringRelatedField()
    images = ProblemImageSerializer(many=True, read_only=True)

    class Meta:
        model = Problem
        fields = [
            'id',
            'problem_type',
            'short_description',
            'full_description',
            'address',
            'latitude',
            'longitude',
            'status',
            'created_at',
            'images'
        ]
        read_only_fields = ['status', 'created_at']  # Добавьте при необходимости