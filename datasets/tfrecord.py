"""
Functions to write the x,y data to a tfrecord file
"""
import tensorflow as tf


def _bytes_feature(value):
    """ Returns a bytes_list from a string / byte. """
    if isinstance(value, type(tf.constant(0))):
        value = value.numpy()  # BytesList won't unpack a string from an EagerTensor.
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def create_tf_example(x, y, domain):
    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'x': _bytes_feature(tf.io.serialize_tensor(x)),
        'y': _bytes_feature(tf.io.serialize_tensor(y)),
        'domain': _bytes_feature(tf.io.serialize_tensor(domain)),
    }))
    return tf_example


def write_tfrecord(filename, x, y, domain):
    """ Output to TF record file """
    assert len(x) == len(y)
    assert len(x) == len(domain)
    options = tf.io.TFRecordOptions(compression_type="GZIP")

    with tf.io.TFRecordWriter(filename, options=options) as writer:
        for i in range(len(x)):
            tf_example = create_tf_example(x[i], y[i], domain[i])
            writer.write(tf_example.SerializeToString())


def tfrecord_filename(domain1, domain2, dataset_name, train_or_test):
    """
    Determine tfrecord filename for source --> target adaptation,
    loading the dataset_name (one of source or target) for training,
    validation, or testing

    domain2=None results in just a single file without the A_and_B prefix.
    This is also the case for those in the "skip" list below.
    """
    names = [domain1, domain2]

    # Sanity checks
    assert train_or_test in ["train", "valid", "test"], \
        "train_or_test must be train, valid, or test"
    assert dataset_name in names, \
        "dataset_name must be one of domain1 or domain2"

    # Some datasets don't need any changes for a particular adaptation, e.g.
    # office is the same for any pair of the 3, so in that case just output a
    # single file without the A_and_B prefix
    skip = ["office_amazon", "office_dslr", "office_webcam"]

    if domain2 is None or (domain1 in skip and domain2 in skip):
        filename = "%s_%s.tfrecord"%(dataset_name, train_or_test)
    else:
        # Prefix is the source and target names but sorted
        names.sort()
        prefix = names[0]+"_and_"+names[1]

        filename = "%s_%s_%s.tfrecord"%(prefix, dataset_name, train_or_test)

    return filename


def tfrecord_filename_simple(dataset_name, train_or_test):
    """
    Version of tfrecord_filename ignoring the pairs and just creating a
    separate file for each domain. This works if there's no changes in the
    data based on the pairing (e.g. no resizing to match image dimensions)
    """
    # Sanity checks
    assert train_or_test in ["train", "valid", "test"], \
        "train_or_test must be train, valid, or test"

    filename = "%s_%s.tfrecord"%(dataset_name, train_or_test)

    return filename
