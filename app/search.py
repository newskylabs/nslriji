
from flask import current_app


def add_to_index(index, model):
    """Add an entry to a full-text index."""

    # Do nothing when elasticsearch has not been configured
    if not current_app.elasticsearch:
        return

    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    print("DEBUG add_to_index():\n  - index: {}\n  - id: {}\n  - body: {}" \
          .format(index, model.id, payload))
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)


def remove_from_index(index, model):
    """Remove an entry from the index."""

    # Do nothing when elasticsearch has not been configured
    if not current_app.elasticsearch:
        return
    
    print("DEBUG remove_from_index():\n  - index: {}\n  - id: {}" \
          .format(index, model.id))
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index, query, page, per_page):
    """Execute a search query."""

    # Return an empty list when elasticsearch has not been configured
    if not current_app.elasticsearch:
        return [], 0

    # Query: searching the entire index:
    # - The 'multi_match' allowes to search across multiple fields. 
    # - By passing '*' as field name all fields are searched.
    # => Combining both, the entire index is searched.
    # Pagination: Returning page 'page' with 'per_page' results.
    body = {'query': {'multi_match': {'query': query, 'fields': ['*']}},
            'from': (page - 1) * per_page, 'size': per_page}

    # Search the given index
    print("DEBUG query_index():\n  - index: {}\n  - body: {}" \
          .format(index, body))
    search = current_app.elasticsearch.search(index=index, body=body)
    print("DEBUG search:", search)

    # Extract ids and number of results.
    # The ids have to be extracted from the list of hits.
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    number_of_results = search['hits']['total']

    return ids, number_of_results


## fin.
