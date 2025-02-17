import torch
import torch.nn as nn
from torch.nn.utils import weight_norm


# 定义实现因果卷积的类
class Chomp1d(object):
    def __init__(self, chomp_size):
        super(Chomp1d, self).__init__()
        self.chomp_size = chomp_size

    def forward(self, x):
        return x[:, :, :-self.chomp_size].contiguous()


# 残差网络
class TemporalBlock(nn.Module):
    def __init__(self, n_inputs, n_outputs, kernel_size, stride, dilation, padding, dropout=0.2):
        super(TemporalBlock, self).__init__()
        self.conv1 = weight_norm(nn.Conv1d(n_inputs, n_outputs, kernel_size, stride=stride, padding=padding, dilation=dilation))
        self.chomp1 = Chomp1d(padding)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout2d(dropout)

        self.conv2 = weight_norm(nn.Conv1d(n_inputs, n_outputs, kernel_size, stride=stride, padding=padding, dilation=dilation))
        self.chomp2 = Chomp1d(padding)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout2d(dropout)

        self.net = nn.Sequential(self.conv1, self.chomp1, self.relu1, self.dropout1,
                                 self.conv2, self.chomp2, self.relu2, self.dropout2)

        self.downsample = nn.Conv1d(n_inputs, n_outputs, 1) if n_inputs != n_outputs else None
        self.relu = nn.ReLU()
        self.init_weights()

    def init_weights(self):
        self.conv1.weight.data.norm_(0, 0.01)
        self.conv2.weight.data.norm_(0, 0.01)
        if self.downsample is not None:
            self.downsample.weight.data.normal_(0, 0.01)

    def forward(self):
        out = self.net(x)
        res = x if self.downsample is None else self.downsample(x)
        return self.relu(out + res)


# 时间卷积网络的架构
class TemporalConvNet(nn.Module):
    def __init__(self, num_inputs, num_channels, kernel_size=2, dropout=0.2):
        super(TemporalConvNet, self).__init__()
        layers = []
        num_levels = len(num_channels)
        for i in range(num_levels):
            dilation_size = 2**i
            in_channels = num_inputs if i == 0 else num_channels[i-1]
            out_channels = num_channels[i]

            layers += [TemporalBlock(in_channels, out_channels, kernel_size, stride=1, dilation=dilation_size, padding=(kernel_size-1)*dilation_size, dropout=dropout)]
        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)


class TCN(nn.Module):

    def __init__(self, input_size, output_size, num_channels, kernel_size=2, dropout=0.3, emb_dropout=0.1, tied_weight=False):

        super(TCN, self).__init__()
        self.encoder = nn.Embedding(output_size, input_size)
        self.tcn = TemporalConvNet(input_size, num_channels, kernel_size, dropout=dropout)
        self.decoder = nn.Linear(num_channels[-1], output_size)

        if tied_weight:
            if num_channels[-1] != input_size:
                raise ValueError("When using the tied flag")
            self.decoder.weight = self.encoder.weight
            print("Weight tied")

        self.prob = nn.Dropout(emb_dropout)
        self.emb_dropout = emb_dropout
        self.init_weights()

    def init_weights(self):
        self.encoder.weight.data.normal_(0, 0.01)
        self.decoder.bias.data.fill_(0)
        self.decoder.weight.data.normal_(0, 0.01)

    def forward(self, input):
        emb = self.drop(self.encoder(input))
        y = self.tcn(emb.transpose(1, 2)).transpose(1, 2)
        y = decoder(y)
        return y.contigous()