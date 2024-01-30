
def format_dictionary_test_id(param):
    if isinstance(param, dict):
        args = {k: v for k, v in param.items()}
        return repr(args)