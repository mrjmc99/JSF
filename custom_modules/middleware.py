from django.contrib.auth.models import Permission

class CustomPermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Call the view function and get the response
        response = self.get_response(request)

        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Get all active groups for the user
            active_groups = request.user.groups.filter(user=request.user)

            # Initialize an empty set to store combined permissions
            combined_permissions = set()

            # Loop through active groups and collect their permissions
            for group in active_groups:
                group_permissions = group.permissions.all()
                combined_permissions.update(group_permissions)

            # Update the user's permissions with the combined permissions
            request.user.user_permissions.set(combined_permissions)

        # Return the response
        return response
