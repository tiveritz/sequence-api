from rest_framework.filters import SearchFilter, OrderingFilter


class SequenceSearchFilter(SearchFilter):
    # TODO: remove this workaround
    def get_search_fields(self, view, request):
        fields = super().get_search_fields(view, request)

        if 'title' in fields:
            return ['step__title']


class SequenceOrderingFilter(OrderingFilter):
    # TODO: remove this workaround

    fields = {
        "title": "step__title",
        "updated": "updated",
        "created": "created",
        "published": "published",
    }
    ordering_fields = fields.keys()

    def filter_queryset(self, request, queryset, view):
        order_fields = []
        ordering = self.get_ordering(request, queryset, view)
        if ordering:
            for field in ordering:
                prefix = field.replace(field.lstrip("-"), "")
                order_fields.append(prefix + self.fields[field.lstrip("-")])
        if order_fields:
            return queryset.order_by(*order_fields)

        return queryset
