---
title: VSCodeの拡張機能を作ってみる
emoji: 🛠️
type: tech
topics:
  - VisualStudioCode

published: false
---
VSCodeの拡張機能を作る方法を一通りやってみました。 基本的にLLMに聞いた通りにやったらできたという内容ですが、 自分の備忘録として必要十分な内容を記述していきたいと思います。

作成するのは、 現在のカーソル箇所に「hoge」を追記する機能です。
## 最初だけの準備
最初に必要なライブラリをグローバルインストールします。
```bash
$ npm install -g yo generator-code vsce
```
## 作成
拡張機能を作成するディレクトリを適当に作成し以下のコマンドを実行します。
```
$ yo code
```
実行すると何を作成するのかの選択肢が出てきます。
```bash
     _-----_     ╭──────────────────────────╮
    |       |    │   Welcome to the Visual  │
    |--(o)--|    │   Studio Code Extension  │
   `---------´   │        generator!        │
    ( _´U`_ )    ╰──────────────────────────╯
    /___A___\   /
     |  ~  |
   __'.___.'__
 ´   `  |° ´ Y `

? What type of extension do you want to create?
❯ New Extension (TypeScript)
  New Extension (JavaScript)
  New Color Theme
  New Language Support
  New Code Snippets
  New Keymap
  New Extension Pack
  New Language Pack (Localization)
  New Web Extension (TypeScript)
  New Notebook Renderer (TypeScript)
```
今回は素直に`New Extension (TypeScript)`を選びます。 名前を聞かれるので、`SampleExtension`とします。 他はEnterを連打で進めました。

Gitリポジトリの中に書くファイルが作られ、VSCodeが開きます。
![](https://raw.githubusercontent.com/shogetoshi/obsidian/refs/heads/master/99_Asset/PastedImage20241205231928.png)
### 実装
`src/extension.ts`の中身を以下のように書きます。
```typescript:src/extensions.ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    let disposable = vscode.commands.registerCommand('appendHoge.appendHoge', () => {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            const position = editor.selection.active;
            editor.edit(editBuilder => {
                editBuilder.insert(position, 'hoge');
            });
        }
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}
```
次にpackage.jsonの`contributes`部分を
```json:package.json
"contributes": {
    "commands": [
        {
            "command": "appendHoge.appendHoge",
            "title": "Append Hoge"
        }
    ]
}
```
で置き換えます。

これで拡張機能としては完成です。
## テスト
VSCodeのターミナルで以下を実行します。
```bash
$ npm install
$ npm run compile
```
このあと`F5`を押すと、この拡張機能が有効になった状態のVSCodeウィンドウが立ち上がります。 `⌘n`で新しいファイルを開いてコマンドパレットで`Append Hoge`を選択すると、 カーソルの場所に`hoge`が挿入されます。
## パッケージ化
ターミナル（↑で新しく開いた方ではなく、拡張機能開発の方のウィンドウ）で
```bash
$ vsce package
```
を実行します。

READMEがないと怒られるので、`README.md`の最初の部分を適当に書き換えます。
```markdown
# sampleextension README

This is my test.
```
こちらを参考にしました。
https://zenn.dev/daifukuninja/articles/13a35a8bb3a4a1

READMEを書き換えて再度コマンドを実行します。
```
 WARNING  A 'repository' field is missing from the 'package.json' manifest file.
Do you want to continue? [y/N]
 WARNING  LICENSE.md, LICENSE.txt or LICENSE not found
Do you want to continue? [y/N]
```
というWARNINGが出ますが、どちらも`y`で先に進みます。

これで`./sampleextension-0.0.1.vsix`というファイルが出力されました。 このファイルは単独で拡張機能として利用できるファイルのようです。
## インストール
コマンドパレットで「Install from VSIX」を選択します。 上記で作成したvsixファイルを選択したらインストール完了です。

コマンドパレットから「Append Hoge」が使えるようになりました！
## まとめ
VSCodeの拡張機能を作成する流れを一通り実施しました。 正直かなり簡単に作成できてびっくりです。 TypeScriptのコードをいじる事でかなり何でもできそうですので 色々遊ぶと楽しそうです。
