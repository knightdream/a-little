# 新游戏原型

独立 Unity + C# 2D 游戏项目，参考洞窟物语的玩法组织方式。使用自行生成的色块占位，不依赖 CSE2 源码或美术。

## 打开和运行

1. Unity Hub → Add project from disk → 选择当前 `newgame` 文件夹。
2. 使用 **Unity 6000.0.28f1** 打开。
3. 打开 `Assets/Scenes/TestRoom.unity`，点击 Play，并点击 Game 窗口获得键盘焦点。
4. 如场景缺失，执行菜单 **New Game → Create Test Room**。

操作：A/D 或方向键移动，空格跳跃，J 射击，R 重置整个房间。

## 代码结构

```text
Assets/
├── Scenes/TestRoom.unity         测试场景，只保存启动组件
├── Scripts/
│   ├── Core/
│   │   ├── GameBootstrap.cs      创建关卡、玩家、敌人，镜头和原型 HUD
│   │   └── Prototype.cs          占位图形、刚体创建工具
│   ├── Player/
│   │   └── PlayerController.cs   移动、跳跃缓冲、土狼时间、生命、输入
│   ├── Combat/
│   │   └── Projectile.cs         子弹移动和命中
│   ├── Enemies/
│   │   └── Walker.cs             巡逻 → 受击停顿 → 再次命中后冲撞
│   └── World/
│       ├── TestRoom.cs           整数网格测试关卡，地形使用第 8 层
│       └── ExperiencePickup.cs   经验掉落和拾取
└── Editor/PrototypeSetup.cs      一键生成测试场景
```

NPC 的行为用状态机组织，思路对应 CSE2 的 `act_no`；移动和碰撞采用 Unity Rigidbody2D。Unity 坐标向上为正，1 个世界单位是一个地形格，不使用 CSE2 的 0x200 定点单位。参数不可直接照抄。

目前是最小原型：有平台跳跃、水平射击、三只敌人、受伤保护和经验计数；敌人受到停顿期间的第二次攻击就冲撞，这不是原作行为的逐帧复刻。生命归零后玩家原地重置到出生点，R 则重新加载整个房间。经验尚未驱动武器升级。界面暂用英文，避免占位阶段的系统字体差异。

后续可逐步加入 Tilemap 编辑、斜坡、动画、武器升级、对话和存档。当前没有这些完整系统，也没有导入原作地图或素材。

项目使用 Unity 传统 Input API；Player Settings 中 Active Input Handling 应为 Input Manager (Old) 或 Both。

## 验证记录

2026-10-13：Unity 6000.0.28f1 批处理编译通过，测试场景生成通过；进入 Play Mode 后验证了玩家落地、三只敌人生成、连续受伤保护、经验计数和子弹生成。尚未进行人工画面检查、键盘操作及完整战斗流程验收。

`Assets/Editor/PrototypeSmokeCheck.cs` 是上述运行检查的入口，可通过 Unity 批处理 `-executeMethod NewGame.Editor.PrototypeSmokeCheck.Run` 执行（不要同时传 `-quit`，检查完成会自动退出）。
