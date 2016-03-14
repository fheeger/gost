import random as rand

def generate_feature():
    counter = 1

    x_orig = rand.randint(1,10000)/100
    y_orig = rand.randint(1,10000)/100
    z_orig = rand.randint(1,10000)/100
    
    Feature_Coords = []
    
    print('start')

    while counter < 24:
        next_pp = tuple(next_point(x_orig, y_orig, z_orig))
        counter += 1
        Feature_Coords.append(next_pp)
    return print(Feature_Coords)


def next_point(x_orig, y_orig, z_orig):
    Seed_x = rand.randint(1,2)
    Seed_y = rand.randint(1,2)
    Seed_z = rand.randint(1,2)

    if Seed_x == 1:
        x_next = x_orig - rand.randint(1,100)/100
    else:
        x_next = x_orig + rand.randint(1,100)/100

    if Seed_y == 1:
        y_next = y_orig - rand.randint(1,100)/100
    else:
        y_next = y_orig + rand.randint(1,100)/100

    if Seed_z == 1:
        z_next = z_orig - rand.randint(1,100)/100
    else:
        z_next = z_orig + rand.randint(1,100)/100
    counter = 1
    
    if counter > 5:
        for step in range(counter):
            z_next += 0.2
            y_next += 0.2
            x_next += 0.2
            counter += 1
            print('1')
            
    elif 5 < counter > 10:
        for step in range(counter):
            z_next += 0.2
            y_next -= 0.2
            x_next += 0.2
            counter += 1
            print('2')
            
    elif 10 < counter > 15:
        for step in range(counter):
            z_next += 0.2
            y_next -= 0.2
            x_next -= 0.2
            counter += 1
            print('3')
            
    elif 15 < counter > 30:
        for step in range(counter):
            z_next += 0.2
            y_next += 0.2
            x_next -= 0.2
            counter += 1
            print('4')
            
    feature_list = x_next, y_next, z_next

    return(x_next, y_next, z_next)
