import warnings
from functools import wraps

__func_map = dict()
__attr_map = dict()


def register_config(function=None, attrs=None, **d_kwargs):
    def _decorator(f):
        @wraps(f)
        def _wrapper(*args, **kwargs):
            all_kwargs = {**d_kwargs, **kwargs}
            return f(*args, **all_kwargs)

        if _wrapper.__name__ in __func_map:
            warnings.warn(f'Overwriting registration for "{_wrapper.__name__}".', RuntimeWarning)

        __func_map[_wrapper.__name__] = _wrapper
        __attr_map[_wrapper.__name__] = attrs or dict()
        return _wrapper

    if function:
        return _decorator(function)
    return _decorator


def config_key(d):
    return d.split(":")[0]


def get_config_attrs(name):
    key = config_key(name)
    if key not in __attr_map:
        raise ValueError(f'Config "{key}" not found.')

    return __attr_map[key]


def get_config_fn(name):
    key = config_key(name)
    if key not in __func_map:
        raise ValueError(f'Config "{key}" not found.')

    return __func_map[key]


def get_config(config_name, **kwargs):
    config_fn = get_config_fn(config_name)
    config = config_fn(config_name=config_name, **{k: v for k, v in kwargs.items() if v is not None})
    return config


def list_configs() -> list[str]:
    return [cname for cname in __func_map.keys() if not get_config_attrs(cname).get("unlisted", False)]
