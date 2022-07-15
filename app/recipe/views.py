'''

Views for the recipe API

'''

from distutils import core
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from core.models import Recipe, Tag
from recipe import serializers

class RecipeViewSet(viewsets.ModelViewSet):
    '''
    ViewSet for the Recipe model
    '''

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()

    def get_queryset(self):
        '''
        Return the recipes for the authenticated user
        '''
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        '''
        Return appropriate serializer class
        '''

        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        '''
        Create a new recipe
        '''
        serializer.save(user=self.request.user)

class TagViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
     ):
    '''View set for the Tag model'''

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        '''
        Return the tags for the authenticated user
        '''
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        '''
        Create a new tag
        '''
        serializer.save(user=self.request.user)