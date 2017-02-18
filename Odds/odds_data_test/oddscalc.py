# Calculator of poker probabilities

# For now, it still needs several changes. I did not how to get cards from a
# shuffled deck that is missing  the cards in the table or in my hand, so cards
# are being randomly generated, allowing for repeated cards. I will look into
# this soon. Also, because of this, final probabilities are independent of
# number of opponents.  
from __future__ import print_function
import numpy as np
import random
import os
import sys
scriptpath = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, scriptpath+'/../')
sys.path.insert(0, scriptpath+'/../../')
import saveloadpkl
import hand
import bbr
from collections import namedtuple
try:
	from collections import Counter
except:
	import backport_Counter
from operator import attrgetter
import time
import scipy
from matplotlib import pylab as plt
import copy
import shutil
import itertools
import scipy.integrate
import scipy.interpolate

try:
	from multiprocessing import Process, Queue
	MP = True
except:
	print('Warning: multiprocessing module not found. This might make some calculations much longer.')
	MP = False

Card = namedtuple("Card", ["value", "kind"])

VALUES=13


best_hand =  [Card(12,3), Card(11,3), Card(10,3), Card(9,3), Card(8,3)]
max_score = hand.full_hand_best(best_hand)[1]

hand_names = ['High Card', 'Pair', 'Two Pair', 'Three of a Kind', 'Straight', 'Flush', 'Full House', 'Four of a Kind', 'Straight Flush']

hand_bounds = []
for ival in range(len(hand_names)):
	if ival>0:
		hand_bounds.append(ival*((VALUES)**5))

print(hand_bounds)

print('Max-ish high card:',  hand.full_hand_best([Card(12,3), Card(8,1), Card(6,2), Card(1,1), Card(7,2), Card(2,3), Card(10,0)])[1])
print('Min-ish Pair:',  hand.full_hand_best([Card(0,3), Card(0,1), Card(6,2), Card(1,1), Card(7,2), Card(2,3), Card(10,0)])[1])


def hand_to_ID_full(hand):
	hand = sorted(hand, key=attrgetter('value'))
	hsize = len(hand)
	handID= '1'+str(hsize).zfill(2)
	icard=0
	prev_suit = hand[-1].kind
	for card in hand:
		handID+=str(card.value).zfill(2)
		handID+=str(card.kind)
		icard+=1

	return int(handID)

def hand_to_ID_reduced(hand):
	hand = sorted(hand, key=attrgetter('value'))
	hsize = len(hand)
	handID= '1'+str(hsize).zfill(2)

	ref_val=hand[-1].value

	ssvals = []
	
	for icard in range(len(hand)):
		iicard=icard
		while iicard>=1:
			ssvals.append(int(hand[iicard].kind==hand[iicard-1].kind))
			iicard-=1

	sparam = 0
	for ival in range(len(ssvals)):
		sparam+=ssvals[ival]*(2**ival)
			

	icard=0
	prev_suit = hand[-1].kind
	for card in hand:
		handID+=str(card.value).zfill(2)
		prev_suit
		icard+=1
	
	handID+=str(sparam).zfill(3)
	if len(hand)>6:
		print('ID format not valid')
		sys.exit()

	return [-1*int(handID), ref_val]

def hand_to_ID_minimal(hand):
	hand = sorted(hand, key=attrgetter('value'))
	hsize = len(hand)
	handID= '2'+str(hsize).zfill(2)

	ref_val=hand[-1].value

	ssvals = []
	
	for icard in range(len(hand)):
		iicard=icard
		while iicard>=1:
			ssvals.append(int(hand[iicard].kind==hand[iicard-1].kind))
			iicard-=1

	sparam = 0
	for ival in range(len(ssvals)):
		sparam+=ssvals[ival]*(2**ival)
			

	icard=0
	prev_suit = hand[-1].kind
	for card in hand:
		handID+=str(ref_val-card.value).zfill(2)
		prev_suit
		icard+=1
	
	handID+=str(sparam).zfill(3)
	if len(hand)>6:
		print('ID format not valid')
		sys.exit()

	return [-1*int(handID), ref_val]


