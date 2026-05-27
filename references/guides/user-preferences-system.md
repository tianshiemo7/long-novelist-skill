# 用户偏好持久化系统

> 本文件定义 long-novelist 的用户偏好存储与使用机制，确保跨会话写作体验的一致性。

---

## 一、存储文件

`user-preferences.json`（位于技能根目录 `C:\Users\刘朝阳\.claude\skills\long-novelist\` 下，首次使用后自动创建）

---

## 二、数据结构

```json
{
  "version": 1,
  "createdAt": "2026-05-27",
  "updatedAt": "2026-05-27",
  "preferences": {
    "favoriteGenres": [],
    "preferredProtagonistType": "",
    "preferredProtagonistGender": "",
    "preferredConflictType": "",
    "defaultChapterWordCount": 4000,
    "preferredWorldbuilding": "",
    "preferredPerspective": "",
    "preferredTone": "",
    "preferredTheme": "",
    "preferredTargetReaders": "",
    "styleImitationTargets": [],
    "commonSpecialRequirements": [],
    "dislikes": []
  },
  "creationHistory": [
    {
      "title": "",
      "genre": "",
      "totalChapters": 0,
      "totalWords": 0,
      "completedAt": "",
      "notes": ""
    }
  ],
  "feedbackPatterns": {
    "commonCorrections": [],
    "praisedPatterns": []
  }
}
```

---

## 三、偏好更新规则

| 时机 | 行为 |
|------|------|
| Phase 1 配置完成后 | 自动将本次所有配置写入偏好文件 |
| 每完成一部作品 | 将作品信息追加到 `creationHistory` |
| 用户说"记住这个风格" | 将当前风格设定追加到对应偏好字段 |
| 用户说"记住我的偏好" | 保存当前所有配置到偏好 |
| 用户说"忘记XX偏好" | 清除指定维度的偏好 |
| 用户说"重置偏好" | 清空所有偏好数据 |
| 写作中反复出现同类修改 | 静默追加到 `feedbackPatterns.commonCorrections` |
| 用户明确表扬某个写法 | 静默追加到 `feedbackPatterns.praisedPatterns` |

---

## 四、偏好如何影响交互

### Phase 1 配置阶段

1. **快捷入口检测**：如有偏好，提供"使用上次配置"选项，跳过重复问答
2. **选项排序**：将 `favoriteGenres` 匹配项排在最前面
3. **默认值**：`defaultChapterWordCount` 作为每章字数的默认值
4. **⭐标记**：对匹配历史偏好的选项标记"你的常用"
5. **个性化建议**：结合历史偏好给出推荐（如"你之前写仙侠+群像+权谋，这次要不要试试……"）

### Phase 2 规划阶段

1. **风格参考优先**：优先推荐 `styleImitationTargets` 中的作者/作品
2. **字数经验参考**：根据 `creationHistory` 中的历史数据给出现实的完成周期预估

### Phase 3 写作阶段

1. **避坑提醒**：写作前读取 `feedbackPatterns.commonCorrections`，在写作时主动避免历史常见问题
2. **亮点复用**：写作前读取 `feedbackPatterns.praisedPatterns`，在合适的场景复用被表扬过的写法
3. **字数把控**：若历史作品平均每章字数与设定有偏差，提醒调整

### Phase 4 大纲辅助

1. **偏好范围内的搜索**：联网搜索时优先推荐与偏好风格匹配的创作建议

---

## 五、feedbackPatterns 自动学习机制

### 触发条件

写作阶段 Phase 3 中，当以下情况发生时自动记录：

| 触发事件 | 记录方式 |
|----------|----------|
| 用户连续3次提出同类修改意见 | 追加到 `commonCorrections`，附注频率 |
| 用户明确说"这段写得好"/"这个写法不错" | 追加到 `praisedPatterns` |
| 用户连续多章没提某方面意见 | 该方面标记为"已内化"，降低提醒优先级 |

### 新旧用户区别

- **新用户（无偏好文件）**：完整的13问配置流程
- **回流用户（有偏好文件）**：展示上次配置摘要，提供"沿用上次"快捷选项
- **多产用户（≥3部作品历史）**：启动时展示创作统计，提供"随机灵感"功能

---

## 六、操作命令

| 用户命令 | 系统行为 |
|----------|----------|
| "查看我的偏好" | 以表格展示当前偏好文件所有内容 |
| "修改XX偏好为YY" | 更新指定字段，展示修改前后对比 |
| "沿用上次配置" | 加载偏好作为当前配置，跳过问答 |
| "忘记我的风格偏好" | 清除 `styleImitationTargets` 和 `preferredTone` |
| "重置所有偏好" | 清空文件（保留 version），重新走完整配置流程 |
| "导出偏好" | 将偏好文件内容展示为可读文本 |

---

## 七、错误恢复

- **偏好文件损坏（JSON解析失败）**：忽略偏好，使用默认值，后台新建备份文件并重建
- **偏好文件缺失**：正常走完整配置流程，结束后自动创建
- **字段版本不兼容**：按字段逐一解析，不兼容字段使用默认值，静默升级
- **写入失败（权限不足等）**：提示用户检查文件权限，本次会话使用内存模式
