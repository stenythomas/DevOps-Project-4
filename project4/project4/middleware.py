class SecurityHeadersMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        response["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        response["X-Content-Type-Options"] = "nosniff"

        response["X-Frame-Options"] = "DENY"

        response["Referrer-Policy"] = (
            "strict-origin-when-cross-origin"
        )

        if "text/html" in response.get("Content-Type", ""):

            response["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, max-age=0"
            )

            response["Pragma"] = "no-cache"
            response["Expires"] = "0"

            response["Content-Security-Policy"] = (
                "default-src 'self'; "

                "script-src 'self' 'unsafe-eval' "
                "https://widget.kommunicate.io "
                "https://cdn.kommunicate.io "
                "'sha256-2qNzNpI3gwHqqEBSeKFFc4Nd1Gz75vybmFp1jNGOvmA='; "

                "style-src 'self' 'unsafe-inline' "
                "https://fonts.googleapis.com "
                "https://cdn.jsdelivr.net "
                "https://widget.kommunicate.io "
                "https://cdn.kommunicate.io; "

                "font-src 'self' data: "
                "https://fonts.gstatic.com "
                "https://cdn.jsdelivr.net "
                "https://widget.kommunicate.io "
                "https://cdn.kommunicate.io; "

                "img-src 'self' data: blob: "
                "https://*.kommunicate.io; "

                "connect-src 'self' "
                "https://cdn.jsdelivr.net "
                "https://*.kommunicate.io "
                "wss://*.kommunicate.io; "

                "frame-src 'self' "
                "https://*.kommunicate.io; "

                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "
            )

        return response
