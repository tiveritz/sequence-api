def parse_environment_boolean(variable):
    match variable:
        case 'True':
            return True
        case 'False':
            return False
        case _:
            raise AttributeError(f'Environment variable {variable} does not '
                                 'equal to either "True" or "False"')
