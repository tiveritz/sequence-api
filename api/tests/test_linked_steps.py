import pytest

from django.urls import reverse
from rest_framework import status

from api.base.choices import StepChoices
from api.models import LinkedStep


@pytest.mark.django_db
def test_create_linked_step(client, make_step):
    super = make_step()
    step = make_step()

    kwargs = {'uuid': super.uuid}
    url = reverse('api:step-link', kwargs=kwargs)

    payload = {'sub': step.uuid}
    response = client.post(url, payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['super'] == str(super.uuid)
    assert response.data['sub'] == str(step.uuid)
    assert response.data['pos'] == 0


@pytest.mark.django_db
def test_create_linked_step_auto_pos(client, step, make_linked_steps):
    linked_step = make_linked_steps(super=step, sub=1)[0]

    kwargs = {'uuid': step.uuid}
    url = reverse('api:step-link', kwargs=kwargs)

    payload = {'sub': linked_step.sub.uuid}
    response = client.post(url, payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['super'] == str(step.uuid)
    assert response.data['sub'] == str(linked_step.sub.uuid)
    assert response.data['pos'] == 1


@pytest.mark.django_db
def test_delete_linked_step(client, step, make_linked_steps):
    linked_step = make_linked_steps(super=step, sub=1)[0]

    kwargs = {'uuid': step.uuid}
    url = reverse('api:linked-step-delete', kwargs=kwargs)

    payload = {'sub': linked_step.sub.uuid}
    response = client.delete(url, payload)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    with pytest.raises(LinkedStep.DoesNotExist):
        LinkedStep.objects.get(uuid=linked_step.uuid)


@pytest.mark.parametrize('delete_index',
                         [(0),
                          (1),
                          (2)])
@pytest.mark.django_db
def test_delete_linked_step_updates_order(client, delete_index, step,
                                          make_linked_steps):
    linked_steps = make_linked_steps(super=step, sub=3)

    kwargs = {'uuid': step.uuid}
    url = reverse('api:linked-step-delete', kwargs=kwargs)

    payload = {'sub': linked_steps[delete_index].sub.uuid}
    client.delete(url, payload)

    stored_linked_steps = LinkedStep.objects.filter(super=step).order_by('pos')

    assert len(stored_linked_steps) == 2
    assert stored_linked_steps[0].pos == 0
    assert stored_linked_steps[1].pos == 1


@pytest.mark.django_db
def test_delete_last_linked_step_updates_super_step_type(client, step,
                                                         make_linked_steps):
    linked_steps = make_linked_steps(super=step, sub=2)

    kwargs = {'uuid': step.uuid}
    url = reverse('api:linked-step-delete', kwargs=kwargs)

    payload = {'sub': linked_steps[0].sub.uuid}
    client.delete(url, payload)

    step.refresh_from_db()
    assert step.type == StepChoices.SUPER

    payload = {'sub': linked_steps[1].sub.uuid}
    client.delete(url, payload)

    step.refresh_from_db()
    assert step.type == StepChoices.STEP


@pytest.mark.parametrize('order, expected',
                         [((0, 2), (1, 2, 0)),
                          ((0, 1), (1, 0, 2)),
                          ((1, 2), (0, 2, 1)),
                          ((2, 0), (2, 0, 1)),
                          ((2, 1), (0, 2, 1)),
                          ((1, 0), (1, 0, 2))])
@pytest.mark.django_db
def test_rearrange_linked_steps(client, order, expected, step,
                                make_linked_steps):
    linked_steps = make_linked_steps(super=step, sub=3)

    kwargs = {'uuid': step.uuid}
    url = reverse('api:linked-step-order', kwargs=kwargs)

    payload = {'from_index': order[0], 'to_index': order[1]}
    response = client.post(url, payload)

    assert response.status_code == status.HTTP_200_OK

    stored_linked_steps = LinkedStep.objects.filter(super=step).order_by('pos')

    assert stored_linked_steps[0] == linked_steps[expected[0]]
    assert stored_linked_steps[1] == linked_steps[expected[1]]
    assert stored_linked_steps[2] == linked_steps[expected[2]]


@pytest.mark.django_db
def test_link_step_updates_super_step_type(client, make_step,
                                           make_linked_steps):
    step = make_step(type=StepChoices.STEP)
    linked_step = make_linked_steps(super=step, sub=1)[0]

    kwargs = {'uuid': step.uuid}
    url = reverse('api:step-link', kwargs=kwargs)

    payload = {'sub': linked_step.sub.uuid}
    client.post(url, payload)

    step.refresh_from_db()
    assert step.type == StepChoices.SUPER
