# -*- coding: UTF-8 -*-
# Author: Tim Wu

# 是否允许三带一
ALLOW_THREE_ONE = True
# 是否允许三带二
ALLOW_THREE_TWO = False
# 是否允许四带二
ALLOW_FOUR_TWO = True

# 牌型枚举
class COMB_TYPE:
	PASS, SINGLE, PAIR, TRIPLE, TRIPLE_ONE, TRIPLE_TWO, FOURTH_TWO_ONES, FOURTH_TWO_PAIRS, STRIGHT, BOMB, KING_PAIR = range(11)

# 根据牌，获取此副牌所有可能的牌型
# 牌型数据结构为牌类型，主牌，副牌
def get_all_hands(pokers):
	if not pokers:
		return []

	combs = [{'type':COMB_TYPE.PASS}]
	dic = {}
	for poker in pokers:
		dic[poker] = dic.get(poker, 0) + 1

	for poker in dic:
		if dic[poker] >= 1:
			# 单张
			combs.append({'type':COMB_TYPE.SINGLE, 'main':poker})
		if dic[poker] >= 2:
			# 对子
			combs.append({'type':COMB_TYPE.PAIR, 'main':poker})
		if dic[poker] >= 3:
			# 三带零
			combs.append({'type':COMB_TYPE.TRIPLE, 'main':poker})
			for poker2 in dic:
				if ALLOW_THREE_ONE and dic[poker2] >= 1 and poker2 != poker:
					# 三带一
					combs.append({'type':COMB_TYPE.TRIPLE_ONE, 'main':poker, 'sub':poker2})
				if ALLOW_THREE_TWO and dic[poker2] >= 2 and poker2 != poker:
					# 三带二
					combs.append({'type':COMB_TYPE.TRIPLE_TWO, 'main':poker, 'sub':poker2})
						
		if dic[poker] == 4:
			# 炸弹
			combs.append({'type':COMB_TYPE.BOMB, 'main':poker})
			if ALLOW_FOUR_TWO:
				pairs = []
				ones = []
				for poker2 in dic:
					if dic[poker2] == 1:
						ones.append(poker2)
					elif dic[poker2] == 2:
						pairs.append(poker2)
				for i in xrange(len(ones)):
					for j in xrange(i + 1, len(ones)):
						combs.append({'type':COMB_TYPE.FOURTH_TWO_ONES, 'main':poker, 'sub1':ones[i], 'sub2':ones[j]})
				for i in xrange(len(pairs)):
					combs.append({'type':COMB_TYPE.FOURTH_TWO_ONES, 'main':poker, 'sub1':pairs[i], 'sub2':pairs[i]})
					for j in xrange(i + 1, len(pairs)):
						combs.append({'type':COMB_TYPE.FOURTH_TWO_PAIRS, 'main':poker, 'sub1':pairs[i], 'sub2':pairs[j]})

	if 16 in pokers and 17 in pokers:
		# 王炸
		combs.append({'type':COMB_TYPE.KING_PAIR})

	# 所有顺子组合
	distincted_sorted_pokers = sorted(list(set(pokers)))
	lastPoker = distincted_sorted_pokers[0]
	sequence_num = 1
	i = 1
	while i < len(distincted_sorted_pokers):
		# 只有3-A能连成顺子
		if distincted_sorted_pokers[i] <= 14 and distincted_sorted_pokers[i] - lastPoker == 1:
			sequence_num += 1
			if sequence_num >= 5:
				j = 0
				while sequence_num - j >= 5:
					# 顺子
					combs.append({'type':COMB_TYPE.STRIGHT, 'main':sequence_num - j, 'sub':distincted_sorted_pokers[i]})
					j += 1
		else:
			sequence_num = 1
		lastPoker = distincted_sorted_pokers[i]
		i += 1

	return combs

# comb1先出，问后出的comb2是否能打过comb1
def can_comb2_beat_comb1(comb1, comb2):
	if comb2['type'] == COMB_TYPE.PASS:
		return False

	if not comb1 or comb1['type'] == COMB_TYPE.PASS:
		return True

	if comb1['type'] == comb2['type']:
		if comb1['type'] == COMB_TYPE.STRIGHT:
			if comb1['main'] != comb2['main']:
				return False
			else:
				return comb2['sub'] > comb1['sub']
		else:
			if comb1['main'] == comb2['main']:
				return comb2['sub'] > comb1['sub']
			else:
				return comb2['main'] > comb1['main']
	elif comb2['type'] == COMB_TYPE.BOMB or comb2['type'] == COMB_TYPE.KING_PAIR:
		return comb2['type'] > comb1['type']

	return False

# 给定牌pokers，求打出手牌hand后的牌
def make_hand(pokers, hand):
	poker_clone = pokers[:]
	if hand['type'] == COMB_TYPE.SINGLE:
		poker_clone.remove(hand['main'])
	elif hand['type'] == COMB_TYPE.PAIR:
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['main'])
	elif hand['type'] == COMB_TYPE.TRIPLE:
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['main'])
	elif hand['type'] == COMB_TYPE.TRIPLE_ONE:
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['sub'])
	elif hand['type'] == COMB_TYPE.TRIPLE_TWO:
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['sub'])
		poker_clone.remove(hand['sub'])
	elif hand['type'] == COMB_TYPE.FOURTH_TWO_ONES:
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['sub1'])
		poker_clone.remove(hand['sub2'])
	elif hand['type'] == COMB_TYPE.FOURTH_TWO_PAIRS:
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['sub1'])
		poker_clone.remove(hand['sub1'])
		poker_clone.remove(hand['sub2'])
		poker_clone.remove(hand['sub2'])
	elif hand['type'] == COMB_TYPE.STRIGHT:
		for i in xrange(hand['sub'], hand['sub'] - hand['main'], -1):
			poker_clone.remove(i)
	elif hand['type'] == COMB_TYPE.BOMB:
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['main'])
		poker_clone.remove(hand['main'])
	elif hand['type'] == COMB_TYPE.KING_PAIR:
		poker_clone.remove(16)
		poker_clone.remove(17)
	return poker_clone

# 模拟每次出牌，me_pokers为当前我的牌，enemy_pokers为对手的牌
# last_hand为上一手的手牌
def hand_out(me_pokers, enemy_pokers, last_hand, cache):
	if not me_pokers:
		return True
	if not enemy_pokers:
		return False
	if (str(me_pokers),str(enemy_pokers),str(last_hand)) in cache:
		return cache[(str(me_pokers),str(enemy_pokers),str(last_hand))]
	all_hands = get_all_hands(me_pokers)
	for hand in all_hands:
		if (last_hand and can_comb2_beat_comb1(last_hand, hand)) or (not last_hand and hand['type'] != COMB_TYPE.PASS):
			if not hand_out(enemy_pokers, make_hand(me_pokers, hand), hand, cache):
				cache[(str(me_pokers),str(enemy_pokers),str(last_hand))] = True
				return True
		elif last_hand and hand['type'] == COMB_TYPE.PASS:
			if not hand_out(enemy_pokers, me_pokers, None, cache):
				cache[(str(me_pokers),str(enemy_pokers),str(last_hand))] = True
				return True
	cache[(str(me_pokers),str(enemy_pokers),str(last_hand))] = False
	return False

# 残局1 
lord = [17,16,11,11,9,9,9]
farmer = [3,3,3,3,4,5,6,7,10,10,14,14,14,14]
print hand_out(farmer, lord, None, {})

# 残局2
# lord = [14,14,11,11]
# farmer = [16,13,13,13,12,12,12,10,10,9,9,8,8]
# print hand_out(farmer, lord, None, {})
