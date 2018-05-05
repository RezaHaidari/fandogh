def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class ClientInfo(object):
    def __init__(self, request):
        self.ip = get_client_ip(request)
        self.device_type, self.device_id = self.parse_device_id(request.META.get('HTTP_X_DEVICE_ID', None))
        self.user = request.user
        self.user_agent = request.META.get("HTTP_USER_AGENT", "").lower()

    def get_user_id(self):
        if self.is_anonymous():
            return None
        else:
            return self.user.id

    @property
    def is_bot(self):
        return 'bot' in self.user_agent

    def is_anonymous(self):
        return self.user.is_anonymous

    def parse_device_id(self, device_id):
        if device_id is None:
            return None, None
        try:
            if "|" not in device_id:
                return "ANDROID", device_id
            _type, _id = device_id.split("|")
            return _type, _id
        except ValueError:
            return None, device_id

    def __str__(self):
        return "IP:%s DEVICE-ID:%s user:%s" % (self.ip, self.device_id, self.user)

# curl localhost:8000/api/webapp/services -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InNvcm9vc2hAeWFob28uY29tIiwiZXhwIjoxNTI1NTExOTIyLCJ1c2VyX2lkIjoxLCJlbWFpbCI6InNvcm9vc2hAeWFob28uY29tIn0.5zFO-ELs9KudyLx_pFPOTVwY1NKqFJBcmWuHG07r9k8"

