from slinn.http_json_response import HttpJSONResponse


class HttpJSONAPIResponse(HttpJSONResponse):

    """
    HttpJSONResponse-based with header `Access-Control-Allow-Origin: *`
    """
    
    def __init__(self, **payload: dict) -> None:
        super().__init__(**payload)
        default_data = [('Server', 'Slinn'), ('Content-Type', self.content_type), ('Access-Control-Allow-Origin', '*')]
        self.data = default_data + self.data if self.data is not None else default_data
