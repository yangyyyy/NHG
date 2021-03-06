import json
from preprocess.my_rouge import Myrouge


def create_summaries(origin_data, max_sent_num=4):
    """
    origin_data: List[json str], content->title json文件数据
    max_sent_num: int, max number of sentence in summary

    return
    res_data: List[json str]
    """
    my_rouge = Myrouge()
    res_data = []
    for _, line in enumerate(origin_data):  # 对于每一条训练数据
        # 有可能有些数据找不到summary(title和content一个相同词都没有)
        tmp = json.loads(line)
        content = tmp['content']
        title = tmp['title']
        seqs = [seq.strip() for seq in content.split('\n') if len(seq) > 4]  # 至少一句话得有4个字母吧
        for i, seq in enumerate(seqs): # 消掉其中太多的空行
            words = seq.split()
            seqs[i] = ' '.join(words)
        summary_list = []
        index_set = set()
        pre_score = 0
        # initiate the first sentence in summary_list
        for i, seq in enumerate(seqs):
            cur = my_rouge.compute(seq, title)
            if cur > pre_score:
                pre_score = cur
                if not len(summary_list):
                    summary_list.append(i)
                else:
                    summary_list[0] = i
        if not len(summary_list):
            continue  # 一个相同词都没有, 那就下一轮开始循环
        index_set.add(summary_list[0])
        while len(summary_list) <= min(max_sent_num, len(seqs)):
            pre_summary = '\n'.join([seqs[i] for i in summary_list])
            tmp_i = -1
            for i, seq in enumerate(seqs):
                if i not in index_set:
                    cur = my_rouge.compute(pre_summary + '\n' + seq, title)
                    if cur > pre_score:
                        pre_score = cur
                        tmp_i = i
            if tmp_i == -1: break
            index_set.add(tmp_i)
            summary_list.append(tmp_i)
            summary_list.sort()

        summary = '\n'.join([seqs[i] for i in summary_list])
        res = json.dumps({'summary': summary, 'title': title}, ensure_ascii=False)
        res_data.append(res)

        if _ + 1 % 1000 == 0:
            print(_ + 1, "dealed")

    print(
        'the length of origin data(content->title): {}, the length of summary->title data: {}'.format(len(origin_data),
                                                                                                      len(res_data)))
    return res_data


def create(origin_file_path, max_summa_len=5, max_sent_len=60):
    """
    :param origin_file_path: 训练数据集(content->title)
    :param max_summa_len: 最多抽取多少句话成为摘要
    :param max_sent_len: 摘要中每句话的最大长度(设置为50，参考论文为<SumaRuNNer>)
    :return:
    """
    my_rouge = Myrouge()

    data = [] # (json{"summary":xxx, "title":title})
    # cnt = 0

    with open(origin_file_path, 'r', encoding='utf-8') as f:
        for _, line in enumerate(f.readlines()): # 对于每一条训练数据
            # 有可能有些数据找不到summary(title和content一个相同词都没有)
            tmp = json.loads(line)
            content = tmp['content'].strip()
            title = tmp['title'].strip()
            seqs = [seq.strip() for seq in content.split('\n') if len(seq) > 2] # 至少一句话得有3个字母吧
            for i, seq in enumerate(seqs):
                words = seq.strip().split()
                if len(words) > max_sent_len:
                    words = words[:max_sent_len] # 每句话不得超过最大词语限制长度
                seqs[i] = ' '.join(words)
            summary_list = []
            index_set = set()
            pre_score = 0
            # 初始化第一句
            for i, seq in enumerate(seqs):
                cur = my_rouge.compute(seq, title)
                if cur > pre_score:
                    pre_score = cur
                    if not len(summary_list):
                        summary_list.append(i)
                    else:
                        summary_list[0] = i
            if not len(summary_list):
                continue # 一个相同词都没有
            index_set.add(summary_list[0])
            while len(summary_list) <= min(max_summa_len, len(seqs)): # 生成的摘要，最多max_summa_len句话
                pre_summary = '\n'.join([seqs[i] for i in summary_list])
                tmp_i = -1
                for i, seq in enumerate(seqs):
                    if i not in index_set:
                        cur = my_rouge.compute(pre_summary + '\n' + seq, title)
                        if cur > pre_score:
                            pre_score = cur
                            tmp_i = i
                if tmp_i == -1: break
                index_set.add(tmp_i)
                summary_list.append(tmp_i)
                summary_list.sort()

            summary = '\n'.join([seqs[i] for i in summary_list])
            res = json.dumps({'summary': summary, 'title': title}, ensure_ascii=False)
            data.append(res)

            # print(cnt, "dealed")
            # cnt += 1

    data_len = len(data)

    with open('sum2tit_{}.txt'.format(data_len), 'w', encoding='utf-8') as f:
        f.writelines('\n'.join(data))


if __name__ == "__main__":
    # create('/home/nile/Downloads/cont2tit.txt')

    create('/media/nile/study/repositorys/autosumma/summarunner_weather/weather_preprocess/weather_preprocess.txt')