def ID_to_hand(ID_num, ref_val=12):
	all_cards = []
	red=False
	print(ID_num)
	if ID_num<0:
		ID_num*=-1
		red = True
	ID_num=str(ID_num)
	Ncards = ID_num[1:3]
	print(Ncards)
	Ncards=int(Ncards)
	if red:
		suit_array = np.zeros(Ncards)
		sparam = int(ID_num[len(ID_num)-3:])
		len_svals = 0
		for icard in range(Ncards):
			iicard=icard
			while iicard>=1:
				len_svals+=1
				iicard-=1
		
		suit_bool = np.zeros(len_svals)
		print(sparam)
		for isuit in range(len_svals):
			print(isuit, 2**(len_svals-isuit-1), sparam)
			if sparam>=2**(len_svals-isuit-1):
				suit_bool[len_svals-isuit-1]=1
				sparam-=2**(len_svals-isuit-1)
		iisuit=0
		news_flag=False
		print(suit_bool)
		for isuit in range(Ncards):
			iicard=isuit
			while iicard>=1:
				news_flag=True
				print(isuit, iicard, iisuit)
				if suit_bool[iisuit]==1:
					suit_array[isuit]=suit_array[iisuit]
					news_flag=False
					break

				iicard-=1
				iisuit+=1
				

			if news_flag:
				suit_array[isuit]=np.amax(suit_array)+1

	if ID_num[0]=='1' and not red:
		for icard in range(Ncards):
			stc = 3+3*icard
			all_cards.append(Card(int(ID_num[stc:stc+2]), int(ID_num[stc+2:stc+3])))
	elif ID_num[0]=='1':
		values = np.zeros(Ncards)
		for icard in range(Ncards):
			stc = 3+2*icard
			values[icard]= int(ID_num[stc:stc+2])
	elif ID_num[0]=='2' and red:
		values = np.zeros(Ncards)
		for icard in range(Ncards):
			stc = 3+2*icard
			values[icard]= ref_value-int(ID_num[stc:stc+2])
	else:
		print('Hand ID not recognised.')
		sys.exit()

	if red:
		for icard in range(Ncards):
			all_cards.append(Card(int(values[icard]), int(suit_array[icard])))

	return all_cards
		

def load_dist(hand_cards, rtype='blind'):
	if rtype=='blind':
		fIDname = str(searchID[ihnd][0])+'_'+str(searchID[ihnd][1])
		searchID =  hand_to_ID_reduced(hand_cards)
		redone_hand = ID_to_hand(searchID[0])
		IDarray = np.load(scriptpath+'/blinds/blindIDs.npy')
		allarray = np.load(scriptpath+'/blinds/blindData'+fIDname+'.npy')
		Darray = allarray[0][:-1]
		bins= allarray[1]
		IDopp_array = np.load(scriptpath+'/blinds/blind_oppIDs.npy')
		opparray = np.load(scriptpath+'/blinds/blind_oppData'+fIDname+'.npy')
		Dopparray = opparray[0][:-1]
		oppbins= opparray[1]
		bins = np.load(scriptpath+'/blinds/bins.npy')
		own_bins_arr = (bins[1:] + bins[:-1])/2.
		"""iID=0
		for own_dist in Darray:
			plt.plot(own_bins_arr, own_dist, label=IDarray[iID])
			iID+=1
			if iID>2:
				break
		iID=0
		for opp_dist in Dopparray:
			plt.plot(own_bins_arr,opp_dist,marker='^', label=IDopp_array[iID])
			iID+=1
			if iID>2:
				break
		plt.legend(loc='best')
		plt.show()
		"""
		IDinds = np.where((IDarray == searchID).all(axis=-1))[0]
		IDoppinds = np.where((IDopp_array == searchID).all(axis=-1))[0]

	if len(IDinds)>1:
		print('More than one matching data array found for the hand requested.')
		sys.exit()
	elif len(IDinds)==0:
		print('No matching data found for the hand requested.')
		sys.exit()
	else:
		print(IDinds)
		print(IDarray[IDinds[0]],searchID)
		return np.asarray(Darray), bins, np.asarray(Dopparray), oppbins

def pl_integrand(xbins, dist, bins, ibin):
	#dfunc = scipy.interpolate.interp1d(bins,dist, kind='nearest')
	#between and xbin[ibin]  xbin[ibin+1] lie all the values that could be the same as
	#tother.. should strictly choose largest res.
	#xbins_mid = (xbins[1:] + xbins[:-1])/2.
	bins_mid = (bins[1:] + bins[:-1])/2.
	#print(xbins[ibin], xbins[ibin+1])
	#cond1 = bins_mid>xbins[ibin]
	#cond2 = bins_mid<xbins[ibin+1]
	#print(cond1*cond2)
	#dist_half = 0.5*dist[cond1*cond2]
	dist_trunc = dist[bins_mid<xbins[ibin]]
	#dist_trunc = np.append(dist_trunc, dist_half, axis=0)
	#print(dist_trunc)
	bin_trunc = bins_mid[bins_mid<xbins[ibin]]
	return np.trapz(dist_trunc, bin_trunc)

