---
typora-root-url: pics\README
---

# Test-of-Zhishui
### 文件夹中文件介绍

```
question1.py,question2.py,question3.py是测试问题1,2,3的代码，代码中包括了模拟与作图，但没有可视化界面
question_4_simulation.py是测试问题4运算模块的代码，new_UI.py是测试问题4的GUI界面
其余文件为必要的支持文件，（如MatploylibWidget.py用于实现GUI界面中的绘图功能）
```



注：推荐使用虚拟环境来运行本程序，以免对您的本地环境产生干扰。

## 使用步骤

### 安装

### 从GitHub上抓取

```
git clone https://github.com/hyywestwood/Test-of-Zhishui/tree/master
cd Test-of-Zhishui

#### 建议使用 venv 虚拟环境避免依赖包冲突
python3 -m venv venv
# 在 Windows cmd 中：
venv\Scripts\activate.bat
# 在 PowerShell 中：
& ./venv/[bS]*/Activate.ps1
# 在 bash/zsh 中：
source venv/bin/activate
#### venv end

pip install -r requirements.txt
```

![1](/1.png)

### 直接从文件夹使用

如果您是直接获得了本项目的整个文件夹，那么可以在cmd中cd到该文件夹路径下后直接从创建虚拟环境开始



## 运行软件

```python
python new_UI.py
```

 正确进行配置之后，软件便可正常运行

​	![2](/2.png)

```bash

```