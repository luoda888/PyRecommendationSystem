from const import *
import tensorflow as tf


def build_features():
    f_dense = []
    f_sparse = []
    # categorical features
    for col, config in EMB_CONFIGS.items():
        ind = tf.feature_column.categorical_column_with_hash_bucket(col, hash_bucket_size=config['hash_size'])
        f_sparse.append(tf.feature_column.indicator_column(ind))
        f_dense.append(tf.feature_column.embedding_column(ind, dimension=config['emb_size']))

    for col, config in BUCKET_CONFIGs.items():
        bucket = tf.feature_column.bucketized_column(tf.feature_column.numeric_column(col), boundaries=config['bin'])
        f_sparse.append(bucket)
        f_dense.append(tf.feature_column.embedding_column(bucket, dimension=config['emb_size']))

    return f_dense, f_sparse
