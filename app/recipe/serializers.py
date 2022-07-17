"""
Serializers for the Recipe API
"""

from rest_framework import serializers

from core.models import Ingredient, Recipe, Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients"""

    class Meta:
        model = Ingredient
        fields = ["id", "name"]
        read_only_fields = ["id"]


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for the Tag model
    """

    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Recipe model
    """

    tags = TagSerializer(many=True, required=False,)
    ingredients = IngredientSerializer(many=True, required=False,)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "title",
            "time_minutes",
            "price",
            "link",
            "tags",
            "ingredients",
        ]
        read_only_fields = ["id"]

    def _get_or_create_tags(self, tags_data, recipe):
        """Handling getting or crreating tags """
        auth_user = self.context["request"].user
        for tag in tags_data:
            tag_obj, _ = Tag.objects.get_or_create(user=auth_user, **tag)
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients_data, recipe):
        """Handling getting or crreating tags """
        auth_user = self.context["request"].user
        for i in ingredients_data:
            ing_obj, _ = Ingredient.objects.get_or_create(user=auth_user, **i)
            recipe.ingredients.add(ing_obj)

    def create(self, validated_data):
        tags_data = validated_data.pop("tags", [])
        ingredients_data = validated_data.pop("ingredients", [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags_data, recipe)
        self._get_or_create_ingredients(ingredients_data, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update recipe"""
        tags_data = validated_data.pop("tags", None)
        ingredients_data = validated_data.pop("ingredients", None)
        if tags_data is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags_data, instance)

        if ingredients_data is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients_data, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """
    Serializer for the Recipe detail view
    """

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description", "image"]


class RecipeImageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Recipe image
    """

    class Meta:
        model = Recipe
        fields = ["id", "image"]
        read_only_fields = ["id"]
        extra_kwargs = {"image": {"required": True}}
