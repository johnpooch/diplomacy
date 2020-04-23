# Basic checks - applies to all order types (except build).
A001 = ('A001', 'Cannot order a piece belonging to another nation.')

# Move checks - applies to move orders.
M001 = ('M001', 'Cannot move a piece belonging to another nation.')
M002 = ('M002', 'Cannot move to territory that the piece is already in.')
M003 = ('M003', 'Army cannot move to a non-adjacent territory without convoy.')
M004 = ('M004', 'Fleet cannot move to a non-adjacent territory.')
M005 = ('M005', 'Army cannot enter a sea territory')
M006 = ('M006', 'Fleet cannot enter an inland territory')
M007 = ('M007', 'Fleet cannot move from a coastal territory to another adjacent coastal territory if there is no shared coastline.')

# Convoy checks - applies to convoy orders.
C001 = ('C001', 'Cannot convoy a fleet.')
C002 = ('C002', 'Fleet can only convoy from a sea territory.')

# Support checks - applies to support orders.
S001 = ('S001', 'A piece cannot support itself.')
S002 = ('S002', 'A piece cannot support a territory which it cannot reach.')

# Retreat checks - applies to retreat orders.
R001 = ('R001', 'Piece cannot retreat to the territory from which it was attacked.')
R005 = ('R005', 'A piece cannot retreat to a territory which was contested on the previous turn.')

# Build checks - applies to all build orders.
B001 = ('B001', 'Cannot build in a territory that is already occupied.')
B002 = ('B002', 'Cannot build in a territory that does not have a supply center.')
B003 = ('B003', 'Cannot build in supply centers outside of national borders.')
B004 = ('B004', 'Cannot build in a supply center which is controlled by a foreign power.')
B005 = ('B005', 'Cannot build a fleet in an inland territory.')
B006 = ('B006', 'Must specify a coast when building a fleet in a territory with named coasts.')




