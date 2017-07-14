# -*- coding: UTF-8 -*-
# Author: Tim Wu
# Author: Carl King


# 牌型枚举
class COMB_TYPE:
    PASS, SINGLE, PAIR, TRIPLE, TRIPLE_ONE, TRIPLE_TWO, FOURTH_TWO_ONES, FOURTH_TWO_PAIRS, STRIGHT, BOMB = range(10)


# 3-14 分别代表 3-10, J, Q, K, A
# 16, 18, 19 分别代表 2, little_joker, big_joker
# 将 2 与其他牌分开是为了方便计算顺子
# 定义 HAND_PASS 为过牌
little_joker, big_joker = 18, 19
HAND_PASS = {'type':COMB_TYPE.PASS, 'main': 0, 'component':[]}


# 根据当前手牌，获取此牌所有可能出的牌型
# 牌型数据结构为 {牌类型，主牌，包含的牌}
# 同种牌类型可以通过主牌比较大小
# 为方便比较大小, 将顺子按照不同长度分为不同牌型
def get_all_hands(pokers):
    if not pokers:
        return []

    # 过牌
    combs = [HAND_PASS]


    # 获取每个点数的数目
    dic = {}
    for poker in pokers:
        dic[poker] = pokers.count(poker)


    # 王炸
    if little_joker in pokers and big_joker in pokers:
        combs.append({'type':COMB_TYPE.BOMB, 'main': big_joker, 'component': [big_joker, little_joker]})


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
                    combs.append({'type':COMB_TYPE.TRIPLE_ONE, 'main':poker, 'component': [poker, poker, poker, poker2]})
                if ALLOW_THREE_TWO and dic[poker2] >= 2 and poker2 != poker:
                    # 三带二
                    combs.append({'type':COMB_TYPE.TRIPLE_TWO, 'main':poker, 'component': [poker, poker, poker, poker2, poker2]})

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
                        combs.append({'type':COMB_TYPE.FOURTH_TWO_ONES, 'main':poker, \
                            'component':[poker, poker, poker, poker, ones[i], ones[j]]})

                # 四带二对
                for i in range(len(pairs)):
                    combs.append({'type':COMB_TYPE.FOURTH_TWO_ONES, 'main':poker, \
                        'component': [poker, poker, poker, poker, pairs[i], pairs[i]]})
                    for j in range(i + 1, len(pairs)):
                        combs.append({'type':COMB_TYPE.FOURTH_TWO_PAIRS, 'main':poker, \
                            'component': [poker, poker, poker, poker, pairs[i], pairs[i], pairs[j], pairs[j]]})


    # 所有顺子组合
    # 以 COMB_TYPE.STRIGHT * len(straight) 标志顺子牌型, 不同长度的顺子是不同的牌型
    for straight in create_straight(list(set(pokers)), 5):
        combs.append({'type':COMB_TYPE.STRIGHT * len(straight), 'main': straight[0], 'component': straight})


    # 返回所有可能的出牌类型
    return combs



# 根据列表创建顺子
def create_straight(list_of_nums, min_length):

    a = sorted(list_of_nums)
    lens = len(a)
    for start in range(0, lens):
        for end in range(start, lens):
            if a[end] - a[start] != end - start:
                break
            elif end - start >= min_length - 1:
                yield list(range(a[start], a[end] + 1))



# comb1 先出，问后出的 comb2 是否能打过 comb1
# 1. 同种牌型比较 main 值, main 值大的胜
# 2. 炸弹大过其他牌型
# 3. 牌型不同, 后出为负
def can_beat(comb1, comb2):
    if not comb2 or comb2['type'] == COMB_TYPE.PASS:
        return False
    if not comb1 or comb1['type'] == COMB_TYPE.PASS:
        return True
    elif comb1['type'] == comb2['type']:
        return comb2['main'] > comb1['main']
    elif comb2['type'] == COMB_TYPE.BOMB:
        return True
    else:
        return False



# 给定 pokers，求打出手牌 hand 后的牌
# 用 component 字段标志打出的牌, 可以方便地统一处理
def make_hand(pokers, hand):
    poker_clone = pokers[:]
    for poker in hand['component']:
        poker_clone.remove(poker)
    return poker_clone



# 模拟每次出牌, my_pokers 为当前我的牌, enemy_pokers 为对手的牌
# last_hand 为上一手对手出的牌, cache 用于缓存牌局与胜负关系
def hand_out(my_pokers, enemy_pokers, last_hand = None, cache = {}):

    # 牌局终止的边界条件
    if not my_pokers:
        return True
    if not enemy_pokers:
        return False

    # 如果上一手为空, 则将上一手赋值为 HAND_PASS
    if last_hand is None:
        last_hand = HAND_PASS

    # 从缓存中读取数据
    key = str((my_pokers, enemy_pokers, last_hand['component']))
    if key in cache:
        return cache[key]

    # 模拟出牌过程, 深度优先搜索, 找到赢的分支则返回 True
    for current_hand in get_all_hands(my_pokers):
        # 转换出牌权有两种情况: 
        # 1. 当前手胜出, 则轮到对方选择出牌
        # 2. 当前手 PASS, 且对方之前没有 PASS, 则轮到对方出牌
        if can_beat(last_hand, current_hand) or \
        (last_hand['type'] != COMB_TYPE.PASS and current_hand['type'] == COMB_TYPE.PASS):
            if not hand_out(enemy_pokers, make_hand(my_pokers, current_hand), current_hand, cache):
                # print(True,' :', key)
                cache[key] = True
                return True

    # 遍历所有情况, 均无法赢, 则返回 False
    # print(False, ':', key)
    cache[key] = False
    return False


# todo:
# 1. 用出牌列表作为 last_hand 的值, 方便调用函数


if __name__ == '__main__':
    import time
    start = time.clock()

    # 残局1
    # 是否允许三带一
    ALLOW_THREE_ONE = True
    # 是否允许三带二
    ALLOW_THREE_TWO = False
    # 是否允许四带二
    ALLOW_FOUR_TWO = True

    lord = [19,18,11,11,9,9,9]
    # farmer = [3,3,3,3,4,5,6,7,10,10,14,14,14,14]
    farmer = [16, 16, 16, 14, 14, 14, 3, 4, 5, 6, 7, 8, 9, 10]
    result = hand_out(farmer, lord)


    # 残局2
    # # 是否允许三带一
    # ALLOW_THREE_ONE = False
    # # 是否允许三带二
    # ALLOW_THREE_TWO = False
    # # 是否允许四带二
    # ALLOW_FOUR_TWO = True

    # lord = [14,14,11,11]
    # farmer = [16,13,13,13,12,12,12,10,10,9,9,8,8]
    # result = hand_out(farmer, lord)

    elapsed = (time.clock() - start)

    print("Result:", result)
    print("Elapsed:", elapsed)
