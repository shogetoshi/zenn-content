---
title: 【DevIO】CloudTrailの証跡をDuckDBで愚直にクエリする

emoji: 🐼
type: tech
topics: 
published: false
devio: true
---
前回こんな記事を書きました。
https://dev.classmethod.jp/articles/cloudtrail-lake-for-beginner/
CloudTrailの証跡を一通りクエリできるようになったのですが、 ちょっと準備が面倒だなという感想が残りました。

よく考えてみたら証跡はただのJSONファイルです。 JSONファイルをクエリするのに何もそんな大層なことをする必要はないな、 と気づいてしまったわけです。 ということで、 JSONファイルをローカルに持ってきてDuckDBでクエリしてみようと思います。

もちろんJSONをローカルにもって来られない環境の方もいるかと思いますが、 ローカルに持って来られるならこのやり方の方がかなり楽だなと思います。

ちなみに私はDuckDBを全然使いこなせていないので、 CLIの`duckdb`コマンドで本当に使い捨てのクエリを実行する形を取ることにします。 対象データが本当に大きくなってきたり、 何度も同じ対象にクエリをするならDBにインポートするなどの方法が有効ですが、 使い捨てならそんな考慮をする前にさっさと中を見てしまった方が良いと思います。
## やってみる
AWS CLI、DuckDBのインストールは割愛させて頂きます。
### 証跡のダウンロード
証跡はただのS3オブジェクトです。 これをダウンロードしてきます。 ある程度の期間をがばっと取ってくるのでAWS CLIを利用します。

実際のコマンドはこんな感じです。
```bash
aws s3 cp s3://bucket-name/AWSLogs/123456789012/CloudTrail/ap-northeast-1/2025/03/01/ . --recursive 
```
大量のファイルをダウンロードするので、 新しく作ったディレクトリで操作することが実質必須です。

このS3パスからわかる通り、
- 日時
- リージョン

については探索対象範囲が事前に目星がついていることを前提としています。 これはCloudTrailの証跡を見たいという用途においては前提にできることが多いと思います。

今回は24時間分で517ファイルでした。 gz圧縮後のファイル容量合計は6.4MB。
### 日時について
S3パスの日時についてのルールは以下のようになっているようです。
```
パスの例） s3://bucket-name/AWSLogs/123456789012/CloudTrail/ap-northeast-1/2025/03/01/123456789012_CloudTrail_ap-northeast-1_20250301T0000Z_f73oSTJKZvI6Uy4h.json.gz
```
- `2025/03/01/`
	- UTCにおける日付です。次項と全く同じ日付になるように見えます
- `20250301T0000Z`
	- UTCにおける日時（秒なし）です。
	- この部分は5分刻みの時刻になっている
		- 必ずしも5分刻みの全ての時刻ファイルが出力されるわけではない（歯抜けあり）
		- この部分が全く同一のファイルが複数出力されることがある（重複あり）
- ファイルの出力時刻
	- 前項の時刻のおよそプラスマイナス5分の間に出力される
		- ファイルの時刻よりも前に出力されることもある
## ファイルの整形
ダウンロードしてきたファイルをDuckDBで見れるように少し整形します。 それぞれのファイルはjson.gzになっているので、安直に解凍して結合します。
```bash
for f in *.json.gz; do
  cat $f | gzip -d | jq '.Records.[]' >> all.json
done
```
この辺は正直全然スマートなやり方ではないと思います。 ただ私はシェル上でのコマンドでファイルを変換する処理が大好きなので、 このやり方が結局一番しっくりきます。 517ファイルが対象で3秒ほどかかりました。

なお`jq '.Records.[]'`で配列の中があらわになるように剥いています。 DuckDBはこの形式（JSONL）であれば同一要素の配列であると解釈してくれるようです。
## DuckDBでクエリする
```bash
duckdb -c "select * from 'all.json'"
```
基本的にはこんな感じでクエリが打てます。 これだと何もフィルタなどはしていないので出力はこんな感じです。
![Pasted image 20250402003612.png](https://devio2024-2-media.developers.io/upload/4U3o45fAuZZUasz83nnvPk/2025-04-01/dNj4j935Rt75.png)
今回は24時間分 * 1リージョンのファイルを持ってきていて、 およそ2万レコードありましたが、 クエリはほぼ一瞬と言っていいくらいの時間で完了しています。
### パイプラインに流して整形する
完全におまけな話ですが、 `duckdb`コマンドの出力は当然パイプラインに流せます。 なので次のようなコマンドを使えば、 あるロールが実行したサービス名とアクションの組を得ることができます。
```bash
$ duckdb -csv -c \
"select distinct eventSource, eventName from 'all.json' \
where userIdentity.arn like '%Lambda%'" | \
sed 's/\.[^,]\+,/:/' | sort
```
出力結果はこんな感じになります。
```
dynamodb:DescribeStream
ec2:DescribeFlowLogs
ec2:DescribeSnapshots
ec2:DescribeSubnets
ec2:DescribeVpcEndpointServices
ec2:DescribeVpcEndpoints
ec2:DescribeVpcs
ec2:GetEbsEncryptionByDefault
ec2:GetManagedPrefixListEntries
ecr:BatchGetRepositoryScanningConfiguration
ecr:DescribeRepositories
eks:ListClusters
```
これで許可したいアクションとしてIAMポリシーにペタッと貼り付けられますね。
### コマンド解説
- `duckdb`
	- -csv: 出力をcsv形式にします。
	- -c: 次の要素をクエリとして実行します。
- `sed`
	- `dynamodb.amazonaws.com,DescribeStream`を
	- `dynamodb:DescribeStream`に変換しています。
- `sort`
	- まぁサービス順に並んでいた方が良いので...
## 後片付け
書くまでもないですが、 ローカルに保存したファイルをディレクトリごと削除したら後片付け完了です。
## まとめ
CloudTrailの証跡であるjson.gzファイルをローカルで愚直に`duckdb`コマンドでクエリする方法をご紹介しました。 うまい方法というよりは本当に愚直な方法ですが、 こういうシンプルなやり方が現場では役に立ったりするんだよなぁと思っています。 とにかくすぐに証跡の中身を見たいという用途で使ってみてはいかがでしょうか？

以上、誰かの参考になれば幸いです。
