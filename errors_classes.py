class SocialNetworkError(Exception):    # TODO кинул сюда, потому что не придумал, куда еще. Открыто для дискуссии
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'{self.message}'
