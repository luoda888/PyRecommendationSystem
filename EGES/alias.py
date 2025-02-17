import numpy as np


def create_alias_table(area_ratio):
    """
    :param area_ratio: sum(area_ratio)=1
    :return: accept,alias
    """
    l = len(area_ratio)
    area_ratio = [prop * l for prop in area_ratio]
    accept, alias = [0] * l, [0] * l
    small, large = [], []

    for i, prob in enumerate(area_ratio):
        if prob < 1.0:
            small.append(i)
        else:
            large.append(i)

    while small and large:
        small_idx, large_idx = small.pop(), large.pop()
        accept[small_idx] = area_ratio[small_idx]
        alias[small_idx] = large_idx
        area_ratio[large_idx] = area_ratio[large_idx] - (1 - area_ratio[small_idx])
        if area_ratio[large_idx] < 1.0:
            small.append(large_idx)
        else:
            large.append(large_idx)

    while large:
        large_idx = large.pop()
        accept[large_idx] = 1
    while small:
        small_idx = small.pop()
        accept[small_idx] = 1

    return accept, alias


def alias_sample(accept, alias):
    """
    :param accept:
    :param alias:
    :return: sample index
    """
    N = len(accept)
    i = int(np.random.random() * N)
    r = np.random.random()
    if r < accept[i]:
        return i
    else:
        return alias[i]


if __name__ == "__main__":
    test_list = [0.05263157894736842, 0.05263157894736842, 0.05263157894736842, 0.05263157894736842,
                 0.05263157894736842,
                 0.10526315789473684, 0.10526315789473684, 0.05263157894736842, 0.05263157894736842,
                 0.05263157894736842,
                 0.05263157894736842, 0.05263157894736842, 0.05263157894736842, 0.05263157894736842,
                 0.05263157894736842,
                 0.05263157894736842, 0.05263157894736842]
    create_alias_table(test_list)
