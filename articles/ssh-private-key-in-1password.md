---
title: SSHの秘密鍵を1PasswordのVaultから直接利用する
emoji: 🐼
type: tech
topics:
  - SSH
  - 1Password

published: false
---
## バージョン
- 1Password
	- 1Password for Mac 8.10.56 (81056028)
- macOS
	- macOS Sonoma 14.6.1
## やってみる
あるVaultに秘密鍵が保管されている場合を想定してやってみます。
### 秘密鍵の確認
秘密鍵は見た目こんな感じになっているはずです。
![[Pasted image 20250109010000.png]]
単純な「文書」としてインポートすると↓のような見た目になりますが、 これでは期待した通りの動作はできません。
![[Pasted image 20250109091821.png]]
もしSSHキーとして登録されていない場合は「SSHキー」として追加し直します。
![[Pasted image 20250109002002.png]]
### `.ssh/config`
次に自分の手元のSSH設定をします。
```
Host hogehoge-dev
  HostName ***.***.***.***
  User ec2-user
  # IdentityFileによる秘密鍵の指定は削除
  IdentityAgent "~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock"
```
`IdentityAgent`の行を追加します。 （元々`IdentityFile`で秘密鍵を使うようになっていた場合はその指定を削除します。） この設定で、SSH接続時に1Passwordに保存された秘密鍵を探してくれるようになります。
#### 公開鍵を配置する
ただし、このままだと1Passwordに登録されているSSHキーの数が増えると 「Too many authentication failures」というエラーが出るようになってしまいます。 なのでそれを回避します。

SSHキーの「公開鍵」の部分からファイルがダウンロードできます。
![[Pasted image 20250109002429.png]]
保存先として`~/.ssh/`に保存します。 （実際は任意の場所で良いのですが、ここが一番自然だと思います）

次に、下記のように`IdentityFile`として上で保存した公開鍵ファイルを指定します。
```
Host hogehoge-dev
  HostName ***.***.***.***
  User ec2-user
  IdentityFile "~/.ssh/hogehoge-dev.pub"
  IdentityAgent "~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock"
```
これでSSHキーの数が増えても、 問題なく該当の秘密鍵を見つけてくれるようになります。
#### agent.tomlの編集
基本的な設定は以上ですが、 Vaultに保存されているSSHキーの場合は以下の設定が必要になるかと思います。 `~/.config/1Password/ssh/agent.toml`に以下を追加します。
```:~/.config/1Password/ssh/agent.toml
[[ssh-keys]]
account = "（アカウント名）"
```
ここで`（アカウント名）`は1Password画面の左上に出ている文字列です。
![[Pasted image 20250109090131.png]]
これでVaultにあるSSHキーについても期待通りに動作するようになります。
#### 接続
準備できたので、
```bash
ssh hogehoge-dev
```
してみます。
![[Pasted image 20250109090852.png]]
1Passwordの認証画面が出ますのでTouch IDでスマートに認証できます。 1Passwordの認証が済んだあとは勝手に秘密鍵が使われてリモートホストに接続できます。
## 解説つき
まず`IdentityAgent`を設定します。 これは、`IdntityFile`に秘密鍵を設定する代わりに、 秘密鍵を取得する仕組みを利用する時の書き方になります。

その設定値として`~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock`を指定します。 これは1Passwordから秘密鍵を取得するときの固定値になります。

基本的にはこの設定を行うだけで、 SSHしようとしたときに1Passwordを使って秘密鍵の取得をしてくれます。

しかしこの1Passwordの仕組みはかなり単純な動きになっており、 登録されているSSHキーが複数あった場合、 一定の順番で1つずつ秘密鍵を取得しては試してみるというのを繰り返しています。 SSHの認証はサーバ側でリトライの許容回数が設定されているので、 その回数を超えてしまった場合エラーが発生してSSH接続は失敗してしまいます （Too many authentication failures）。

そこで、この当てずっぽうなやり方を回避するために `IdentityFile`として公開鍵を設定します。 公開鍵を指定すると、それを元に正しい秘密鍵を一発で引き当てることができるようになります。
## まとめ
## 参照情報



