# Linux安装Python实验

## 步骤1：更新软件源
**说明：** 首先更新系统的软件包索引，确保安装最新版本
```bash
apt-get update
```
**输出：**
```
Hit:1 http://archive.ubuntu.com/ubuntu jammy InRelease
Get:2 http://archive.ubuntu.com/ubuntu jammy-updates InRelease [119 kB]
Get:3 http://archive.ubuntu.com/ubuntu jammy-security InRelease [110 kB]
Reading package lists... Done
Building dependency tree... Done
All packages are up to date.
```

## 步骤2：安装Python3和pip
**说明：** 安装Python3解释器和pip包管理器
```bash
apt-get install -y python3 python3-pip
```
**输出：**
```
Reading package lists... Done
Building dependency tree... Done
python3 is already the newest version (3.10.6-1~22.04).
The following NEW packages will be installed:
  python3-pip
0 upgraded, 1 newly installed, 0 to remove.
Need to get 1,300 kB of archives.
Get:1 http://archive.ubuntu.com/ubuntu jammy-updates/main amd64 python3-pip all 22.0.2+dfsg-1ubuntu0.4 [1,300 kB]
Fetched 1,300 kB in 1s (1,543 kB/s)
Selecting previously unselected package python3-pip.
(Reading database ... 31245 files and directories currently installed.)
Preparing to unpack .../python3-pip_22.0.2+dfsg-1ubuntu0.4_all.deb ...
Unpacking python3-pip (22.0.2+dfsg-1ubuntu0.4) ...
Setting up python3-pip (22.0.2+dfsg-1ubuntu0.4) ...
```

## 步骤3：验证Python安装
**说明：** 检查Python版本确认安装成功
```bash
python3 --version
```
**输出：**
```
Python 3.10.6
```

## 步骤4：验证pip安装
**说明：** 检查pip版本确认安装成功
```bash
pip3 --version
```
**输出：**
```
pip 22.0.2 from /usr/lib/python3/dist-packages/pip (python 3.10)
```

## 步骤5：升级pip到最新版
**说明：** 升级pip到最新版本以获取最新功能和安全修复
```bash
pip3 install --upgrade pip
```
**输出：**
```
Defaulting to user installation because normal site-packages is not writeable
Collecting pip
  Downloading pip-24.0-py3-none-any.whl (2.1 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.1/2.1 MB 3.2 MB/s eta 0:00:00
Installing collected packages: pip
  WARNING: The scripts pip, pip3 and pip3.10 are installed in '/home/user/.local/bin' which is not on PATH.
Successfully installed pip-24.0
```
