import graphene
from graphene_django import DjangoObjectType

from product.models import Category, Product, ProductImage, ProductVariant


class CategoryType(DjangoObjectType):
    children = graphene.List(lambda: CategoryType)

    class Meta:
        model = Category
        fields = '__all__'

    @staticmethod
    def resolve_children(parent, info):
        return parent.children.all()


class ProductImageType(DjangoObjectType):
    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductVariantType(DjangoObjectType):
    images = graphene.List(ProductImageType)

    class Meta:
        model = ProductVariant
        fields = '__all__'

    @staticmethod
    def resolve_images(parent, info):
        return parent.images.all()


class ProductType(DjangoObjectType):
    variants = graphene.List(ProductVariantType)

    class Meta:
        model = Product
        fields = '__all__'

    @staticmethod
    def resolve_variants(parent, info):
        return parent.variants.all()