def pl_short(own_bins, own_dist, opp_cumsum):
	bins_diff = (own_bins[1:] - own_bins[:-1])
	bins_mid = (own_bins[1:] + own_bins[:-1])/2.
	#opp_cumsum_trunc = opp_cumsum[bins[:-1]<xbin]
	#own_cumsum_trunc = own_cumsum[own_bins[:-1]>xbin]
	#own_cumsum_trunc -= own_cumsum_trunc[0]
	#print(xbin, opp_cumsum_trunc[-1],own_cumsum_trunc[-1])

	pw = opp_cumsum*own_dist*bins_diff

	print(pw, type(pw))
	print(np.sum(own_dist*bins_diff))
	print(np.sum(opp_cumsum))
	return np.sum(bins_diff*opp_cumsum*own_dist*bins_diff)


def pl_integrand_losing(xbins, dist, bins, ibin):
	#dfunc = scipy.interpolate.interp1d(bins,dist, kind='nearest')
	#between and xbin[ibin]  xbin[ibin+1] lie all the values that could be the same as
	#tother.. should strictly choose largest res.
	#xbins_mid = (xbins[1:] + xbins[:-1])/2.
	bins_mid = (bins[1:] + bins[:-1])/2.
	#print(xbins[ibin], xbins[ibin+1])
	cond1 = bins_mid>xbins[ibin]
	cond2 = bins_mid<xbins[ibin+1]
	#print(cond1*cond2)
	dist_half = 0.5*dist[cond1*cond2]
	dist_trunc = dist[bins_mid>xbins[ibin+1]]
	dist_trunc = np.append(dist_trunc, dist_half, axis=0)
	#print(dist_trunc)
	bin_trunc = bins_mid[bins_mid>xbins[ibin]]
	return np.trapz(dist_trunc, bin_trunc)

	

def odds_winning(own_dist, own_bins, opp_dist, opp_bins):
	#first divide own_dist into hand types
	#then divide by local minima 
	#integrate between local minima to get probability
	#if probability is above threshold (1e-2??) then continue
	#integrate opp_dist to find prob opp > local maxima between

	own_bins_arr = (own_bins[1:] + own_bins[:-1])/2.
	opp_bins_arr = (opp_bins[1:] + opp_bins[:-1])/2.
	#plt.plot(own_bins_arr, own_dist)
	#plt.plot(opp_bins_arr, opp_dist)
	#plt.show()

	opp_cumsum=np.cumsum(opp_dist, gamma=0.1)
	#own_dist_func = scipy.interpolate.interp1d(own_bins_arr, own_dist,kind='nearest') 
	
	"""print('Integrand...')
	#integrand = np.asarray([own_dist[ib]*pl_short(own_bins[ib], opp_dist, opp_bins, ib) for ib in range(len(own_dist))])	
	print('Out..')
	#integrand2 = np.asarray([own_dist[ib]*pl_integrand_losing(own_bins, opp_dist, opp_bins, ib) for ib in range(len(own_dist))])
	#plt.plot(own_bins_arr, integrand)
	#plt.plot(own_bins_arr, integrand2)
	#plt.show()"""
	#prob_winning =scipy.integrate.quad(pl_short, own_bins[0], own_bins[-1], args=(own_cumsum, own_bins, opp_cumsum, opp_bins))# np.trapz(integrand, own_bins_arr)

	prob_winning=  pl_short(opp_bins, own_dist, opp_cumsum)

	#prob_losing =  np.trapz(integrand2, own_bins_arr)
	#print('Prob losing: ', prob_losing)

	winning_prob = prob_winning #1.-prob_losing	

	return winning_prob

def hand_probs(own_dist, own_bins):
	own_bins_arr = (own_bins[1:] + own_bins[:-1])/2.
	hdivs = []
	for bound in hand_bounds:
		hdivs.append(np.searchsorted(own_bins, bound, side="left"))
	own_segs = np.split(own_dist, hdivs)
	own_segbins = np.split(own_bins_arr, hdivs)
	#opp_bins_arr = (opp_bins[1:] + opp_bins[:-1])/2.
	#print('Integrated prior: ', np.trapz(opp_dist, opp_bins_arr))
	print('Integrated: ', np.trapz(own_dist, own_bins_arr))
	#plt.plot(own_bins_arr, own_dist)
	#plt.plot(opp_bins_arr, opp_dist)
	#plt.show()
	chances = np.zeros(len(own_segs))
	for iseg in range(len(own_segs)):
		#plt.plot(own_segbins[iseg],own_segs[iseg])
		chances[iseg] = np.trapz(own_segs[iseg], own_segbins[iseg])

	#plt.show()
	return chances, hand_names


