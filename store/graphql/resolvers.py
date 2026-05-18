from store.models import Brand, Branch


def _user_page_ids(user):
    return user.pages.values_list('id', flat=True)


def resolve_brands(_root, info, page_id=None, **_kwargs):
    user = info.context.user
    qs = Brand.objects.filter(page_id__in=_user_page_ids(user))
    if page_id is not None:
        qs = qs.filter(page_id=page_id)
    return qs.order_by('-created_at')


def resolve_brand(_root, info, id, **_kwargs):
    user = info.context.user
    return Brand.objects.filter(
        pk=id,
        page_id__in=_user_page_ids(user),
    ).first()


def resolve_branches(_root, info, page_id=None, **_kwargs):
    user = info.context.user
    qs = Branch.objects.filter(page_id__in=_user_page_ids(user))
    if page_id is not None:
        qs = qs.filter(page_id=page_id)
    return qs.order_by('-created_at')


def resolve_branch(_root, info, id, **_kwargs):
    user = info.context.user
    return Branch.objects.filter(
        pk=id,
        page_id__in=_user_page_ids(user),
    ).first()
