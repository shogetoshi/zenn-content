---
title: 【DevIO】"[Python] DB-APIの変数展開について基本を復習してみた"

emoji: 🐼
type: tech
topics:
  - Python
  - Redshift

published: false
devio: true
---
PythonからDBに接続する際のインターフェイスについて、 [PEP 249 – Python Database API Specification v2.0](https://peps.python.org/pep-0249/) （以降はDB-APIと表記） でガイドラインが定められています。

DB-APIのインターフェイスの機能として、 SQLクエリ内にプレースホルダーを配置してそこにPythonのタプルや辞書を渡すことで クエリ実行時に変数を展開させることができます。 この挙動についてきちんと理解していない部分があったので、 非常に基礎的な内容ですが確認を行いました。
## redshift_connector
今回の動作確認には[redshift-connector](https://pypi.org/project/redshift-connector/) (2.1.5)を用いました。 もちろん接続先はRedshiftです。

> This pure Python connector implements [Python Database API Specification 2.0](https://www.python.org/dev/peps/pep-0249/).

と書かれている通り、redshift_connectorはDB-APIに則って実装がされています。
## プレースホルダーによる変数展開
Pythonプログラムから与えらえるSQLクエリにプレースホルダーを配置し、 Redshiftにクエリが投げられる際に変数展開させることができます。

混同してはいけないのは、DB-APIのプレースホルダー展開は Pythonのf-stringなどの変数展開とは別のタイミングで行われるということです。 Pythonのf-stringなどの展開が先に行われて、 その後にDB-APIに準拠した展開が行われることはきちんと意識しておきましょう。
### paramstyle
DB-APIのプレースホルダーの記述方法は全部で5つのスタイルが用意されています。 ユーザは使用するスタイルを1つ選んで実装をします。

5つありますが、使い勝手で3種類に分けられます。
- 辞書で指定するもの
	- `named`, `pyformat`
- タプルで指定するもの（コード内で順序指定あり）
	- `numeric`
- タプルで指定するもの（コード内で順序指定なし）
	- `qmark`, `format`

となります。

ガイドラインとしては`named`, `pyformat`,`numeric`の利用が推奨されています。

> Module implementors should prefer `numeric`, `named` or `pyformat` over the other formats because these offer more clarity and flexibility.

理由は
- `named`, `pyformat`
	- 展開箇所を名前で指定できる
- `numeric`
	- 展開箇所を数字で指定できる
- `qmark`, `format`
	- 展開箇所を指定できない
	- たまたま何番目に出てくるかだけで判断される

ということになります。 より明示的に意図を指定できた方が良いですので、 特に理由がない限り`named`か`pyformat`しか使わないべきだと思います。
## コード例
### pyformat
pyformatを使ったコード例は以下の通りです。
```python
import redshift_connector

conn = redshift_connector.connect(
    host="redshift_host.example.com",
    database="smaple_db",
    port=5439,
    user="sample_user",
    password="Passw0rd",
)

cursor.paramstyle = "pyformat"

query = """
select * from schema_name.table_name
where c1 like '%%' || %(xxx)s || '%%'
limit %(limit)s;
"""
cursor.execute(query, args={"xxx": "hoge", "limit": 10})
results = cursor.fetchall()
print(results)
```
#### ポイント
#### テーブルは展開できない
例えばテーブル名を展開させることはできません。 試しに実行してみると
```python
# ERROR! テーブルの箇所は展開できない
query = """
select * from %(table_name)s;
"""
cursor.execute(query, args={"table_name": "my_table"})
```

```
{'S': 'ERROR', 'C': '42601', 'M': 'syntax error at or near "$1" in context "select * from $1", at line 2', 'P': '16', 'F': '/opt/brazil-pkg-cache/packages/RedshiftPADB/RedshiftPADB-1.0.9616.0/AL2_x86_64/generic-flavor/src/src/pg/src/backend/parser/parser_scan.l', 'L': '860', 'R': 'extended_yyerror'}
```
ここからわかるように、 DB-APIのプレースホルダー展開は単純な文字列の展開よりはもっと高度なことをやっていて、 クエリの構文をきちんと解釈した上で展開していることがわかります。
#### 値は`''`込みで展開される
```
%(xxx)s
```
と書いた部分は
```
'hoge'
```
に展開されます。

なので例えば
```
where c1 = 'some_prefix_%(xxx)s'
```
のように書いても、これは期待通りには動きません。 これはSQLインジェクションを防ぐための仕組みと考えられます。

ただし文字列の結合を意図したクエリの場合はその限りではありません。
```
where c1 = 'some_prefix_' || %(xxx)s
```
と書くことで文字列の一部だけを変数として扱うことができます。

変数側が無理やり変なクエリをねじ込むことはできないが、 クエリ側が想定するような使い方ならある程度許容されるという感じですね。
#### 特殊文字
pyformatの場合`%`は特殊文字とみなされるので、 クエリの中で`%`を使いたい場合は`%%`と重ねる必要があります。

よって、`like`を使った部分一致をしたい場合は
```
where c1 like '%%' || %(xxx)s || '%%'
```
とすることで変数の内容による部分一致を実現できます。
### named
paramstyle = namedもほぼ一緒です。 冗長ですが全文を示します。
```python
import redshift_connector

conn = redshift_connector.connect(
    host="redshift_host.example.com",
    database="smaple_db",
    port=5439,
    user="sample_user",
    password="Passw0rd",
)

cursor.paramstyle = "named"

query = """
select * from schema_name.table_name
where c1 like '%' || :xxx || '%'
limit :limit;
"""
cursor.execute(query, args={"xxx": "hoge", "limit": 10})
results = cursor.fetchall()
print(results)
```
この場合は`%`をエスケープする必要はありません。 特にpyformatに加えて解説することはありません。
## namedとpyformatどっちがいい？
以下の2点から、namedスタイルが一番良さそうです。
### SQLFluffによるフォーマット
私はSQLクエリをSQLFluffでフォーマットしています。 しかし`pyformat`形式のクエリをフォーマットしようとするとエラーが発生するようです。

これはpyformatという名前の通り、 この記法がPython側の都合で設定されていることと考えられます。 SQL側としてはよく知らない記法ということで対応がされていないものと考えられます （推測）。

フォーマッタの支援が受けられないのは困るのでpyformatはちょっと避けたいです。
### Pythonの変数展開との衝突
当然ですが、 Pythonによる変数展開とDB-API仕様による変数展開とは併用が可能です。
```python
# Pythonの変数展開の例
print("今日の天気は%(weather)sです" % {"weather": "晴れ"})
```
全く同じ構文がPythonで展開されたりDBにクエリされたときに展開されたりするのは混乱を生みやすいので、 この意味でもpyformatは避けたいお気持ちです。 とはいえ今はPythonの変数展開はf-stringを使うことが主流ですので、 こちらはあまり気にする必要なさそうです。
## まとめ
PythonからDBにSQLを投げる際のプレースホルダーの動きを復習しました。 paramstyleとしては、まずnamedスタイルが使えるかを検討するのが良さそうですね。

SQLインジェクションを回避するため、 テーブル名に使えなかったり、 基本的には文字列の一部として展開することができないなど、 ある程度クエリの意味を汲み取った上で展開がされるようです。 無邪気にPythonレベルで変数展開してしまうよりは安全に使うことができそうです。

以上誰かの参考になれば幸いです。


