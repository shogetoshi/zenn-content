---
title: "最小限のChrome拡張機能を作ってみる"
emoji: "🐼"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---
```json:manifest.json
{
  "manifest_version": 3,
  "name": "サンプル",
  "version": "1.0",
  "description": "",
  "permissions": ["scripting", "tabs", "activeTab"],
  "background": {
    "service_worker": "background.js"
  },
  "action": {}
}
```

```javascript:background.js
// タブが更新されたときに実行
chrome.tabs.onUpdated.addListener((_, changeInfo, tab) => {
  if (changeInfo.status === "complete") {
    updateAction(tab);
  }
});

// タブが切り替わったときに実行
chrome.tabs.onActivated.addListener((activeInfo) => {
  chrome.tabs.get(activeInfo.tabId, (tab) => {
    updateAction(tab);
  });
});

chrome.action.onClicked.addListener(async (tab) => {
  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: execute,
  });
});

async function execute() {
  //任意の関数
}
```
