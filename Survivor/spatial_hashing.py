from math import floor

"""
http://mauveweb.co.uk/posts/2011/05/introduction-to-spatial-hashes.html
"""
class spatial_hash():
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.cells = {}

    def add_rect(self, rect, obj):
        """Add an object obj with bounds r."""
        cells = self._cells_for_rect(rect)
        for c in cells:
            self._add(c, obj)

    def remove_rect(self, r, obj):
        """Remove an object obj which had bounds r."""
        cells = self._cells_for_rect(r)
        for c in cells:
            self._remove(c, obj)
        
    def reset(self):
        self.cells = {}

    def _add(self, cell_coord, o):
        """Add the object o to the cell at cell_coord."""
        try:
            self.cells.setdefault(cell_coord, set()).add(o)
        except KeyError:
            self.cells[cell_coord] = set((o,))

    def _cells_for_rect(self, rect):
        """Return a set of the cells into which r extends."""
        cells = set()
        cy = floor(rect[1] / self.cell_size)
        while (cy * self.cell_size) <= rect[3]:
            cx = floor(rect[0] / self.cell_size)
            while (cx * self.cell_size) <= rect[2]:
                cells.add((int(cx), int(cy)))
                cx += 1.0
            cy += 1.0
        return cells
    
    def potential_collisions(self, rect, obj):
        """Get a set of all objects that potentially intersect obj."""
        cells = self._cells_for_rect(rect)
        potentials = set()
        for c in cells:
            cell = self.cells.get(c, set())
            potentials.update(cell)
        potentials.discard(obj) # obj cannot intersect itself
        return potentials

    def _remove(self, cell_coord, o):
        """Remove the object o from the cell at cell_coord."""
        cell = self.cells[cell_coord]
        cell.remove(o)

        # Delete the cell from the hash if it is empty.
        if not cell:
            del(self.cells[cell_coord])
