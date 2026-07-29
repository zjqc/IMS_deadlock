from ims_deadlock.cases import c0_two_resource_deadlock, c1_cycle_insufficient_wip
from ims_deadlock.certificates import find_deadlock_certificate


def test_c0_two_resource_model_has_minimal_closed_blocking_kernel() -> None:
    model, state = c0_two_resource_deadlock()

    certificate = find_deadlock_certificate(model, state)

    assert certificate is not None
    assert certificate.kernel_jobs == frozenset({"j1", "j2"})
    assert certificate.kernel_resources == frozenset({"r1", "r2"})
    assert certificate.is_minimal is True
    assert certificate.assumptions == ("stable_state", "capacity_saturation")


def test_c1_static_cycle_without_saturation_is_not_deadlock_certificate() -> None:
    model, state = c1_cycle_insufficient_wip()

    certificate = find_deadlock_certificate(model, state)

    assert certificate is None

