from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.db.models import QuerySet

from user.models import *


def paginate_query(request: WSGIRequest, query: QuerySet) -> QuerySet:
    if query.count() == 0:
        return query

    page = request.GET.get('page')
    page_size = request.GET.get('page_size')

    if page and page_size:
        page = int(page)
        page_size = int(page_size)
        p = Paginator(query, page_size).page(page)
        return query[p.start_index()-1:p.end_index()]
    return query


def apply_user_sorting(request: WSGIRequest, query: QuerySet,
                       model: type[Student, Teacher, Admin]) -> QuerySet:
    sort_by = request.GET.get('sort_by')
    if not sort_by:
        return query
    sort_order = request.GET.get('sort_order')
    order = '-' if sort_order and (sort_order == 'desc' or '-') else ''

    sort_by_field = f'{order}{model.__name__.lower()}__{sort_by}'
    return query.order_by(sort_by_field)
