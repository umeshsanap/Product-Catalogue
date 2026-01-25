def user_context(request):
    """Add user session info to all templates."""
    return {
        'user_id': request.session.get('user_id'),
        'user_name': request.session.get('user_name', ''),
        'user_email': request.session.get('user_email', ''),
        'is_logged_in': 'user_id' in request.session
    }





