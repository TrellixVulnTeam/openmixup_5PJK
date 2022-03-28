_base_ = '../../_base_/datasets/cifar10/mocov3_vit_sz224_bs64.py'

# model settings
model = dict(
    type='MoCoV3',
    base_momentum=0.99,
    backbone=dict(
        type='VisionTransformer',
        arch='mocov3-small',  # embed_dim = 384
        img_size=224,
        patch_size=16,
        stop_grad_conv1=True),
    neck=dict(
        type='NonLinearNeck',
        in_channels=384, hid_channels=4096, out_channels=256,
        num_layers=3,
        with_bias=False, with_last_bn=True, with_last_bn_affine=False,
        with_last_bias=False, with_avg_pool=False,
        vit_backbone=True),
    head=dict(
        type='MoCoV3Head',
        temperature=0.2,
        predictor=dict(
            type='NonLinearNeck',
            in_channels=256, hid_channels=4096, out_channels=256,
            num_layers=2,
            with_bias=False, with_last_bn=True, with_last_bn_affine=False,
            with_last_bias=False, with_avg_pool=False))
)

# dataset settings for SSL metrics
data_source_cfg = dict(type='CIFAR10', root='data/cifar10/')
test_pipeline = [
    dict(type='Resize', size=256),
    dict(type='CenterCrop', size=224),
    dict(type='ToTensor'),
    dict(type='Normalize', mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
]
val_data = dict(
    train=dict(
        type='ClassificationDataset',
        data_source=dict(split='train', **data_source_cfg),
        pipeline=test_pipeline,
        prefetch=False,
    ),
    val=dict(
        type='ClassificationDataset',
        data_source=dict(split='test', **data_source_cfg),
        pipeline=test_pipeline,
        prefetch=False,
    ))

# interval for accumulate gradient
update_interval = 8  # total: 8 x bs64 x 8 accumulates = bs4096

# additional hooks
custom_hooks = [
    dict(type='CosineScheduleHook',  # update momentum
        end_momentum=1.0,
        adjust_scope=[0.05, 1.0],
        warming_up="constant",
        interval=update_interval),
    dict(type='SSLMetricHook',
        val_dataset=val_data['train'],
        train_dataset=val_data['val'],  # remove it if metric_mode is None
        forward_mode='vis',
        metric_mode='knn',  # linear metric (take a bit long time on imagenet)
        metric_args=dict(knn=200, temperature=0.07, chunk_size=256),
        visual_mode='umap',  # 'tsne' or 'umap'
        visual_args=dict(n_epochs=400, plot_backend='seaborn'),
        save_val=False,  # whether to save results
        initial=True,
        interval=50,
        imgs_per_gpu=256,
        workers_per_gpu=4,
        eval_param=dict(topk=(1, 5))),
]

# optimizer
optimizer = dict(
    type='AdamW',
    lr=2.4e-3,  # bs4096
    betas=(0.9, 0.95), weight_decay=0.1,
    paramwise_options={
        '(bn|ln|gn)(\d+)?.(weight|bias)': dict(weight_decay=0.),
        'bias': dict(weight_decay=0.),
        'pos_embed': dict(weight_decay=0.),
        'cls_token': dict(weight_decay=0.)
    })

# apex
use_fp16 = True
fp16 = dict(type='apex', loss_scale=dict(init_scale=512., mode='dynamic'))
# optimizer args
optimizer_config = dict(update_interval=update_interval, use_fp16=use_fp16, grad_clip=None)

# learning policy
lr_config = dict(policy='CosineAnnealing', min_lr=0.)

# runtime settings
runner = dict(type='EpochBasedRunner', max_epochs=1000)