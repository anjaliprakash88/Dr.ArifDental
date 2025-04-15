from django.shortcuts import redirect

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs that don't require authentication
        allowed_urls = [
            '/', '/about/', '/contact/', '/services/', '/blogs/', 
            '/blog-single/', '/doctors/', '/navigation/'
        ]

        allowed_urls += [
            '/reception/login/', '/superadmin/login/', 
            '/pharmacy/login/', '/doctor/login/'
        ]

        # Allow users to access login and public pages
        if request.path in allowed_urls:
            return self.get_response(request)

        # Redirect unauthenticated users trying to access restricted pages
        if not request.user.is_authenticated:
            if request.path.startswith('/reception/'):
                return redirect('/reception/login/')
            elif request.path.startswith('/superadmin/'):
                return redirect('/superadmin/login/')
            elif request.path.startswith('/pharmacy/'):
                return redirect('/pharmacy/login/')
            elif request.path.startswith('/doctor/'):
                return redirect('/doctor/login/')
            else:
                return redirect('/navigation/')  # Default redirection

        # Prevent caching for authenticated pages
        response = self.get_response(request)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
