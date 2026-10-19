def cost_per_serving(total_cost, servings):
    return total_cost / servings


def test_cost_per_serving():
    assert cost_per_serving(100, 4) == 25
