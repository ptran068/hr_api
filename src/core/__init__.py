try:
    import ujson
    import requests
    # noinspection PyUnresolvedReferences
    requests.compat.json = ujson
    requests.models.complexjson = ujson
except ImportError:
    pass
