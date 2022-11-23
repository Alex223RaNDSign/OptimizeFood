import csv
import itertools
from scipy.optimize import linprog
import functools
import numpy
import json

mul = lambda x : lambda y : x*y

def simplex(target_nutrient, id_or_neg, ingredients, nutrients, matrix, filename, optimization_function, A_eq, b_eq, A_ub, b_ub, bounds):    

    solution = linprog(
        c = optimization_function,
        A_eq = A_eq,
        b_eq = b_eq,
        A_ub = A_ub,
        b_ub = b_ub,
        bounds = bounds,
        method = 'simplex'
    )
    
    solution.fun = id_or_neg(solution.fun)
    
    recipe = list(zip(ingredients, nested(solution.x, lambda z : round(z*100.0, 1), 1)))
    recipe = filter(lambda x : x[1] != 0.0, recipe)
    recipe = list(recipe)

    matrix = [numpy.float64(i) for i in matrix]
    matrix = numpy.float64(matrix)
    nutritional_label = numpy.dot(matrix, solution.x)
    nutritional_label = list(zip(nutrients, nutritional_label))
    
    file = open(filename, 'w')
    file.write("{}\n{} : {}\n".format(solution.message, target_nutrient, solution.fun))
    file.write("\nIngredients Used\n")
    file.write("\n".join(["{}".format(i[0]) for i in recipe]))
    file.write("\n\nRecipe\n")
    file.write("\n".join(["{} : {}".format(i[0], i[1]) for i in recipe]))
    
    file.write("\n\nNutritional Label\n")
    file.write("\n".join(["{} : {}".format(i[0], i[1]) for i in nutritional_label]))

    file.close()
    
def transpose(l):
    return map(list, itertools.zip_longest(*l, fillvalue=None))

def nested(x, op, depth):
    if depth == 0:
        try:
            return op(x)
        except TypeError:
            exit("operation is not callable")
    return [nested(i, op, depth - 1) for i in x]
    
def parse_document(filename):
    nutrients, limits, *matrix = csv.reader(open(filename, 'r'))
    del nutrients[0:3]; del limits[0:3]
    ingredients, lower, upper, *matrix = transpose(matrix)
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] == 'None':
                matrix[i][j] = 0.0
    lower = nested(lower, lambda x : float(x)/100.0, 1)
    upper = nested(upper, lambda x : float(x)/100.0, 1)
    matrix = nested(matrix, float, 2)
    bounds = list(zip(lower, upper))
    return (nutrients, limits, matrix, bounds, ingredients)

def make_function(matrix, id_or_neg, search_term):
    try:
        index_term = nutrients.index(search_term)
        try:
            optimization_function = matrix[index_term].copy()
        except IndexError:
            exit("unreachable")
        return (nested(optimization_function, id_or_neg, 1), search_term)
    except ValueError:
        make_function(matrix, id_or_neg)

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
    sign_mul = {
        'E' : mul(1),
        'L' : mul(1),
        'G' : mul(-1),
    }
    for (vector, limit) in zip(matrix, limits):
        x = iter(limit.upper().split())
        while True:
            try:
                code = str(next(x))
                value = float(next(x))
            except StopIteration:
                break
            try:
                constraints[place[code]]['vectors'].append(nested(vector, sign_mul[code], 1))
                constraints[place[code]]['scalars'].append(sign_mul[code](value))
            except KeyError:
                exit("unreachable")
    return constraints
    
def erase_ingredients(bounds, ingredients, filename):
    f = open(filename)
    neg_ingredients = [i for i in f.read().split('\n') if i.strip() != '']
    print(neg_ingredients)
    for ni in neg_ingredients:
        for (c, k) in enumerate(ingredients):
            if k == ni:
                bounds[c] = (0.0, 0.0)
    f.close()
    return None
    
def include_ingredients(nutrients, matrix, ingredients, bounds, filename):
    f = open(filename).read()
    j = json.loads(f)
    extra_ingredients = []
    for (i, v) in j.items():
        ingredients.append(i)
        bounds.append((0.0, float('Inf')))
        new_vector = [0.0]*len(nutrients)
        for (k, u) in v.items():
            try:
                h = nutrients.index(k)
                new_vector[h] = float(u)
            except KeyError:
                exit("Nutrient {} is not found".format(h))
            except ValueError:
                exit("Value {} could not be converted to float".format(u))
        print(new_vector)
        extra_ingredients.append(new_vector)
    extra_ingredients = list(transpose(extra_ingredients))
    for i in range(len(matrix)):
        matrix[i] = matrix[i] + extra_ingredients[i]
    
if __name__ == "__main__":
    
    sign = mul(1)
    
    nutrients, limits, matrix, bounds, ingredients = parse_document('food_matrix.csv')
    
    include_ingredients(nutrients, matrix, ingredients, bounds, 'include_ingredients.json')
    
    erase_ingredients(bounds, ingredients, 'delete_ingredients.txt')
    
    optimization_function, target_nutrient = make_function(matrix, sign, 'carbohydrate, by difference')

    constraints = get_constraints(matrix, limits)
    
    solution = simplex(target_nutrient, sign, ingredients, nutrients, matrix, 'recipe.txt', optimization_function, constraints['equalities']['vectors'], constraints['equalities']['scalars'], constraints['inequalities']['vectors'], constraints['inequalities']['scalars'], bounds)
 
    
    
