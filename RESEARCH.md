## A Light Weight Model for Active Speaker Detection

Upstream research repository notes (CVPR 2023). SpeakFrame uses the inference pipeline from this codebase.

[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/a-light-weight-model-for-active-speaker/audio-visual-active-speaker-detection-on-ava)](https://paperswithcode.com/sota/audio-visual-active-speaker-detection-on-ava?p=a-light-weight-model-for-active-speaker)

> A Light Weight Model for Active Speaker Detection  
> Junhua Liao, Haihan Duan, Kanghui Feng, Wanbing Zhao, Yanbing Yang, Liangyin Chen

Extended: [LR-ASD (IJCV 2025)](https://junhua-liao.github.io/Junhua-Liao/publications/papers/IJCV_2025.pdf)

### Evaluate on AVA-ActiveSpeaker dataset

```bash
python train.py --dataPathAVA AVADataPath --download
python train.py --dataPathAVA AVADataPath
python train.py --dataPathAVA AVADataPath --evaluation
```

### Evaluate on Columbia ASD dataset

```bash
python Columbia_test.py --evalCol --colSavePath colDataPath
python Columbia_test.py --evalCol --pretrainModel weight/finetuning_TalkSet.model --colSavePath colDataPath
```

### Video demo (CLI)

```bash
python Columbia_test.py --videoName 0001 --videoFolder demo
python Columbia_test.py --videoName 0001 --videoFolder demo --pretrainModel weight/finetuning_TalkSet.model
```

### Citation

```
@InProceedings{Liao_2023_CVPR,
    author    = {Liao, Junhua and Duan, Haihan and Feng, Kanghui and Zhao, Wanbing and Yang, Yanbing and Chen, Liangyin},
    title     = {A Light Weight Model for Active Speaker Detection},
    booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
    month     = {June},
    year      = {2023},
    pages     = {22932-22941}
}
```

