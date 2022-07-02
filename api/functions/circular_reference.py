from ..models import LinkedStep


def get_sub_step_tree(super):
    sub_steps = LinkedStep.objects.filter(super=super)
    sub_step_tree = []

    # Add self
    sub_step_tree.append(super)

    # Recursively add sub_steps
    for sub_step in sub_steps:
        sub_step_tree = get_sub_step_tree(sub_step.sub)
        if sub_step_tree:
            sub_step_tree.append(sub_step)
    return sub_step_tree


def get_super_step_tree(sub):
    super_steps = LinkedStep.objects.filter(sub=sub)
    super_step_tree = []

    # Add self
    super_step_tree.append(sub)

    # Recursively add super_steps
    for super_step in super_steps:
        super_step_tree = get_super_step_tree(super_step.super)
        if super_step_tree:
            super_step_tree.append(super_step)
    return super_step_tree


def has_circular_reference(step, check):
    sub_steps = get_sub_step_tree(step)
    super_steps = get_super_step_tree(step)

    if check in sub_steps:
        return True
    if check in super_steps:
        return True
    return False
