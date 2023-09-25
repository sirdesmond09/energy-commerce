
class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-XSS-Protection'] = '1; mode=block'

        response['X-Frame-Options'] = 'DENY'  # You can also use 'SAMEORIGIN' if needed

        response['X-Content-Type-Options'] = 'nosniff'
        response['Permissions-Policy'] = "geolocation 'none';midi 'none';notifications 'none';push 'none';sync-xhr 'none';microphone 'none';camera 'none';magnetometer 'none';gyroscope 'none';speaker 'self';vibrate 'none';fullscreen 'self';payment 'none';"

    
        return response