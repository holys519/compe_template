# Experiment workflow

## 1. 仮説を作る

重複を避けるため、まず `python3 scripts/status.py` と `EXPERIMENT_REPORT.md` を確認する。
「何を変えると、どの指標が、なぜ改善するか」を1文にする。

## 2. Mac実験を作る

```bash
python3 scripts/new_experiment.py m "feature baseline" \
  --hypothesis "特徴量XによりCV scoreがbaselineより0.01以上改善する" \
  --base exp000 \
  --change "特徴量Xだけを追加する"
```

自動採番を使わず番号を指定する場合は `--exp exp007` を付ける。

生成されるファイル:

- `spec.toml`: 実験前に固定する仮説、差分、成功条件
- `config.toml`: 実行時設定。Mac、3090、GPUクラスタでキーを揃える
- `run.py`: 実験本体。最後に `metrics.json` を書く
- `README.md`: 背景、実行コマンド、結果、結論
- `run.sh`: 手動確認用。通常は管理スクリプト経由で実行する

## 3. 実行する

```bash
python3 scripts/run_experiment.py m exp007
```

実行ごとに `runs/m/exp007/<run_id>/` が作られ、以下が残る。

- `job.json`: 相対化したコマンド、時刻、終了コード、Git commit、成功条件の判定。ホスト名や絶対パスは保存しない
- `metrics.json`: 指標（実験結果の唯一の契約）
- `spec.toml`, `config.toml`: 実行時点のsnapshot
- `stdout.log`: ローカル確認用。Git管理外
- `artifacts/`: checkpointなど。Git管理外

実験側は `COMPE_ENV`、`COMPE_EXP`、`COMPE_RUN_ID` を参照できる。

独自コマンドを使う場合:

```bash
python3 scripts/run_experiment.py m exp007 -- python3 m_experiments/exp007/train.py --fold 0
```

独自コマンドでも、環境変数 `COMPE_RUN_DIR` が示す場所に `metrics.json` を書く。

## 4. 3090へ昇格する

Macでデータ読み込み、分割、指標、1 batchのforward/backwardまで確認したら昇格する。

```bash
python3 scripts/promote_experiment.py exp007
```

`l_experiments/exp007` が新規作成される。既に存在する場合は上書きしない。
`device` と `num_workers` は昇格時にCUDA向けへ自動変更される。モデルに適したbatch size、epoch、foldなど、残りの計算資源設定を確認する。

```bash
python3 scripts/run_experiment.py l exp007
```

## 5. GPUクラスタ／クラウドへ昇格する

3090環境で学習全体が成立したら、同じ実験番号を `g_experiments` へ昇格する。

```bash
python3 scripts/promote_experiment.py exp007 --from l
```

`g_experiments/exp007` が新規作成される。GPU種別、GPU数、partition、実行時間、containerなどの環境固有設定を確認する。

```bash
python3 scripts/run_experiment.py g exp007
```

MacからGPUクラスタへ直接移す必要がある場合は、移動元と移動先を明示する。

```bash
python3 scripts/promote_experiment.py exp007 --from m --to g
```

## 6. 結論を残す

```bash
python3 scripts/report.py
```

実験READMEの「結果」「結論」も更新する。不採用なら、失敗理由と次に試さない条件を書く。

## metrics.json の契約

最低限、トップレベルに `metrics` オブジェクトを持たせる。

```json
{
  "experiment": "exp007",
  "environment": "m",
  "run_id": "20260831_120000",
  "metrics": {
    "cv_score": 0.8123,
    "runtime_sec": 123.4
  }
}
```

`spec.toml` の `[[success_criteria]]` にある `metric` は `metrics` 内のキーを参照する。
利用可能な演算子は `>`, `>=`, `<`, `<=`, `==`, `!=`。
