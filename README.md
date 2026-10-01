# 星拂云锦 (xfyj)

适用于 **Minecraft 26.2 + Fabric** 的音乐唱片模组。

向游戏中添加一张自定义唱片：

| 项目 | 值 |
| --- | --- |
| 唱片物品 | `xfyj:music_disc_xfyj` |
| 曲目 | S9ryne - 星拂云锦 feat. koi |
| 时长 | 2:48（168 秒） |
| 唱片类型 | 稀有（Rarity.RARE），堆叠上限 1 |
| 可在唱片机播放 | 是（比较器输出 15） |
| 唱片机曲目 ID | `xfyj:music_disc_xfyj` |
| 音效事件 | `xfyj:music_disc.xfyj` |

## 项目结构

```
src/main/java/com/xfyj/
├── Xfyj.java                    模组入口，注册音效与物品
└── registry/
    ├── ModSounds.java           注册音效事件 xfyj:music_disc.xfyj
    └── ModItems.java            注册唱片物品并挂载唱片机组件

src/main/resources/
├── fabric.mod.json              模组元数据
├── pack.mcmeta                  内置数据/资源包元数据
├── assets/xfyj/
│   ├── icon.png                 模组图标
│   ├── sounds.json              音效定义（曲目 music_disc.xfyj）
│   ├── items/music_disc_xfyj.json        物品模型定义（1.21.4+ 格式）
│   ├── models/item/music_disc_xfyj.json  物品模型
│   ├── textures/item/music_disc_xfyj.png 16x16 唱片贴图
│   ├── lang/en_us.json / zh_cn.json      语言文件
│   └── sounds/records/xfyj.ogg           音乐本体（3.6 MB）
└── data/xfyj/jukebox_song/music_disc_xfyj.json   唱片机曲目数据

mirror.init.gradle                可选的国内镜像开关（-PuseMirrors）
tools/
├── compile_mod.py                用 javac 对着真实 26.2 jar 离线编译校验
├── check_wiring.py               跨文件 ID / 资源路径一致性校验
├── check_sources.py              源码结构校验
└── make_texture.py               从专辑封面生成 16x16 唱片贴图
```

## 如何构建

需要 **JDK 25 或更高版本**（本模板按 Java 25 编译），其余依赖由 Gradle 自动下载。

```bash
# Windows
gradlew.bat build

# macOS / Linux
./gradlew build
```

构建产物：`build/libs/xfyj-1.0.0.jar`

把该 jar 放进 `.minecraft/mods/`，同时安装 **Fabric Loader ≥ 0.19.3** 与
**Fabric API 0.156.0+26.2**。

### 国内网络：Gradle 发行包下载超时

首次构建会自动下载 Gradle 9.5.1（134 MB）。官方
`services.gradle.org` 在国内经常读超时，报错形如：

```
Downloading https://services.gradle.org/distributions/gradle-9.5.1-bin.zip failed: timeout (10000ms)
java.net.SocketTimeoutException: Read timed out
```

本工程已做两处调整：

1. `gradle/wrapper/gradle-wrapper.properties` 的 `distributionUrl` 改为
   **阿里云开源镜像**（已确认该镜像存在 `gradle-9.5.1-bin.zip`）：
   `https://mirrors.aliyun.com/gradle/distributions/v9.5.1/gradle-9.5.1-bin.zip`
2. 读取超时由默认 10 秒提高到 **120 秒**，并允许重试 3 次。

直接重新执行 `gradlew.bat build` 即可。若该镜像不可用，把 `distributionUrl`
换回官方地址，或改用华为云同类镜像。

### 可选：把依赖也走国内镜像

Minecraft、Yarn 映射、Fabric API、Maven Central 仍来自国外主机。若这一步也慢，
加上 `-PuseMirrors`，通过 `mirror.init.gradle` 改走 BMCLAPI 与阿里云：

```bash
gradlew.bat build -PuseMirrors
```

不加该开关时脚本不做任何改写；若某个镜像失效，去掉开关即回到官方源。

### 其他构建问题

- **JDK 版本不符**：本模板要求 JDK 25+；若报
  `Unsupported class file major version`，检查 `JAVA_HOME` 指向的版本。
- **依赖下载中断**：删除 `%USERPROFILE%\.gradle\caches` 后重试。
- **需要代理**：在项目根目录 `gradle.properties` 追加
  `systemProp.https.proxyHost` 与 `systemProp.https.proxyPort`。

## 使用方式

1. 创造模式物品栏 →「工具与实用物品」页签，唱片排在原版唱片之后；
2. 或直接使用命令：`/give @s xfyj:music_disc_xfyj`；
3. 右键唱片机放入唱片即可播放，比较器输出 15。

## 常见问题

**唱片能拿到，但唱片机不播放？**
说明唱片机曲目的 ID 对不上。三个地方必须完全一致：

| 位置 | 值 |
| --- | --- |
| `ModItems.DISC_PATH` | `music_disc_xfyj` |
| 数据文件 | `data/xfyj/jukebox_song/music_disc_xfyj.json` |
| 音效事件 | `xfyj:music_disc.xfyj`（`ModSounds.DISC_SOUND_PATH`） |

三者任一改名，唱片就只是普通物品。可运行 `tools/check_wiring.py` 一次性核对。

**物品代码用的是哪些 26.2 API？**
本项目直接使用真实 API，没有反射兜底。26.2 相对 1.21.x 的主要变化：

- `ResourceLocation` → `net.minecraft.resources.Identifier`
- `RegistryKey` → `net.minecraft.resources.ResourceKey`
- 唱片机组件 → `net.minecraft.world.item.JukeboxPlayable`，
  通过 `Item.Properties#jukeboxPlayable(ResourceKey<JukeboxSong>)` 挂载
- 物品组事件 → `net.fabricmc.fabric.api.creativetab.v1.CreativeModeTabEvents`
  （旧的 `ItemGroupEvents` 已不在 Fabric API 中）
- `CreativeModeTabs` 的页签常量在 26.2 变成了 `private`，因此本模组自行
  构造等价键 `minecraft:tools_and_utilities`
- `CreativeModeTab.Output` 是 `protected`，lambda 参数只能用类型推断

**改动后如何离线自检？**
不需要启动游戏，也不需要完整 `gradlew build`：

```bash
python tools/compile_mod.py     # 用 javac 对着真实 26.2 jar 编译全部源码
python tools/check_wiring.py    # 核对 ID、资源路径、语言键
```

**想换音乐？**
替换 `src/main/resources/assets/xfyj/sounds/records/xfyj.ogg`（推荐 48 kHz Vorbis），
并把 `src/main/resources/data/xfyj/jukebox_song/music_disc_xfyj.json` 里的
`length_in_seconds` 改成实际时长。

**想换贴图？**
`tools/make_texture.py` 会从专辑封面自动生成 16x16 唱片贴图：

```bash
python tools/make_texture.py <封面图片> src/main/resources/assets/xfyj/textures/item/music_disc_xfyj.png
```

## 版权

音乐《星拂云锦 feat. koi》版权归 S9ryne / Pigeon Games 所有，本仓库仅用于
模组封装演示，请勿用于商业用途。