def hms(seconds):
	m, s = divmod(seconds, 60)
	h, m = divmod(m, 60)
	return (h, m, s)


def dist(table, table_tot, cards, cards_tot, accuracy=10000, ret=2, del_cards=[]):
	new_deck = []
	new_table = []
	new_cards = []
	hand_tot = []

	deck = hand.poker_deck()
	for card in cards:
		deck.remove(card)
	for card in table:
		deck.remove(card)
	for card in del_cards:
		deck.remove(card)

	if len(deck)>50:
		print('Temp quit.')
		print(del_cards)
		print(len(deck))
		sys.exit()
	
	#print('Player hand: ', cards)
	#print('Table hand: ', table)
	#print('Delete: ', del_cards)

	point_distr= np.zeros(accuracy)

	table_togo = table_tot - len(table)
	cards_togo = cards_tot - len(cards)
	
	for irun in range(accuracy):
		new_deck = copy.copy(deck)
		new_table = list(table)
		new_cards = list(cards)
		random.shuffle(new_deck)
		for i in range(table_togo):
			if new_deck[0] in del_cards:
				print('Error')
				sys.exit()
			new_table.append(new_deck[0])
			new_deck.remove(new_deck[0])
		for i in range(cards_togo):
			if new_deck[0] in del_cards:
				print('Error')
				sys.exit()
			new_cards.append(new_deck[0])
			new_deck.remove(new_deck[0])


		hand_tot =list(new_table)+list(new_cards)
		point_distr[irun] = hand.full_hand_best(hand_tot)[1]
	
	
	n, bins, patches = plt.hist(point_distr, bins=bbr.bayesian_blocks(point_distr),
		  alpha=0.2, normed=True)
	plt.show()
	if ret==2:
		distr = np.zeros((2,len(n)+1))
		distr[0][:-1] = n
		distr[1] = bins
	
		return distr
	else:
		return n, bins

"""
def exact_calc
Can be used and return for reasonable time on the flop for your own hand
or for other peoples hands on the river 

"""

def exact_calc(table, own, cards_tot, score_range=None, nbins=None, mtype='own'):

	deck = hand.poker_deck()
	for card in list(table)+list(own):
		deck.remove(card)
	
	if mtype=='own':
		given_hand=list(table)+list(own)
		togo = cards_tot - len(given_hand)

		poss_left = list(itertools.combinations(deck, togo))
		point_distr = np.zeros(len(poss_left))
		ihand=0
		for hval in poss_left:
			point_distr[ihand] = hand.full_hand_best(list(given_hand)+list(hval))[1]
			ihand+=1
	if mtype=='other':
		given_hand = list(table)
		togo = cards_tot - len(table)

		poss_left = list(itertools.combinations(deck, togo))
		point_distr = np.zeros(len(poss_left))
		ihand=0
		for hval in poss_left:
			point_distr[ihand] = hand.full_hand_best(list(given_hand)+list(hval))[1]
			ihand+=1


	
	
	if nbins!=None:
		n, bins, patches = plt.hist(point_distr, bins=nbins, histtype='stepfilled',
		  alpha=0.2, range=score_range, normed=True)
	
		return n, bins
	else:
		return point_distr


