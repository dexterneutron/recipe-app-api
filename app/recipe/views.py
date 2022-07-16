'''

Views for the recipe API

'''

from distutils import core
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action

from core.models import Recipe, Tag, Ingredient
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

        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        '''
        Create a new recipe
        '''
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        '''
        Upload an image to a recipe
        '''
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class BaseRecipeAttrViewset(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin):
    '''
    Base viewset for user owned recipe attributes
    '''

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        '''
        Return objects for the authenticated user
        '''
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        '''
        Create a new ingredient
        '''
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewset):
    '''View set for the Tag model'''

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

class IngredientViewSet(BaseRecipeAttrViewset):
    '''View set for the Ingredient model'''

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

