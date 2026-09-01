# g_experiments — GPUクラスタ／クラウド実験

SLURMクラスタ、クラウドGPU、Kaggle GPUなど、ローカルRTX 3090以外のGPU環境で実験する。

- `l_experiments` で成立した実験を、同じ `expNNN` のまま配置する。
- 全Fold、大規模モデル、複数GPU、長時間実行などに使用する。
- scheduler、container、GPU種別、GPU数、実行時間を実験READMEとrun metadataに残す。
- クラスタ固有のjob scriptは各実験内に追加し、最終的に `scripts/run_experiment.py g expNNN` を呼び出す。

RTX 3090環境からの昇格:

```bash
python3 scripts/promote_experiment.py expNNN --from l
```

GPU環境で直接作成:

```bash
python3 scripts/new_experiment.py g "title" --hypothesis "検証する仮説"
```