def data_fetcher_general(hands, tables, IDarray, IDfname, Datafname, acc=10000, del_cards=[]):
	best_hand =  [Card(12,3), Card(11,3), Card(10,3), Card(9,3), Card(8,3)]
	max_score = hand.full_hand_best(best_hand)[1]

	if len(del_cards)==0:
		hand_set=hands
		del_cards = [list([]) for _ in xrange(len(hands))]
	if len(hands)==0:
		hand_set=del_cards
		hands = [list([]) for _ in xrange(len(del_cards))]
		#print(hands, tables)

	ihand = 0
	start_time = time.time()
	if not (os.path.exists(IDfname) and os.path.exists(Datafname)):
		ident_array = np.empty((0, 2), int)
	else:
		ident_array = np.load(IDfname)
	print(len(hands))
	print(ident_array)
	print(IDarray)
	for ihnd in range(len(hand_set)):
		if not any(np.equal(IDarray[ihnd], ident_array).all(1)):
			Dt_prev=time.time()
			distr_array, bin_array = dist(tables[ihnd], 5, hands[ihnd], 2,accuracy=acc, ret=1, del_cards= del_cards[ihnd])
			if not os.path.exists('bins.npy'):
				np.save('bins', bin_array)
			
			#own_bins_arr = (bin_array[1:] + bin_array[:-1])/2.
			#plt.plot(own_bins_arr,distr_array)
			#plt.plot(own_bins_arr,data_array[-1])
			Dtitle = Datafname.split('.')[0]+str(IDarray[ihnd][0])+'_'+str(IDarray[ihnd][1])
			data_array = np.save(Dtitle, np.array([distr_array]))
			ident_array = np.append(ident_array,np.array([IDarray[ihnd]]), axis=0)
			#plt.plot(own_bins_arr,data_array[-1], marker='^', color='b')
			#plt.plot(own_bins_arr,data_array[-2], marker='^', color='g')
			#plt.show()
			print('Hand {0}: {1} complete.'.format(ihand, hand_set[ihnd]))
			if ihand%10==0:
				shutil.copyfile(Dtitle, Datafname+'.backup')
				shutil.copyfile(IDfname, IDfname+'.backup')
				Dt = time.time()-start_time
				t = hms(Dt)
				print('Time elapsed: {0} hrs, {1} mins, {2} secs'.format(int(t[0]), int(t[1]), int(t[2])))
				print('Completed: {0}/{1}'.format(ihand, len(hands)))
				t_pred = (Dt-Dt_prev)*(len(hands)-ihand)
				t_pred = hms(t_pred)
				print('Time remaining: {0} hrs, {1} mins, {2} secs'.format(int(t_pred[0]), int(t_pred[1]), int(t_pred[2])))
		else:
			print('Data for {0} already stored...'.format(IDarray[ihnd]))
			ihand+=1

def blinds():
	best_hand =  [Card(12,3), Card(11,3), Card(10,3), Card(9,3), Card(8,3)]
	
	max_score = hand.full_hand_best(best_hand)[1]
	score_range = (0, max_score)

	hands = []
	tables=[]
	IDs = []
	IDs_check = []
	RVs_check = []
	deck = hand.poker_deck()
	for card in deck:
		new_deck = copy.copy(deck)
		new_deck.remove(card)
		for card1 in new_deck:
			hval = [card, card1]
			ID_arr= hand_to_ID_reduced(hval)
			ID_check = ID_arr[0]
			#RV_check = ID_arr[1]
			if not ID_check in IDs_check:
				IDs_check.append(ID_check)
				#RVs_check.append(RV_check)
				IDs.append(np.asarray(ID_arr))
				hands.append(hval)
				tables.append([])
				print('in', hval)
			print(hval)
			
	IDs = np.asarray(IDs)

	print(IDs, type(IDs))

	print('Number of hands to analyse: {0}'.format(len(hands)))
	data_fetcher_general(hands, tables, IDs, 'blindIDs.npy', 'blindData.npy', acc=10000, del_cards=[])
	"""ihand = 0
	Dt_prev=0
	start_time = time.time()
	for title in hand_dict:
		if not os.path.exists(title+'.npy'):
			distr_array = dist([], 5, hand_dict[title], 2, score_range=(0,max_score))
			np.save(title, distr_array)
		ihand+=1
		Dt = time.time()-start_time
		print('Time elapsed: {0}'.format(Dt))
		print('Completed: {0}/{1}'.format(ihand, len(hand_dict)))
		t_pred = (Dt-Dt_prev)*(len(hand_dict)-ihand)
		t_pred = hms(t_pred)
		print('Time remaining: {0} hrs, {1} mins, {2} secs'.format(int(t_pred[0]), int(t_pred[1]), int(t_pred[2])))
		Dt_prev=Dt"""

