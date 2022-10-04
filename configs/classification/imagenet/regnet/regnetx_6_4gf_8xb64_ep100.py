_base_ = './regnetx_3_2gf_8xb64_ep100.py'

# model settings
model = dict(
    backbone=dict(type='RegNet', arch='regnetx_6.4gf'),
    head=dict(in_channels=1624, ),
)
