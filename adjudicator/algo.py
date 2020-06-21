num_dep = 0


class States:
    UNRESOLVED = 'unresolved'
    GUESSING = 'guessing'
    RESOLVED = 'resolved'


class Resolutions:
    FAILS = 'fails'
    SUCCEEDS = 'succeeds'


def adjudicate():
    pass


def backup_rule():
    pass


def resolve(order):
    dep_list = []

    # If order is already resolved, just return the resolution
    if order.state == States.RESOLVED:
        return order.state

    # Order is in guess state. Add the order to the dependencies list, if it
    # isn't there yet and return the guess.
    if order.state == Resolutions.GUESSING:
        if order not in dep_list:
            dep_list.append(order)
        return order.state

    # Remember how big the dependency list is before we enter recursion.
    old_num_dep = len(dep_list)

    order.resolution = Resolutions.FAILS
    order.state = States.GUESSING

    # adjudicate order
    first_result = adjudicate(order)

    if num_dep == old_num_dep:
        # No orders were added to the dependency list. This means that the
        # result is not dependent on a guess.

        # Set the resolution (ignoring initial guess). The order may already have
        # the state RESOLVED, due to the backup rule acting outside the cycle.
        order.state = States.RESOLVED
        order.resolution = first_result
        return order.resolution

    if dep_list[old_num_dep] != order:
        # The order is dependent on a guess, but not our own guess, because it
        # would be the first dependency added. Add to dependency list, update
        # result, but state remains guessing.
        dep_list.append(order)
        order.resolution = first_result
        return order.resolution

    # Result is dependent on our own guess. Set all the orders in the
    # dependency list to UNRESOLVED and reset dependency list.
    for dependency in dep_list:
        dependency.state = States.UNRESOLVED

    # Do the other guess
    order.resolution = Resolutions.SUCCEEDS
    order.state = States.GUESSING

    # adjudicate with the other guess
    second_result = adjudicate(order)

    if first_result == second_result:
        # Although there is a cycle, there is only one resolution. Clean up
        # dependency list first.
        for dependency in dep_list:
            dependency.state = States.UNRESOLVED
        order.resolution = first_result
        order.state = States.RESOLVED

    # There are two or no resolutions for the cycle. Pass dependencies to the
    # backup rule. These are dependencies within the range [old_num_dup:]. The
    # backup rule should clean up the clean up the dependency list (setting len
    # dep_list to old_num_dep). Any order in the dependency list that is not
    # set to RESOLVED should be set to UNRESOLVED.
    backup_rule(old_num_dep)

    # Backup rule may not have resolved all orders in the cycle. For instance,
    # the Szykman rule, will not resolve the orders of the moves attacking the
    # convoys. To deal with this we start all over again.