def blinds_opp():
	best_hand =  [Card(12,3), Card(11,3), Card(10,3), Card(9,3), Card(8,3)]
	
	max_score = hand.full_hand_best(best_hand)[1]
	score_range = (0, max_score)

	hands = []
	tables=[]
	IDs = []
	IDs_check = []
	RVs_check = []
	deck = hand.poker_deck()
	for card in deck:
		new_deck = copy.copy(deck)
		new_deck.remove(card)
		for card1 in new_deck:
			hval = [card, card1]
			ID_arr= hand_to_ID_reduced(hval)
			ID_check = ID_arr[0]
			#RV_check = ID_arr[1]
			if not ID_check in IDs_check:
				IDs_check.append(ID_check)
				#RVs_check.append(RV_check)
				IDs.append(np.asarray(ID_arr))
				hands.append(hval)
				tables.append([])
				print('in', hval)
			print(hval)
			
	IDs = np.asarray(IDs)

	opp_hands = []
	print('Number of hands to analyse: {0}'.format(len(hands)))
	data_fetcher_general(opp_hands, tables, IDs, 'blind_oppIDs.npy', 'blind_oppData.npy', acc=10000, del_cards=hands)

def blind_priors(accuracy = int(2e6)):
	best_hand =  [Card(12,3), Card(11,3), Card(10,3), Card(9,3), Card(8,3)]
	
	max_score = hand.full_hand_best(best_hand)[1]
	score_range = (0, max_score)

	title = 'prior'
	if not os.path.exists(title+'.npy'):
		deck = hand.poker_deck()
		point_distr= np.zeros(accuracy)
	
		for irun in range(accuracy):
			new_deck = copy.copy(deck)
		
			random.shuffle(new_deck)
			hand_tot = new_deck[0:7]

			point_distr[irun] = hand.full_hand_best(hand_tot)[1]

			if irun%int(accuracy/100)==0:
				print('Blind prior: {0}/{1} complete.'.format(irun, accuracy))
	
		if score_range==None:
			n, bins, patches = plt.hist(point_distr, bins=100, histtype='stepfilled',
			  alpha=0.2, normed=True)
		else:
			n, bins, patches = plt.hist(point_distr, bins=10000, histtype='stepfilled',
			  alpha=0.2, range=score_range, normed=True)
	

		"""distr = np.zeros((2,len(n)+1))
		distr[0][:-1] = n
		distr[1] = bins"""
		np.save(title+'Data', n)
		np.save(title+'Bins', bins)
	

		
if __name__=="__main__":
	best_hand =  [Card(12,3), Card(11,3), Card(10,3), Card(9,3), Card(8,3)]
	max_score = hand.full_hand_best(best_hand)[1]
	
	score_range = (0, max_score)
	table = [Card(3,2), Card(6,1), Card(10,3), Card(4,1), Card(8,3)]
	my_cards = [Card(0,0), Card(0,1)]
	dorig =scriptpath
	blind_run=True
	blind_prior=False
	flop_run1=False

	"""own_dist, bin_array = dist([], 5, my_cards, 2,accuracy=1000, score_range=(0,max_score), nbins=360, ret=1, del_cards= [])
	own_bins_arr = (bin_array[1:] + bin_array[:-1])/2.
	plt.plot(own_bins_arr, own_dist)
	plt.show()
	sys.exit()"""
	"""start=time.time()
	own_dist, own_bins, opp_dist, opp_bins = load_dist(my_cards, rtype='blind')
	res = hand_probs(own_dist, own_bins)
	print('TIME:', time.time()-start)
	for ires in range(len(res[0])):
		print(res[1][ires], '...', res[0][ires])
	#sys.exit()
	start=time.time()
	own_dist, own_bins, opp_dist, opp_bins = load_dist(my_cards, rtype='blind')
	#opp_dist = np.load(scriptpath+'/blinds/priorData.npy')
	#opp_bins = np.load(scriptpath+'/blinds/priorBins.npy')
	chance = odds_winning(own_dist, own_bins, opp_dist, opp_bins)
	print('TIME:', time.time()-start)
	print('Probability of winning: ', chance)
	sys.exit()"""
	
	"""start=time.time()

	out=exact_calc(table,my_cards, 7, score_range=score_range, nbins=45, mtype='other')

	print('TIME:', time.time()-start)
	sys.exit()"""
	
	
	if blind_run:
		os.chdir(dorig)
		if not os.path.exists('blinds'):
			os.makedirs('blinds')
		os.chdir('blinds')
		blinds_opp()
		#blinds()

	if blind_prior:
		os.chdir(dorig)
		if not os.path.exists('blinds'):
			os.makedirs('blinds')
		os.chdir('blinds')

		blind_priors()

	if flop_run1:
		os.chdir(dorig)
		if not os.path.exists('flops_prior'):
			os.makedirs('flops_prior')
		os.chdir('flops_prior')

		flops_others()
		


	
	
