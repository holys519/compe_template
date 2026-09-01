# l_experiments — RTX 3090実験

CUDA / RTX 3090環境で本学習と本番に近い検証を行う。

- 全データ、全Fold、必要なepoch数で実行する。
- mixed precision、VRAM、worker数、学習時間を記録する。
- Macで検証済みの実験は同じ `expNNN` で置く。
- GPUでしか成立しない仮説は `new_experiment.py l ...` で直接作成してよい。
- GPUクラスタやクラウドで続ける場合も、同じ `expNNN` で `g_experiments/` へ昇格する。

Macからの昇格:

```bash
python3 scripts/promote_experiment.py expNNN
```

GPUクラスタ／クラウドへの昇格:

```bash
python3 scripts/promote_experiment.py expNNN --from l
```
