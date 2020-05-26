#### IOTA 环境搭建

官方教程地址：https://docs.iota.org/docs/compass/0.1/how-to-guides/set-up-a-private-tangle#prerequisites

按照官方教程执行到Step 2.2时

1. 如果出现 **error: java_base** 

```
cd compass and 修改文件 `WORKSPACE` 中的内容，将如下内容
container_pull(
    name = "java_base",
    digest =       "sha256:bb1c9179c2263733f235291998cb849d52fb730743125420cf4f97a362d6a6dd",
    registry = "gcr.io",
    repository = "distroless/java",
)
修改为
container_pull(
     name = "java_base",
     registry = "index.docker.io",
     repository = "anjia0532/distroless.java",
     tag = "latest"
  )
```

2. 如果出现**error: no such package @io_netty_netty_tcnative_boringssl_static//jar**

```
在Step 1.2中安装0.29版本:
"wget https://github.com/bazelbuild/bazel/releases/download/0.29.0/bazel-0.29.0-installer-linux-x86_64.sh"
然后在Step 2.2执行中报错后，进入
"/home/YOURUSERNAME/.cache/bazel/bazel_YOURUSERNAME/SOMECOMBINATIONOFNUMBERSANDLETTERS/external/io_grpc_grpc_java"
修改脚本"repositories.bzl"，将内容修改为网站
https://github.com/Exo-dar/exo/blob/master/repositories.bzl
中的内容，保存后运行Step 2.2的命令
```

3. 在执行docker相关命令时，可能出现如下错误

```
”Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get http://%2Fvar%2Frun%2Fdocker.sock/v1.26/images/json: dial unix /var/run/docker.sock: connect: permission denied“
```

​	只需创建docker用户组，并将当前用户加入到docker用户组中

```
sudo groupadd docker     #添加docker用户组
sudo gpasswd -a $USER docker     #将登陆用户加入到docker用户组中
newgrp docker     #更新用户组
docker ps    #测试docker命令是否可以使用sudo正常使用
```

4. 如果出现google.io...相关的报错，需要科学上网，如果使用的虚拟机，建议修改git的代理为科学上网的端口 (本机科学上网的端口地址为 192.168.0.103:7890)

```
git config --global http.proxy http://192.168.0.103:7890
git config --global https.proxy http://192.168.0.103:7890
```



接着继续按官方教程走，到Step 2.8修改config.json内容时，如果电脑配置不够，建议将depth修改为3，配置足够则修改为16，此外为保证IRI节点可访问，还需要对API接口的开发进行修改，IRI的API配置见

https://docs.iota.org/docs/node-software/0.1/iri/references/iri-configuration-options

这里仅限制了removeNeighbors, setApiRateLimit两个接口，修改后的内容如下

```
{
	"seed": "步骤3所创建的seed",
	"powMode": "CURLP81",
	"sigMode": "CURLP27",
	"security": 1,
	"depth": 16,
	"milestoneStart": 0,
	"mwm": 9,
	"tick": 60000,
	"host": http://localhost:14265,
	"REMOTE_LIMIT_API": "removeNeighbors, setApiRateLimit"
}
```



接着继续按照教程走，到Step 3.3时，先修改02_run_iri.sh的内容，在其中添加

```
--remote-limit-api $REMOTE_LIMIT_API
```

到Step 3.4时不要执行 **Ctrl+C** ，另开终端继续执行教程内容，启动Compass协调器。Compass协调器在第一次启动的指令为

```
sudo ./03_run_coordinator.sh -bootstrap -broadcast
```

往后启动的指令为

```
sudo ./03_run_coordinator.sh -broadcast
```



官方教程中Step 5测试过程已失效。建议采用官方各语言使用教程进行测试，下网址为Python在IOTA中的使用教程

https://docs.iota.org/docs/client-libraries/1.0/getting-started/python-quickstart

示例使用如下

```python
def getNewAddress(seed):
    # 获取IOTA api函数接口
    api = Iota(ip, seed=seed, testnet=True)
    # 设置信息传输安全等级
    security_level = os.getenv('SECURITY_LEVEL', 1)
    # 获取可用的交易地址
    address = api.get_new_addresses(index=0, count=1,
                                    security_level=security_level)['addresses'][0]
    return str(address)
    
    
def transaction(seed, address, form):
    # 获取IOTA api函数接口
    api = Iota(ip, seed=seed, testnet=True)
    # 将要传送的json数据字符串化
    stringified = json.dumps(form)
    # 转换数据编码格式
    message = TryteString.from_unicode(stringified)
    # 对交易进行打包
    tx = ProposedTransaction(
        address=Address(address),
        message=message,
        value=0
    )
    # 发送交易并获得交易结果
    result = api.send_transfer(transfers=[tx])
    # 取出返回的hash值
    tail_transaction_hash = result['bundle'].tail_transaction.hash
    return str(tail_transaction_hash)
    
    
def getInformation(hash_value, seed=None):
    # 获取IOTA api函数接口
    if seed is None:
        api = Iota(ip, testnet=True)
    else:
        api = Iota(ip, seed=seed, testnet=True)
    # 获取交易捆绑
    bundle = api.get_bundles(hash_value)
    # 读取交易信息
    message = bundle['bundles'][0].tail_transaction.signature_message_fragment
    # 将信息转成json数据格式并返回
    jsonData = json.loads(message.decode())
    return jsonData
```



注：

1. 在config.json中，depth的数值会影响IOTA的执行效率
2. 在重新开机后，运行 02_run_iri.sh 之前需要执行 bazel run //docker:layers_calculator ；在运行 03_run_coordinator.sh 之前，需要执行 bazel run //docker:coordinator

