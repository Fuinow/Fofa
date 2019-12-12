import requests
import time

def get_same_str(text1, text2, min_len=10, max_len=500):
        pos_list = []
        dp = [([0] * (len(text2)+1)) for i in range(len(text1)+1)]
        _len = index = 0

        for i in range(1, len(text1)+1):
            for j in range(1, len(text2)+1):
                if i == 0 or j == 0:  # 在边界上，自行+1
                        dp[i][j] = 0
                if text1[i-1] == text2[j-1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1         
                    if dp[i][j] > _len:  
                        _len = dp[i][j]
                        index = i - _len
                else:
                    dp[i][j] = 0
            if _len > min_len and _len < max_len:
                pos_list.append([index, _len])
            _len = min_len

        # for dp_line in dp:
        #     print(dp_line)
        result = []
        pos_list.append([-2,0])
        len_list = []
        last_pos = pos_list[0]
        for pos in pos_list:
            if pos[0] == last_pos[0]:
                len_list.append(pos[1])
            else:
                if len_list:
                    same_str = text1[last_pos[0]:last_pos[0] + max(len_list)]
                    for _str in same_str.split('>'):
                        _str = _str.strip()
                        if _str not in result and len(_str) >= min_len:
                            result.append(_str)
                last_pos[0] = pos[0]
                len_list = [pos[1]]

        return result

s1 = requests.get("https://zabbix.infatek.se/", verify=False).text
s2 = requests.get("http://18.206.17.51/").text
print(len(s1))
print(len(s2))
start_time = time.time()
res = get_same_str(s1, s2, min_len=10, max_len=500)
print(res)
print("Use time: "+ str(time.time()-start_time))
print(len(res))