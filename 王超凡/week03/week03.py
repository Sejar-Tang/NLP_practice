# coding=utf-8
import torch
import torch.nn as nn
import numpy

#用RNN和交叉熵完成一个多分类任务，判断某字符字符串的哪一个位置
#字符串由小写字母和*号组成，任务是判断*号的位置，保证每个字符串有且仅有一个*号

g_string_length = 8 #每个样本包含的字符数
g_embedding_dim = 16
g_hiden_size = 128
g_alpha_set = "abcdefghijklmnopqrstuvwxyz"
g_vocab = {
    "[pad]" : 0,
    "a" : 1,
    "b" : 2,
    "c" : 3,
    "d" : 4,
    "e" : 5,
    "f" : 6,
    "g" : 7,
    "h" : 8,
    "i" : 9,
    "j" : 10,
    "k" : 11,
    "l" : 12,
    "m" : 13,
    "n" : 14,
    "o" : 15,
    "p" : 16,
    "q" : 17,
    "r" : 18,
    "s" : 19,
    "t" : 20,
    "u" : 21,
    "v" : 22,
    "w" : 23,
    "x" : 24,
    "y" : 25,
    "z" : 26,
    "*" : 27,
    "[unk]" : 28
}

#构建样本，长度固定10，由小写字母和*号组成，有且仅有1个*号
def build_sample():
    sample = []
    for i in range(g_string_length):
        alpha = g_alpha_set[numpy.random.randint(0, 26)]
        sample.append(g_vocab[alpha])
    star_idx = numpy.random.randint(0, g_string_length) # *号的下标
    sample[star_idx] = g_vocab['*']
    return sample, star_idx

def build_dataset(data_size):
    x_dataset = []
    y_dataset = []
    for i in range(data_size):
        x, y = build_sample()
        x_dataset.append(x)
        y_dataset.append(y)
    return torch.LongTensor(x_dataset), torch.LongTensor(y_dataset)

class TorchModel(nn.Module):
    def __init__(self, input_size):
        super(TorchModel, self).__init__()
        #先embedding
        self.embedding = nn.Embedding(len(g_vocab), g_embedding_dim, padding_idx=0)
        #再RNN层
        self.rnn_layer = nn.RNN(g_embedding_dim, g_hiden_size, bias=False, batch_first=True)
        #线性层
        self.linear_layer = nn.Linear(g_hiden_size, g_string_length)
        #loss函数为交叉熵
        self.loss = nn.functional.cross_entropy
    def forward(self, x, y=None):
        x = self.embedding(x) # 10 * 1 -> batch_size * 10 * 16
        output, h = self.rnn_layer(x) # output: batch_size * 10 * 16 -> batch_size * 10 * 128
        x = output[:, -1, :]
        y_pred = self.linear_layer(x)
        if y is not None:
            return self.loss(y_pred, y)
        else:
            return y_pred


def main():
    epoch_num = 20
    batch_size = 20
    train_sample = 500
    learning_rate = 0.005
    model = TorchModel(g_string_length)
    #优化器
    optim = torch.optim.Adam(model.parameters(), lr=learning_rate)
    #开始训练
    for epoch in range(epoch_num):
        model.train()
        for batch in range(train_sample // batch_size):
            x, y_true = build_dataset(batch_size)
            optim.zero_grad()
            loss = model.forward(x, y_true)
            loss.backward()
            optim.step()
    #检验模型正确率
    model.eval()
    X, Y = build_dataset(100)
    with torch.no_grad():
        result = model.forward(X)
    count = 0
    correct = 0
    for index, pred_tensor in enumerate(result):
        count += 1
        y_pred = torch.argmax(pred_tensor)
        if y_pred == Y[index]:
            correct += 1
    print("预测样本%d个，正确%d个，正确率%f"%(count, correct, correct/count))


if __name__ == "__main__":
    main()