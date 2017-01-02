# Calculator of poker probabilities

# For now, it still needs several changes. I did not how to get cards from a
# shuffled deck that is missing  the cards in the table or in my hand, so cards
# are being randomly generated, allowing for repeated cards. I will look into
# this soon. Also, because of this, final probabilities are independent of
# number of opponents.  

import numpy as np
import random
import sys
sys.path.insert(0, './Odds/')
from hand import *
from collections import namedtuple, Counter
from operator import attrgetter
import time

table = [Card(3,2), Card(6,1), Card(10,3)]
my_cards = [Card(5,3), Card(9,1)]
#table = [Card(random.randint(2,14), random.randint(1,4)) for i in range(3)]
#my_cards = [Card(random.randint(2,14), random.randint(1,4)) for i in range(2)]

#For now, repeated cards are allowed, I have to fix that
def odds(table, my_cards, num_oponents):
    table_togo = 5 - len(table)
    if table_togo != 0:
        table = table + [Card(random.randint(2,14), random.randint(1,4)) for i in range(table_togo)]
    my_hand = sorted(table + my_cards, key=attrgetter('value'))
    my_score = hand_value(my_hand)

    his_score = 0
    for i in range(num_oponents):
        his_cards = [Card(random.randint(2,14), random.randint(1,4)) for i in range(2)]
        his_hand = sorted(table + his_cards, key=attrgetter('value'))
        temp_score = hand_value(his_hand)
        if temp_score > his_score:
            his_score = temp_score

        return my_score > his_score

def prob(table, my_cards, num_opponents, tol):
    sigma = 1.; win =0; tot = 0; samples = []
    while sigma > tol:
        if odds(table, my_cards, 1) == True:
            win+=1.
        tot+=1.
        p = win/tot
        samples.append(p)
        if tot%1000 == 0:
            sigma = np.std(np.asarray(samples))

    return p

print 'table cards', table
print 'my_cards', my_cards
start_time = time.time()
print 'Probability of winning =', prob(table,my_cards,1,1.e-2), 'after', time.time() - start_time, 'seconds.'
