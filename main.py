import csv
import itertools
from scipy.optimize import linprog

def scale(factor, x):
    match type(x):
        case list():
            return [scale(factor, i) for i in x]
        case _ :
            return scale(factor, x)
            
            
def nested_mutate(operand, operator):
    return [nested_mutate(i, operator) for i in operand] if isinstance(operand, list) else operator(operand) if callable(operator) else operand
a = 12
b = '12'
c = ['21', '12']
d = [['2', '0'], ['23']]



a = nested_mutate(a, float)
b = nested_mutate(b, float)
c = nested_mutate(c, float)
d = nested_mutate(d, 3)

print(a, b, c, d)
exit()
def safe_iter(x):
    return iter(x) if isinstance(x, list) else iter([x])

def transpose(l):
    return map(list, itertools.zip_longest(*l, fillvalue=None))
    
def is_zero(vector):
    aux = iter(vector)
    try:
        if next(aux) != 0:
            return False
    except StopIteration:
        return True
    
def parse_document(filename):
    matrix = iter(csv.reader(open(filename, 'r')))
    nutrients = next(matrix)
    del nutrients[0:2]
    limits = next(matrix)
    del limits[0:2]
    matrix = transpose(matrix)
    
    first_limits = zip(mutate_all(next(matrix), float), mutate_all(next(matrix), float))
    ingredients = next(matrix)
    matrix = mutate_all(matrix, float)
    return (nutrients, limits, matrix, first_limits, ingredients)


mutate_all = lambda operand, operator: lambda answer: operator(operand)
  
o = mutate_all()
print(o(operand, operator))



def min_or_max():
    match input("minimize or maximize : "):
        case 'min' | 'minimize':
            return 1
        case 'max' | 'maximize':
            return -1
        case _ :
            min_or_max()

def make_function(matrix, sign):
    try:
        index = nutrients.index(input("Optimize : ").strip())
        try:
            optimization_function = matrix[index].copy()
        except IndexError:
            exit("unreachable")
        return nested_mutate(optimization_function, scale(sign))
    except ValueError:
        make_function(matrix, sign)


def get_constraints(matrix, limits):
    constraints = {
    'equalities' : {
        'vectors' : [],
        'scalars' : [],
        },
    'inequalities' : {
        'vectors' : [],
        'scalars' : [],
        },
    }
    place = {
        'E' : 'equalities',
        'L' : 'inequalities',
        'G' : 'inequalities',
    }
    matrix = iter(matrix)
    limits = iter(limits)
    while True:
        try:
            vector = next(matrix)
            limit = next(limits)
        except StopIteration:
            break
        x = iter(limit.upper().split())
        
        while True:
            try:
                code = str(next(x))
                value = float(next(x))
                
                    
            except StopIteration:
                break
            
    return constraints
    
    
if __name__ == "__main__":
    
    sign = min_or_max()
    del min_or_max

    nutrients, limits, matrix, first_limits, ingredients = parse_document('cure.csv')
    del parse_document
    
    optimization_function = make_function(matrix, sign)
    del make_function
    
    constraints = get_constraints(matrix, limits)
    del get_constraints
    
    solution = simplex(optimization_function, constraints['equalities']['vectors'], constraints['equalities']['scalars'], constraints['inequalities']['vectors'], constraints['inequalities']['scalars'], first_limits)
    
