def get_username(request):
    name = request.user.username
    return {
        'name': name
    }
