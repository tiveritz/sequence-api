import pytest

from django.urls import reverse
from rest_framework import status

from api.models import SuperStep


@pytest.mark.django_db
def test_create_superstep(client, make_step):
    super = make_step()
    step = make_step()

    kwargs = {'uuid': super.uuid}
    url = reverse('api:step-add', kwargs=kwargs)

    payload = {'sub': step.uuid}
    response = client.post(url, payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['super'] == str(super.uuid)
    assert response.data['sub'] == str(step.uuid)
    assert response.data['pos'] == 0


@pytest.mark.django_db
def test_create_superstep_auto_pos(client, step, make_supersteps):
    superstep = make_supersteps(super=step, sub=1)[0]

    kwargs = {'uuid': step.uuid}
    url = reverse('api:step-add', kwargs=kwargs)

    payload = {'sub': superstep.sub.uuid}
    response = client.post(url, payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['super'] == str(step.uuid)
    assert response.data['sub'] == str(superstep.sub.uuid)
    assert response.data['pos'] == 1


@pytest.mark.django_db
def test_delete_superstep(client, step, make_supersteps):
    superstep = make_supersteps(super=step, sub=1)[0]

    kwargs = {'uuid': step.uuid}
    url = reverse('api:step-delete', kwargs=kwargs)

    payload = {'sub': superstep.sub.uuid}
    response = client.delete(url, payload)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    with pytest.raises(SuperStep.DoesNotExist):
        SuperStep.objects.get(uuid=superstep.uuid)


@pytest.mark.parametrize("delete_index",
                         [(0),
                          (1),
                          (2)])
@pytest.mark.django_db
def test_delete_superstep_updates_order(client, delete_index, step, make_supersteps):
    supersteps = make_supersteps(super=step, sub=3)

    kwargs = {'uuid': step.uuid}
    url = reverse('api:step-delete', kwargs=kwargs)

    payload = {'sub': supersteps[delete_index].sub.uuid}
    client.delete(url, payload)

    stored_supersteps = SuperStep.objects.filter(super=step).order_by('pos')

    assert len(stored_supersteps) == 2
    assert stored_supersteps[0].pos == 0
    assert stored_supersteps[1].pos == 1


@pytest.mark.parametrize("order, expected",
                         [((0, 2), (1, 2, 0)),
                          ((0, 1), (1, 0, 2)),
                          ((1, 2), (0, 2, 1)),
                          ((2, 0), (2, 0, 1)),
                          ((2, 1), (0, 2, 1)),
                          ((1, 0), (1, 0, 2))])
@pytest.mark.django_db
def test_rearrange_substeps(client, order, expected, step, make_supersteps):
    supersteps = make_supersteps(super=step, sub=3)

    kwargs = {'uuid': step.uuid}
    url = reverse('api:step-order', kwargs=kwargs)

    payload = {'from_index': order[0], 'to_index': order[1]}
    response = client.post(url, payload)

    assert response.status_code == status.HTTP_200_OK

    stored_supersteps = SuperStep.objects.filter(super=step).order_by('pos')

    assert stored_supersteps[0] == supersteps[expected[0]]
    assert stored_supersteps[1] == supersteps[expected[1]]
    assert stored_supersteps[2] == supersteps[expected[2]]
