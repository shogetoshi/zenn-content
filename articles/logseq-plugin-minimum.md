---
title: "Logseqプラグインの最小構成"
emoji: "🐼"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---
```typescript:index.ts
/// <reference types="@logseq/libs" />

const main = async () => {
  logseq.UI.showMsg("!!");
  logseq.App.registerCommandPalette(
    {
      key: "format-and-export",
      label: "FormatAndExport",
      keybinding: {
        mode: "global",
        binding: "mod+shift+w",
      },
    },
    () => {
      logseq.UI.showMsg("!");
    }
  );
};
logseq.ready(main).catch(console.error);
```

```json:package.json
{
  "main": "index.html",
  "devDependencies": {
    "@logseq/libs": "^0.0.17"
  }
}
```

```html:index.html
<script src="https://cdn.jsdelivr.net/npm/@logseq/libs"></script>
<script src="./index.ts"></script>
```

index.htmlではCDNでライブラリを読み込んでいる。 ように見せているが、実はLogseq実体の中に存在するライブラリを読んでいる。 この環境を試した時点では、 このURLに存在するライブラリの中身と実際のプラグインが利用するライブラリでは 差分がありますので注意が必要です。
