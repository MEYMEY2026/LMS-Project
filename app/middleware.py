from django.http import HttpResponseForbidden

class AdminIPRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ពិនិត្យមើលថាតើអ្នកកំពុងព្យាយាមចូលទំព័រ Admin ឬអត់
        if request.path.startswith('/secret-admin/'):
            # ទាញយក IP របស់អ្នកប្រើ
            ip = request.META.get('REMOTE_ADDR')
            # អនុញ្ញាតតែ IP 127.0.0.1 (Localhost) ប៉ុណ្ណោះ
            if ip not in ['127.0.0.1', 'localhost']:
                return HttpResponseForbidden(
                    "<h1>403 Forbidden</h1><p>អ្នកមិនមានសិទ្ធិចូលទំព័រនេះពីទីតាំងនេះទេ។ សូមចូលពីកុំព្យូទ័រមេ។</p>"
                )
        
        response = self.get_response(request)
        return response