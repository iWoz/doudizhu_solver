# -*- coding: UTF-8 -*-
# Author: Tim Wu
# Author: Carl King


# 牌型枚举
class COMB_TYPE:
    PASS, SINGLE, PAIR, TRIPLE, TRIPLE_ONE, TRIPLE_TWO, FOURTH_TWO_ONES, FOURTH_TWO_PAIRS, STRIGHT, BOMB, KING_PAIR = range(11)


# 分别使用 3-17 代表 3-10, J, Q, K, A, 2, little_joker, big_joker
cards = list(range(3,18))
*_, little_joker, big_joker = cards



# 根据牌，获取此副牌所有可能的牌型
# 牌型数据结构为牌类型，主牌，副牌, 包含的牌
def get_all_hands(pokers):
    if not pokers:
        return []

    combs = [{'type':COMB_TYPE.PASS}]


    dic = {}
    for poker in pokers:
        dic[poker] = pokers.count(poker)


    # 王炸
    if little_joker in pokers and big_joker in pokers:
        combs.append({'type':COMB_TYPE.KING_PAIR, 'component': [little_joker, big_joker]})


    # 非顺子, 非王炸
    for poker in dic:
        if dic[poker] >= 1:
            # 单张
            combs.append({'type':COMB_TYPE.SINGLE, 'main':poker, 'component':[poker]})

        if dic[poker] >= 2:
            # 对子
            combs.append({'type':COMB_TYPE.PAIR, 'main':poker, 'component':[poker, poker]})

        if dic[poker] >= 3:
            # 三带零
            combs.append({'type':COMB_TYPE.TRIPLE, 'main':poker, 'component':[poker, poker, poker]})
            for poker2 in dic:
                if ALLOW_THREE_ONE and dic[poker2] >= 1 and poker2 != poker:
                    # 三带一
                    combs.append({'type':COMB_TYPE.TRIPLE_ONE, 'main':poker, 'sub':poker2, 'component': [poker, poker, poker, poker2]})
                if ALLOW_THREE_TWO and dic[poker2] >= 2 and poker2 != poker:
                    # 三带二
                    combs.append({'type':COMB_TYPE.TRIPLE_TWO, 'main':poker, 'sub':poker2, 'component': [poker, poker, poker, poker2, poker2]})

        if dic[poker] == 4:
            # 炸弹
            combs.append({'type':COMB_TYPE.BOMB, 'main':poker, 'component': [poker, poker, poker, poker]})
            if ALLOW_FOUR_TWO:
                pairs = []
                ones = []
                for poker2 in dic:
                    if dic[poker2] == 1:
                        ones.append(poker2)
                    elif dic[poker2] == 2:
                        pairs.append(poker2)
                # 四带二单
                for i in range(len(ones)):
                    for j in range(i + 1, len(ones)):
                        combs.append({'type':COMB_TYPE.FOURTH_TWO_ONES, 'main':poker, 'sub1':ones[i], 'sub2':ones[j], 'component':[poker, poker, poker, poker, ones[i], ones[j]]})
                # 四带二对
                for i in range(len(pairs)):
                    combs.append({'type':COMB_TYPE.FOURTH_TWO_ONES, 'main':poker, 'sub1':pairs[i], 'sub2':pairs[i], 'component': [poker, poker, poker, poker, pairs[i], pairs[i]]})
                    for j in range(i + 1, len(pairs)):
                        combs.append({'type':COMB_TYPE.FOURTH_TWO_PAIRS, 'main':poker, 'sub1':pairs[i], 'sub2':pairs[j], 'component': [poker, poker, poker, poker, pairs[i], pairs[i], pairs[j], pairs[j]]})


    # 所有顺子组合
    sorted_set_of_pokers = sorted(list(set(pokers)))
    for straight in create_straight(sorted_set_of_pokers, 5):
        combs.append({'type':COMB_TYPE.STRIGHT, 'main':len(straight), 'sub': straight[-1], 'component': straight})


    # 返回所有可能的出牌类型
    return combs


# 根据有序列表创建顺子
def create_straight(sorted_list, min_length):

    a = sorted_list
    lens = len(a)
    for start in range(0, lens):
        for end in range(start, lens):
            if a[end] - a[start] != end - start:
                break
            elif end - start >= min_length - 1:
                yield list(range(a[start], a[end] + 1))



# comb1 先出，问后出的 comb2 是否能打过 comb1
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
    else:
        return False



# 给定 pokers，求打出手牌 hand 后的牌
def make_hand(pokers, hand):
    poker_clone = pokers[:]
    for poker in hand['component']:
        poker_clone.remove(poker)
    return poker_clone



# 模拟每次出牌, my_pokers 为当前我的牌, enemy_pokers 为对手的牌
# last_hand 为上一手的手牌
def hand_out(my_pokers, enemy_pokers, last_hand, cache):
    if not my_pokers:
        return True
    if not enemy_pokers:
        return False
    situation = ','.join([str(my_pokers),str(enemy_pokers), str(last_hand)])
    if situation in cache:
        return cache[situation]
    all_hands = get_all_hands(my_pokers)
    for hand in all_hands:
        if (last_hand and can_comb2_beat_comb1(last_hand, hand)) or (not last_hand and hand['type'] != COMB_TYPE.PASS):
            if not hand_out(enemy_pokers, make_hand(my_pokers, hand), hand, cache):
                cache[situation] = True
                return True
        elif last_hand and hand['type'] == COMB_TYPE.PASS:
            if not hand_out(enemy_pokers, my_pokers, None, cache):
                cache[situation] = True
                return True
    cache[situation] = False
    return False



if __name__ == '__main__':
    import time
    start = time.clock()

    # 残局1
    # 是否允许三带一
    ALLOW_THREE_ONE = True
    # 是否允许三带二
    ALLOW_THREE_TWO = True
    # 是否允许四带二
    ALLOW_FOUR_TWO = True

    lord = [17,16,11,11,9,9,9]
    # farmer = [3,3,3,3,4,5,6,7,10,10,14,14,14,14]
    farmer = [15, 15, 15, 14, 14, 14]
    result = hand_out(farmer, lord, None, {})


    # 残局2
    # # 是否允许三带一
    # ALLOW_THREE_ONE = False
    # # 是否允许三带二
    # ALLOW_THREE_TWO = False
    # # 是否允许四带二
    # ALLOW_FOUR_TWO = True

    # lord = [14,14,11,11]
    # farmer = [16,13,13,13,12,12,12,10,10,9,9,8,8]
    # result = hand_out(farmer, lord, None, {})

    elapsed = (time.clock() - start)

    print("Result:", result)
    print("Elapsed:", elapsed)
