"""
Dislodged:
    - A unit can only be dislodged when it stays in its current space. This is
      the case when the unit did not receive a move order, or if the unit was
      ordered to move but failed. If so, the unit is dislodged if another unit
      has a move order attacking the unit and for which the move succeeds.

Convoy Order:
    - A fleet with a successful convoy order can be part of a convoy. A convoy
      order is successful when the fleet receiving the order is not dislodged.

Path
    - The path of a move order is successful when the origin and destination of
      the move order are adjacent, or when there is a chain of adjacent fleets
      from origin to destination each with a matching and successful convoy
      order.

Support
    - A support order is cut when another unit is ordered to move to the area
      of the supporting unit and the following conditions are satisfied:
        * The moving unit is of a different nationality
        * The destination of the supported unit is not the area of the unit
          attacking the support
        * The moving unit has a successful path
        * A support is also cut when it is dislodged.

Hold strength
    - The hold strength is defined for an area, rather than for an order.
    - The hold strength is 0 when the area is empty, or when it contains a unit
      that is ordered to move and for which the move succeeds.
    - It is 1 when the area contains a unit that is ordered to move and for
      which the move fails.
    - In all other cases, it is 1 plus the number of orders that successfully
      support the unit to hold.

Attack strength
    - If the path of the move order is not successful, then the attack strength
      is 0.
    - Otherwise, if the destination is empty, or in a case where there is no
      head-to-head battle and the unit at the destination has a move order for
      which the move is successful, then the attack strength is 1 plus the
      number of successful support orders.
    - If not and the unit at the destination is of the same nationality, then
      the attack strength is 0.
    - In all other cases, the attack strength is 1 plus the number of
      successful support orders of units that do not have the same nationality
      as the unit at the destination.

Defend strength
    - In cases where the unit is engaged in a head-to-head battle, the unit has
      to overcome the power of the move of the opposing unit instead of the
      hold strength of the area.
    - The defend strength of a unit with a move order is 1 plus the number of
      successful support orders.

Move
    - In case of a head-to-head battle, the move succeeds when the attack
      strength is larger then the defend strength of the opposing unit and
      larger than the prevent strength of any unit moving to the same area. If
      one of the opposing strengths is equal or greater, then the move fails.
    - If there is no head-to-head battle, the move succeeds when the attack
      strength is larger then the hold strength of the destination and larger
      than the prevent strength of any unit moving to the same area. If one of
      the opposing strengths is equal or greater, then the move fails.
"""
