---
title: Obsidianのプラグインを作ってみる
emoji: 🐼
type: tech
topics:
  - Obsidian

published: false
---
サンプルプラグインをクローンして、それを改変していく。
## 手順
Vault以下の`.obsidian/plugins`ディレクトリがある。 ここで
```bash
git clone https://github.com/obsidianmd/obsidian-sample-plugin.git 
```
でサンプルプラグインをクローンしてくる。

そのディレクトリに入ったら
```bash
npm install
```
で必要なものをインストール。 TypeScriptになっているので`main.js`を作るために
```bash
npm run dev
```
を実行すると`main.js`が作られて読み込めるようになる。

読み込むにはObsidianのコミュニティプラグインで当該プラグインを有効にする/
## .editorconfig
インデントがタブになっているので、スペースにします。
```
indent_style = space
```
## 注意点
Obsidianからこのプラグインを削除すると、 リポジトリごと全て消えてしまう。 Gitで履歴を撮っていたとしても`.git`ディレクトリごと全て消えてしまうので注意が必要。
## ホットリロード
https://github.com/pjeby/hot-reload
をgit cloneしてプラグインのディレクトリに配置します。 これを有効にすることで開発しているプラグインのホットリロードが有効になります。

