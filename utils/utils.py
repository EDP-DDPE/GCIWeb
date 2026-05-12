def sanitize_postgres(value):
    if value == '':
        return None
    return value