---
title: 複数GitHubアカウントをssh設定で使い分ける
emoji: 🐕
type: tech
topics:
  - GitHub
  - SSH
  - 1Password
published: false
---

GitHubのアカウントを複数使い分けしようとした時、CloneはできるもののPushができないという問題が起きた。それに対しての対処法をまとめる。 なおここでは通信方式はSSHに限った話とする。

## 何が問題か
GitHubでは、パブリックリポジトリは当然誰でもCloneできるが、Pushは許可されたユーザしかできない。 そのため何も気にせずCloneすると、Pushできないローカルリポジトリができてしまう（ように見える）。

SSH設定で、HostNameで解決することができる。
## 1Passwordでssh登録
1PasswordでSSHキーを新規作成して行きます。

![[Pasted image 20241119035515.png]]

公開鍵をGitHubのSettingsから登録。

![[Pasted image 20241119035629.png]]

Key typeは「Authentication Key」 名前はなんでも良い。特に使わない。



公開鍵を `~/.ssh/github-private.pub`に保存

`~/.ssh/config`に下記を記載
```
Host github-private
  HostName github.com
  IdentityAgent "~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock"
  IdentityFile ~/.ssh/github-private.pub
  User git
  AddKeysToAgent yes
  UseKeychain yes
```

公開鍵を置く理由については、

https://dev.classmethod.jp/articles/ssh-1password-avoiding-too-many-authentication-failures/

を参照して頂きたいのですが、 一言で言うと、これをやらないとどの秘密鍵を使うべきか1Passwordが判別できないためです。

これでgit pushもできるようになる

## sshでのgit clone & pushについて
git clone自体は
```bash
git clone git@github.com:shogetoshi/zenn-content.git
```
で可能。 しかしこれだとpushができない。

sshでgithubにpushする際には、公開鍵をgithub側に登録しておく必要がある。 ↑の作業ですでに登録自体は終わっている。 しかし対応する秘密鍵がどれなのかわからなければpushができない。

`git@github.com`の部分は
- `git`というユーザで
- `github.com`というホストに

接続するという意味です。 github.com自体にはssh秘密鍵がなくても接続できるため、cloneは問題なくできる。 しかしこの場合は（`.ssh/config`に設定しなければ）秘密鍵の指定がない。

pushするためには、接続先ホストの指定を`.ssh/config`で作成したHostにする。 つまり次のようにcloneする。
```bash
git clone git@github-private:shogetoshi/zenn-content.git
```
これで、接続先Hostが `github-private`となる。 これでどの秘密鍵を使うべきかの指定ができるので、正しくpushできる

はじめ`github.com`でcloneした場合、 `.git/config`の`url`を直接書き換えれば良い。

## まとめ
aaa abc
