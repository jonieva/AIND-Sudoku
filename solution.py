
from utils import *


row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = [[(r+c) for (r,c) in zip(rows, cols)], [(r+c) for (r,c) in zip(rows, cols[::-1])]]

unitlist = row_units + column_units + square_units + diagonal_units


# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).
    """
    for unit in unitlist:
        # Get all the boxes that have 2 possible values
        possible_twins = [(box, values[box]) for box in unit if len(values[box]) == 2]
        # Double loop but only in half of the elements (there is no need to replace the elements twice for each twin)
        # This is why the inner loop begins with i+1
        for i in range(len(possible_twins)):
            for j in range(i+1, len(possible_twins)):
                if possible_twins[i][1] == possible_twins[j][1]:
                    # Twin found. Remove each one of the values from all the boxes in the unit (different from the
                    # twin boxes)
                    for cell in (cell for cell in unit if cell not in (possible_twins[i][0], possible_twins[j][0])):
                        for digit in possible_twins[i][1]:
                            values[cell] = values[cell].replace(digit, '')
    return values


def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    for k,v in values.items():
        if len(v) == 1:
            # Remove peers
            for peer in peers[k]:
                values[peer] = values[peer].replace(v, '')
    return values


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
    for unit in unitlist:
        for digit in '123456789':
            places_counter = [box for box in unit if digit in values[box]]
            if len(places_counter) == 1:
                # The digit is present in the unit just once
                values[places_counter[0]] = digit
    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Eliminate Strategy
        for k, v in values.items():
            if len(v) == 1:
                # Remove peers
                for peer in peers[k]:
                    values[peer] = values[peer].replace(v, '')

        # Only Choice Strategy
        for unit in unitlist:
            for digit in '123456789':
                places_counter = [box for box in unit if digit in values[box]]
                if len(places_counter) == 1:
                    # The digit is present in the unit
                    values[places_counter[0]] = digit

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    values = reduce_puzzle(values)

    # Sanity check
    if not values:
        return False

    # Variables to choose the most promising box
    min_length = 10
    min_box = None

    # Check if we have a solution already. Otherwise pick the optimal candidate
    solved_values = 0
    for box, choices in values.items():
        if len(choices) == 1:
            solved_values += 1
        elif len(choices) < min_length:
            # This is the most promising box so far
            min_length = len(choices)
            min_box = box

    if solved_values == 81:
        # Puzzle solved!
        return values

    # Pick one of the choices for the best candidate
    choices = values[min_box]
    for choice in choices:
        # Copy the solution
        new_puzzle = dict(values)
        new_puzzle[min_box] = choice
        # Search for a solution here
        sol = search(new_puzzle)
        if sol:
            # Success!
            return sol

    # We couldn't find a solution
    return False


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except Exception as ex:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

