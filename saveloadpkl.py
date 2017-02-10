try:
   import cPickle as pickle
except:
   import pickle

import os

def save_obj(obj, name, loc=None):
	if loc!=None:
		name = os.path.join(loc, name)
	with open(name + '.pkl', 'wb') as f:
		pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name, loc=None):
	if loc!=None:
		name = os.path.join(loc, name)
	with open(name + '.pkl', 'rb') as f:
		return pickle.load(f)
