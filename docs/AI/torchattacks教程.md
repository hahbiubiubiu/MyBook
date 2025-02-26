[torchattacks](https://github.com/Harry24k/adversarial-attacks-pytorch)

# 准备

以2024羊城杯的AI题作为上手torchattacks的对象。

题目给出模型及其参数：

```Python
def get_model():
    model = models.densenet121(pretrained=True)
    num_ftrs = model.classifier.in_features
    model.classifier = nn.Sequential(
        nn.Linear(num_ftrs, 500),
        nn.Linear(500, 3)
    )
    PATH = 'ckpt_densenet121_catdogfox_classify.pth'
    model.load_state_dict(torch.load(PATH, map_location=device))
    model = model.to(device)
    model.eval()
    return model
```

题目给出猫、狗、狐狸各三组的图片，每组50张。

模型为对猫、狗、狐狸的图片进行分类，题目要求：

1. 猫的图片识别为狗
2. 狗的图片识别为狐狸
3. 狐狸的图片识别猫
4. 对抗样本与原图片的SSMI值小于0.95
5. 成功攻击80%的样本

这里简化下要求，把一张猫的图片识别为狗，且SSMI值小于0.95。

先给出工具函数：

```python
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import torchattacks

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
def get_model():
    model = models.densenet121(pretrained=True)
    num_ftrs = model.classifier.in_features
    model.classifier = nn.Sequential(
        nn.Linear(num_ftrs, 500),
        nn.Linear(500, 3)
    )
    PATH = 'ckpt_densenet121_catdogfox_classify.pth'
    model.load_state_dict(torch.load(PATH, map_location=device))
    model = model.to(device)
    model.eval()
    return model

def predict(model, image):
    with torch.no_grad():
        output = model(image.clone().detach())
        _, predicted = torch.max(output, 1)
    return predicted.item()

def load_image(path):
    image = Image.open(path)
    preprocess = transforms.Compose([
        transforms.ToTensor(),
    ])
    image = preprocess(image).unsqueeze(0)
    return image

def save_image(image, filename):
    image = image.squeeze(0).cpu()
    image = transforms.ToPILImage()(image)
    image.save(filename, format='PNG')

def ssmi_value(ori_image, adv_image):
    ori_image = ori_image.clone().detach().cpu()
    adv_image = adv_image.clone().detach().cpu()
    ori_image_np = ori_image.squeeze().numpy().transpose(1, 2, 0)
    adv_image_np = adv_image.squeeze().numpy().transpose(1, 2, 0)
    ssmi_value = ssim(ori_image_np, adv_image_np, win_size=3, channel_axis=2, data_range=1.0)
    return ssmi_value
```

# Attack

在`torchattacks`中，每种对抗攻击方法，被定义为`class`，继承于`Attack`。

对于攻击的模式是需要设置的：

1. `set_mode_default`：设置为默认模式，即非目标攻击（untargeted attack）。
2. `set_mode_targeted_by_label`：设置为目标攻击模式，通过指定一个具体的标签作为目标。
3. `set_mode_targeted_by_function`：设置为目标攻击模式，通过提供一个函数来生成目标标签。
4. `set_mode_targeted_least_likely`：设置为目标攻击模式，目标标签是最不可能的类别。
5. `set_mode_targeted_random`：设置为目标攻击模式，目标标签是随机选择的类别。

这里根据题意，设置`set_mode_targeted_by_label`。

# FSGM

由于FSGM是一步的，这里迭代地使用了FSGM多次（约等于BIM），达到目的。

```python
def fgsm_attack(image, label, epsilon, model):
    attack = torchattacks.FGSM(model, eps=epsilon)
    perturbed_image = attack(image, label)
    return perturbed_image

def iterative_fgsm_attack(model, image, ori_label, target_label=None, epsilon=0.001, rounds=20):
    attack = torchattacks.FGSM(model, eps=epsilon)
    if target_label is not None:
        attack.set_mode_targeted_by_label()
    else:
        target_label = ori_label
    ori_image = image.clone().detach()
    adv_image = image.clone().detach()
    for i in range(rounds):
        new_adv_image = attack(adv_image, target_label)
        ssmi = ssmi_value(ori_image, new_adv_image)
        new_label = predict(model, new_adv_image)
        if ssmi < 0.95:
            break
        adv_image = new_adv_image
        print(f"round {i}:")
        print(f"Adversarial Image Prediction: {new_label}")
        print(f"SSMI: {ssmi}")
    return adv_image

def main():
    model = get_model()
    image = load_image('./adv_image/cat/cat_001.jpg').to(device)
    ori_label = torch.tensor([0]).to(device)
    target_label = torch.tensor([1]).to(device)
    adv_image = iterative_fgsm_attack(model, image, ori_label, target_label) 
    save_image(adv_image, 'adv_image.jpg')
```

# BIM

BIM其实就是迭代的FSGM。

这里需要设置：

* `eps`：最大扰动
* `alpha`：每步的大小
* `steps`：迭代的轮数

```python
def bim_attack(model, image, ori_label, target_label=None, eps=8/255, alpha=2/255, steps=1):
    attack = torchattacks.BIM(model, eps=eps, alpha=alpha, steps=steps)
    if target_label is not None:
        attack.set_mode_targeted_by_label()
        adv_image = attack(image, target_label)
    else:
        adv_image = attack(image, ori_label)
    return adv_image

def main():
    model = get_model()
    image = load_image('./adv_image/cat/cat_001.jpg').to(device)
    ori_label = torch.tensor([0]).to(device)
    target_label = torch.tensor([1]).to(device)
    adv_image = bim_attack(model, image, ori_label, target_label)
    ssmi = ssmi_value(image, adv_image)
    predicted = predict(model, adv_image)
    print(f"SSMI: {ssmi}")
    print(f"Predicted: {predicted}")
```

# CW

```python
def cw_attack(model, image, ori_label, target_label=None):
    attack = torchattacks.CW(model, c=1, kappa=0, steps=400, lr=0.01)
    if target_label is not None:
        attack.set_mode_targeted_by_label()
        adv_image = attack(image, target_label)
    else:
        adv_image = attack(image, ori_label)
    return adv_image

def main():
    model = get_model()
    image = load_image('./adv_image/cat/cat_001.jpg').to(device)
    ori_label = torch.tensor([0]).to(device)
    target_label = torch.tensor([1]).to(device)
    adv_image = cw_attack(model, image, ori_label, target_label)
    save_image(adv_image, 'adv_image.png')
    ssmi = ssmi_value(image, adv_image)
    predicted = predict(model, adv_image)
    print(f"SSMI: {ssmi}")
    print(f"Original: {predict(model, image)}")
    print(f"Predicted: {predicted}")
```

# PGD

```python
def pgd_attack(model, image, ori_label, target_label=None):
    attack = torchattacks.PGD(model, eps=0.01, alpha=1/255, steps=10)
    if target_label is not None:
        attack.set_mode_targeted_by_label()
        adv_image = attack(image, target_label)
    else:
        adv_image = attack(image, ori_label)
    return adv_image


def pgd_l2_attack(model, image, ori_label, target_label=None):
    attack = torchattacks.PGDL2(model, eps=1, alpha=0.2, steps=20)
    if target_label is not None:
        attack.set_mode_targeted_by_label()
        adv_image = attack(image, target_label)
    else:
        adv_image = attack(image, ori_label)
    return adv_image
```

