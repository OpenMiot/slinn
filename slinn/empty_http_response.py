from . import HttpResponse


class EmptyHttpResponse(HttpResponse):

    """
    HttpResponse-based class with status '204 No Content'
    """
    
    def __init__(self) -> None:
        super().__init__('', status='204 No Content')
