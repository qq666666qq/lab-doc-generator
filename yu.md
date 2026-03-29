# Linux 环境下安装与配置 Python 3.11

&#x20;

## 步骤 1：更新系统软件包索引

**说明：** 在安装新软件前，先更新系统的软件包列表，确保能获取到最新的软件版本信息，避免安装失败或版本过旧。

bash

运行

```
sudo apt update

```

**输出：**

plaintext

```
Hit:1 http://archive.ubuntu.com/ubuntu jammy InRelease
Get:2 http://archive.ubuntu.com/ubuntu jammy-updates InRelease [114 kB]
Get:3 http://archive.ubuntu.com/ubuntu jammy-backports InRelease [108 kB]
Fetched 222 kB in 1s (236 kB/s)
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
All packages are up to date.

```

## 步骤 2：安装依赖工具

**说明：** 安装编译和运行 Python 所需的依赖库，包括 ssl、zlib、ffi 等，保证 Python 安装后功能完整。

bash

运行

```
sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

```

**输出：**

plaintext

```
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
build-essential is already the newest version (12.9ubuntu3).
libssl-dev is already the newest version (3.0.2-0ubuntu1.10).
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.

```

## 步骤 3：下载 Python 3.11 源码

**说明：** 使用 wget 从 Python 官方网站下载 Python 3.11.0 版本的源码压缩包，用于编译安装。

bash

运行

```
wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tar.xz

```

**输出：**

plaintext

```
--2026-03-28 10:00:00--  https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tar.xz
Resolving www.python.org (www.python.org)... 199.232.68.223
Connecting to www.python.org (www.python.org)|199.232.68.223|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 19785664 (19M) [application/x-xz]
Saving to: ‘Python-3.11.0.tar.xz’

Python-3.11.0.tar.xz           100%[=================================================>]  18.87M  45.1MB/s    in 0.4s

2026-03-28 10:00:01 (45.1 MB/s) - ‘Python-3.11.0.tar.xz’ saved [19785664/19785664]

```

## 步骤 4：解压源码包

**说明：** 解压下载好的 Python 源码压缩包，得到可编译的源码目录，方便后续配置与编译。

bash

运行

```
tar -xf Python-3.11.0.tar.xz

```

**输出：**

plaintext

```
（无输出，解压成功）

```

## 步骤 5：进入源码目录并配置编译参数

**说明：** 进入 Python 源码目录，执行 configure 脚本，配置安装路径和编译选项，开启优化。

bash

运行

```
cd Python-3.11.0 && ./configure --enable-optimizations

```

**输出：**

plaintext

```
checking build system type... x86_64-pc-linux-gnu
checking host system type... x86_64-pc-linux-gnu
checking for python3.11... no
checking for python3... python3
checking for --enable-optimizations... yes
checking for a BSD-compatible install... /usr/bin/install -c
checking whether build environment is sane... yes
...
creating Makefile

```

## 步骤 6：编译 Python 源码

**说明：** 使用 make 命令编译 Python 源码，`-j$(nproc)` 表示使用 CPU 核心数并行编译，加快速度。

bash

运行

```
make -j$(nproc)

```

**输出：**

plaintext

```
gcc -c -Wno-unused-result -Wsign-compare -DNDEBUG -g -fwrapv -O3 -Wall    -std=c99 -Wextra -Wno-unused-result -Wno-unused-parameter -Wno-missing-field-initializers -Wstrict-prototypes -Werror=declaration-after-statement  -DPy_BUILD_CORE -o Modules/python.o ./Modules/python.c
...
building build-info
make[1]: Leaving directory '/home/user/Python-3.11.0'

```

## 步骤 7：安装编译好的 Python 3.11

**说明：** 将编译完成的 Python 安装到系统目录，使用 `altinstall` 避免覆盖系统默认 Python。

bash

运行

```
sudo make altinstall

```

**输出：**

plaintext

```
Creating directory /usr/local/bin
Creating directory /usr/local/lib
Creating directory /usr/local/lib/python3.11
...
Collecting setuptools
Collecting pip
Installing collected packages: setuptools, pip
Successfully installed pip-22.3.1 setuptools-65.5.0

```

## 步骤 8：验证 Python 3.11 安装成功

**说明：** 查看 Python 3.11 的版本号，确认安装是否成功以及是否能正常调用。

bash

运行

```
python3.11 --version

```

**输出：**

plaintext

```
Python 3.11.0

```

## 步骤 9：测试 Python 3.11 运行简单代码

**说明：** 使用 Python 3.11 执行一行简单的打印代码，验证解释器功能正常。

bash

运行

```
python3.11 -c "print('Python 3.11 安装成功！')"

```

**输出：**

plaintext

```
Python 3.11 安装成功！
```

