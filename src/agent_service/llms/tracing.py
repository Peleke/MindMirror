def trace_function(func=None, *, name=None, tags=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            # Optionally use name and tags here for tracing
            return f(*args, **kwargs)

        wrapper._trace_name = name
        wrapper._trace_tags = tags
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator
