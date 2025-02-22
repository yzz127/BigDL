#
# Copyright 2016 The BigDL Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from unittest import TestCase

import pytest
import torch
from torch.utils.data import TensorDataset, DataLoader, Dataset
from torch import nn
from bigdl.nano.pytorch import Trainer

input1 = TensorDataset(torch.ones(10, 3))
input2 = TensorDataset(torch.ones(10, 4))
label1 = TensorDataset(torch.ones(10))
label2 = TensorDataset(torch.ones(10))


class ChainTensorDataset(Dataset):
    def __init__(self, *datasets):
        self.datasets = datasets

    def __getitem__(self, item):
        outputs = []
        for d in self.datasets:
            output = d[item]
            if len(output) < 2:
                outputs.append(output[0])
            else:
                outputs.append(output)
        return outputs

    def __len__(self):
        return len(self.datasets[0])


class ModelWithMultipleInputs(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear1 = nn.Linear(3, 1)
        self.linear2 = nn.Linear(4, 1)

    def forward(self, x1, x2):
        y1 = self.linear1(x1)
        y2 = self.linear2(x2)
        return y1.squeeze()


class TestDataloader(TestCase):

    def test_multiple_inputs_dataloader(self):

        # legal dataloader 1: Tuple(torch.Tensor), torch.Tensor
        dataset = ChainTensorDataset(ChainTensorDataset(input1, input2),
                                     ChainTensorDataset(label1, label2))
        loader = DataLoader(dataset, batch_size=5)
        model = ModelWithMultipleInputs()
        trainer = Trainer()
        loss = (lambda x, y: torch.mean(x[0] + x[1] + y[0] + y[1]))
        model = trainer.compile(model, loss,
                                optimizer=torch.optim.SGD(params=model.parameters(), lr=0.01))

        (x1, x2), (y1, y2) = next(iter(loader))
        assert isinstance(x1, torch.Tensor) and isinstance(x2, torch.Tensor) \
            and isinstance(y1, torch.Tensor) and isinstance(y2, torch.Tensor)

        trainer.quantize(model, calib_dataloader=loader)

    def test_illegal_data_format(self):
        # illegal dataloader: torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor
        dataset = ChainTensorDataset(input1, input2, label1, label2)
        dataloader = DataLoader(dataset, batch_size=5)
        trainer = Trainer()
        model = ModelWithMultipleInputs()

        with pytest.raises(ValueError, match="Dataloader for quantization should yield data *"):
            trainer.quantize(model, calib_dataloader=dataloader)


if __name__ == '__main__':
    pytest.main([__file__])
