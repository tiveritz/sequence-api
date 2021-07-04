from ..models import Step, Super


def get_substep_tree(step):
    substeps = Super.objects.filter(super_id = step.id)
    substep_tree = []

    # Add own id
    substep_tree.append(step)

    # Recursively add substeps
    for substep in substeps:
        step = Step.objects.get(id = substep.step_id.id)
        substep_tree = get_substep_tree(step)
        if substep_tree:
            substep_tree.append(substep.step_id)
    return substep_tree

def get_superstep_tree(step):
    supersteps = Super.objects.filter(step_id = step.id)
    superstep_tree = []

    # Add own id
    superstep_tree.append(step)

    # Recursively add supersteps
    for superstep in supersteps:
        step = Step.objects.get(id = superstep.super_id.id)
        superstep_tree = get_superstep_tree(step)
        if superstep_tree:
            superstep_tree.append(superstep.step_id)
    return superstep_tree

def has_circular_reference(step, check):
    substeps = get_substep_tree(step)
    supersteps = get_superstep_tree(step)

    if check in substeps:
        return True
    if check in supersteps:
        return True
    return False
