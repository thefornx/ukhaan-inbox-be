import graphene
from django.db import transaction
from graphql import GraphQLError

from core.graphql.decorators.login_required import login_required
from core.graphql.decorators.business_required import business_required
from store.graphql.types import BranchType
from store.models import Branch, OpeningHours


class OpeningHoursInput(graphene.InputObjectType):
    day_of_week = graphene.Int(required=True)
    open_time = graphene.Time()
    close_time = graphene.Time()
    is_closed = graphene.Boolean(default_value=False)


class BranchInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    address_text = graphene.String()
    latitude = graphene.Float()
    longitude = graphene.Float()
    phone = graphene.String()
    website = graphene.String()
    opening_hours = graphene.List(OpeningHoursInput)


def _sync_opening_hours(branch, hours):
    branch.opening_hours.all().delete()
    OpeningHours.objects.bulk_create([
        OpeningHours(branch=branch, **dict(h)) for h in hours
    ])


def _split_hours(input):
    data = dict(input)
    hours = data.pop('opening_hours', None)
    return data, hours


class CreateBranchMutation(graphene.Mutation):
    class Arguments:
        input = BranchInput(required=True)

    branch = graphene.Field(BranchType)

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, input):
        data, hours = _split_hours(input)
        with transaction.atomic():
            branch = Branch.objects.create(page=info.context.business, **data)
            if hours:
                _sync_opening_hours(branch, hours)
        return CreateBranchMutation(branch=branch)


class UpdateBranchMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = BranchInput(required=True)

    branch = graphene.Field(BranchType)

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, id, input):
        try:
            branch = Branch.objects.get(pk=id, page=info.context.business)
        except Branch.DoesNotExist:
            raise GraphQLError('Branch not found')

        data, hours = _split_hours(input)
        with transaction.atomic():
            for key, value in data.items():
                setattr(branch, key, value)
            branch.save()
            if hours is not None:
                _sync_opening_hours(branch, hours)

        return UpdateBranchMutation(branch=branch)


class DeleteBranchMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, id):
        deleted, _ = Branch.objects.filter(pk=id, page=info.context.business).delete()
        return DeleteBranchMutation(ok=deleted > 0)
