from ..models import Step, SuperStep


def get_substep_tree(super):
    substeps = SuperStep.objects.filter(super = super)
    substep_tree = []

    # Add own id
    substep_tree.append(super)

    # Recursively add substeps
    for substep in substeps:
        step = Step.objects.get(uri_id = substep.uri_id)
        substep_tree = get_substep_tree(step)
        if substep_tree:
            substep_tree.append(substep)
    return substep_tree

def get_superstep_tree(sub):
    supersteps = SuperStep.objects.filter(sub = sub)
    superstep_tree = []

    # Add own id
    superstep_tree.append(sub)

    # Recursively add supersteps
    for superstep in supersteps:
        step = Step.objects.get(id = superstep.uri_id)
        superstep_tree = get_superstep_tree(step)
        if superstep_tree:
            superstep_tree.append(superstep)
    return superstep_tree

def has_circular_reference(step, check):
    substeps = get_substep_tree(step)
    supersteps = get_superstep_tree(step)

    if check in substeps:
        return True
    if check in supersteps:
        return True
    return False
