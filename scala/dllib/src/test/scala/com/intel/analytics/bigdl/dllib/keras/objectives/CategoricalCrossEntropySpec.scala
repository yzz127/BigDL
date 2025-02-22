/*
* Copyright 2016 The BigDL Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

package com.intel.analytics.bigdl.dllib.keras.objectives

import com.intel.analytics.bigdl.dllib.tensor.Tensor
import com.intel.analytics.bigdl.dllib.keras.layers.KerasBaseSpec

class CategoricalCrossEntropySpec extends KerasBaseSpec {

  "CategoricalCrossEntropy loss" should "be ok" in {
    ifskipTest()
    val kerasCode =
      """
        |input_tensor = Input(shape=[3])
        |target_tensor = Input(shape=[3])
        |loss = categorical_crossentropy(target_tensor, input_tensor)
        |input = np.random.uniform(0, 1, [2, 3])
        |Y = np.zeros((2, 3))
        |index = np.array([1, 2])
        |Y[np.arange(2), index] = 1
      """.stripMargin
    val c = CategoricalCrossEntropy[Float]()
    checkOutputAndGradForLoss(c, kerasCode)
  }

  "CategoricalCrossEntropy loss forward negative input" should "be ok" in {
    val input = Tensor[Float](2, 3).rand(-1, 1)
    val target = Tensor[Float](2, 3)
    target.setValue(1, 1, 1)
    target.setValue(2, 2, 1)
    val c = CategoricalCrossEntropy[Float]()
    val o = c.forward(input, target)
    java.lang.Float.isNaN(o) should be (false)
  }
}
