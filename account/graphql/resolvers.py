from ..models import Page

def resolve_pages(root, info, **kwargs):
    if type(root).__name__ == 'User':
        return root.pages.all()
    else:
        return Page.objects.all()