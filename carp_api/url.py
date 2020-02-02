class Url:
    """Helper class to build urls at the same time avoiding double // and
    similar.
    """
    def __init__(self, parts=None):
        self.url = []

        if not parts:
            return

        for part in parts:
            self.add(part)

    def add(self, part):
        part = str(part).strip('/')

        if not part:
            return

        self.url.append(part)

    def as_full_url(self, trailing_slash=False, host=None):
        host = str(host).strip('/') if host else ''

        if not self.url:
            return host + '/'

        return host + '/' + '/'.join(self.url) + (
            '/' if trailing_slash else '')
