class Request:

    def __init__(self, data: bytes):
        print("\nRECEIVED: ", data)
        lines = [d.strip() for d in data.decode().split("\n") if d.strip()]

        self.method, self.path, self.http_version = lines.pop(0).split(" ")
        self.path = self.path.lstrip('/')
        self.info = {k: v for k, v in (line.split(': ') for line in lines)}

    def __repr__(self) -> str:
        return "<BrowserRequest {method} {path} {http_version}>".format(method=self.method, path=self.path,
                                                                        http_version=self.http_version)
