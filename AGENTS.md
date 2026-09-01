# Repository instructions

このリポジトリでは、会話履歴ではなくファイルから実験の現在地を判断する。

最初に次を実行する。

```bash
python3 scripts/status.py
```

実験を追加・変更するときは以下を守る。

1. `spec.toml` に仮説、ベース実験、変更点、成功条件を実行前に記載する。
2. 1つの実験では主因子を1つだけ変える。
3. Macでの検証は `m_experiments/`、RTX 3090での実験は `l_experiments/`、GPUクラスタ・クラウドでの実験は `g_experiments/` に置く。
4. 環境を移す場合は `scripts/promote_experiment.py` を使い、同じ `expNNN` を保つ。
5. すべての実行は `scripts/run_experiment.py` 経由にし、`metrics.json` を必ず生成する。
6. 実験結果を見た後で成功条件を書き換えない。条件を変える場合は新しい実験にする。
7. `data/` を書き換える処理と、学習・推論処理を分ける。元データは不変として扱う。
8. checkpointやキャッシュなどの重量物をGitへ追加しない。
9. Kaggleへの提出や外部へのpushは自動実行しない。

共有化するのは2つ以上の実験で安定したコードだけとし、それまでは各 `expNNN/` 内で完結させる。
