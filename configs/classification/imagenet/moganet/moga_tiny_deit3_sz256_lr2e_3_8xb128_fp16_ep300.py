_base_ = [
    '../../_base_/models/moganet/moga_tiny.py',
    '../../_base_/datasets/imagenet/moga_light_deit3_sz256_8xbs128.py',
    '../../_base_/default_runtime.py',
]

# data
data = dict(imgs_per_gpu=128, workers_per_gpu=10)

# additional hooks
update_interval = 1  # 128 x 8gpus x 1 accumulates = bs1024

# optimizer
optimizer = dict(
    type='AdamW',
    lr=2e-3,  # lr = 2e-3 / bs1024
    weight_decay=0.04, eps=1e-8, betas=(0.9, 0.999),
    paramwise_options={
        '(bn|ln|gn)(\d+)?.(weight|bias)': dict(weight_decay=0.),
        'norm': dict(weight_decay=0.),
        'bias': dict(weight_decay=0.),
        'layer_scale': dict(weight_decay=0.),
        'scale': dict(weight_decay=0.),
    })

# fp16
use_fp16 = True
fp16 = dict(type='mmcv', loss_scale='dynamic')
optimizer_config = dict(update_interval=update_interval)

# lr scheduler
lr_config = dict(
    policy='CosineAnnealing',
    by_epoch=False, min_lr=1e-6,
    warmup='linear',
    warmup_iters=20, warmup_by_epoch=True,  # warmup 20 epochs with 1r=2e-3
    warmup_ratio=1e-6,
)

# runtime settings
runner = dict(type='EpochBasedRunner', max_epochs=300)
