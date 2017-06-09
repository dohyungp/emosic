
import tensorflow as tf


def cnn(mel, phase_train):

    def init_weights(shape):
        return tf.Variable(tf.random_normal(shape, stddev=0.01))

    def init_biases(shape):
        return tf.Variable(tf.zeros(shape))

    def batch_norm(x, n_out, phase_train, scope='bn'):
        with tf.variable_scope(scope):
            beta = tf.Variable(tf.constant(0.0, shape=[n_out]), name='beta', trainable=True)
            gamma = tf.Variable(tf.constant(1.0, shape=[n_out]), name='gamma', trainable=True)
            batch_mean, batch_var = tf.nn.moments(x, [0, 1, 2], name='moments')
            ema = tf.train.ExponentialMovingAverage(decay=0.5)

            def mean_var_with_update():
                ema_apply_op = ema.apply([batch_mean, batch_var])
                with tf.control_dependencies([ema_apply_op]):
                    return tf.identity(batch_mean), tf.identity(batch_var)

            mean, var = tf.cond(phase_train,
                                mean_var_with_update,
                                lambda: (ema.average(batch_mean), ema.average(batch_var)))
            normed = tf.nn.batch_normalization(x, mean, var, beta, gamma, 1e-3)
        return normed

    weights = {
        'wconv1': init_weights([3, 3, 1, 32]),
        'wconv2': init_weights([3, 3, 32, 128]),
        'wconv3': init_weights([3, 3, 128, 128]),
        'wconv4': init_weights([3, 3, 128, 192]),
        'wconv5': init_weights([3, 3, 192, 256]),
        'bconv1': init_biases([32]),
        'bconv2': init_biases([128]),
        'bconv3': init_biases([128]),
        'bconv4': init_biases([192]),
        'bconv5': init_biases([256]),
        'woutput': init_weights([256, 7]),
        'boutput': init_biases([7])}

    x = tf.reshape(mel, [-1, 1, 96, 1366])
    x = batch_norm(mel, 1366, phase_train)
    x = tf.reshape(mel, [-1, 96, 1366, 1])

    conv2_1 = tf.add(tf.nn.conv2d(x, weights['wconv1'], strides=[1, 1, 1, 1], padding='SAME'), weights['bconv1'])
    conv2_1 = tf.nn.relu(batch_norm(conv2_1, 32, phase_train))
    mpool_1 = tf.nn.max_pool(conv2_1, ksize=[1, 2, 4, 1], strides=[1, 2, 4, 1], padding='VALID')
    dropout_1 = tf.nn.dropout(mpool_1, 0.5)

    conv2_2 = tf.add(tf.nn.conv2d(dropout_1, weights['wconv2'], strides=[1, 1, 1, 1], padding='SAME'), weights['bconv2'])
    conv2_2 = tf.nn.relu(batch_norm(conv2_2, 128, phase_train))
    mpool_2 = tf.nn.max_pool(conv2_2, ksize=[1, 2, 4, 1], strides=[1, 2, 4, 1], padding='VALID')
    dropout_2 = tf.nn.dropout(mpool_2, 0.5)

    conv2_3 = tf.add(tf.nn.conv2d(dropout_2, weights['wconv3'], strides=[1, 1, 1, 1], padding='SAME'), weights['bconv3'])
    conv2_3 = tf.nn.relu(batch_norm(conv2_3, 128, phase_train))
    mpool_3 = tf.nn.max_pool(conv2_3, ksize=[1, 2, 4, 1], strides=[1, 2, 4, 1], padding='VALID')
    dropout_3 = tf.nn.dropout(mpool_3, 0.5)

    conv2_4 = tf.add(tf.nn.conv2d(dropout_3, weights['wconv4'], strides=[1, 1, 1, 1], padding='SAME'), weights['bconv4'])
    conv2_4 = tf.nn.relu(batch_norm(conv2_4, 192, phase_train))
    mpool_4 = tf.nn.max_pool(conv2_4, ksize=[1, 3, 5, 1], strides=[1, 3, 5, 1], padding='VALID')
    dropout_4 = tf.nn.dropout(mpool_4, 0.5)

    conv2_5 = tf.add(tf.nn.conv2d(dropout_4, weights['wconv5'], strides=[1, 1, 1, 1], padding='SAME'), weights['bconv5'])
    conv2_5 = tf.nn.relu(batch_norm(conv2_5, 256, phase_train))
    mpool_5 = tf.nn.max_pool(conv2_5, ksize=[1, 4, 4, 1], strides=[1, 4, 4, 1], padding='VALID')
    dropout_5 = tf.nn.dropout(mpool_5, 0.5)

    flat = tf.reshape(dropout_5, [-1, weights['woutput'].get_shape().as_list()[0]])
    p_y_X = tf.nn.sigmoid(tf.add(tf.matmul(flat,weights['woutput']),weights['boutput']))

    return p_y_X, weights


def crnn(melspectrogram, phase_train):

    def init_weights(shape):
        return tf.Variable(tf.random_normal(shape, stddev=0.01))

    def init_biases(shape):
        return tf.Variable(tf.zeros(shape))

    def batch_norm(x, n_out, phase_train, scope='bn'):
        with tf.variable_scope(scope):
            beta = tf.Variable(tf.constant(0.0, shape=[n_out]),name='beta', trainable=True)
            gamma = tf.Variable(tf.constant(1.0, shape=[n_out]),name='gamma', trainable=True)
            batch_mean, batch_var = tf.nn.moments(x, [0,1,2], name='moments')
            ema = tf.train.ExponentialMovingAverage(decay=0.5)

            def mean_var_with_update():
                ema_apply_op = ema.apply([batch_mean, batch_var])
                with tf.control_dependencies([ema_apply_op]):
                    return tf.identity(batch_mean), tf.identity(batch_var)

            mean, var = tf.cond(phase_train,
                                mean_var_with_update,
                                lambda: (ema.average(batch_mean), ema.average(batch_var)))
            normed = tf.nn.batch_normalization(x, mean, var, beta, gamma, 1e-3)
        return normed

    weights = {
        'wconv1':init_weights([3, 3, 1, 64]),
        'wconv2':init_weights([3, 3, 64, 128]),
        'wconv3':init_weights([3, 3, 128, 128]),
        'wconv4':init_weights([3, 3, 128, 128]),
        'bconv1':init_biases([64]),
        'bconv2':init_biases([128]),
        'bconv3':init_biases([128]),
        'bconv4':init_biases([128]),
        'woutput':init_weights([32, 10]),
        'boutput':init_biases([10])}    

    x = tf.cast(tf.pad(melspectrogram,[[0,0],[0,0],[37,37],[0,0]],'CONSTANT'),tf.float32)
    x = batch_norm(tf.reshape(x,[-1,1,96,1440]), 1440, phase_train)
    x = tf.reshape(x,[-1,96,1440,1])
    conv2_1 = tf.add(tf.nn.conv2d(x, weights['wconv1'], strides=[1, 1, 1, 1], padding='SAME'), weights['bconv1'])
    conv2_1 = tf.nn.relu(batch_norm(conv2_1, 64, phase_train))
    mpool_1 = tf.nn.max_pool(conv2_1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='VALID')
    dropout_1 = tf.nn.dropout(mpool_1, 0.5)

    conv2_2 = tf.add(tf.nn.conv2d(dropout_1, weights['wconv2'], strides=[1, 1, 1, 1], padding='SAME'), weights['bconv2'])
    conv2_2 = tf.nn.relu(batch_norm(conv2_2, 128, phase_train))
    mpool_2 = tf.nn.max_pool(conv2_2, ksize=[1, 3, 3, 1], strides=[1, 3, 3, 1], padding='VALID')
    dropout_2 = tf.nn.dropout(mpool_2, 0.5)

    conv2_3 = tf.add(tf.nn.conv2d(dropout_2, weights['wconv3'], strides=[1, 1, 1, 1], padding='SAME'), weights['bconv3'])
    conv2_3 = tf.nn.relu(batch_norm(conv2_3, 128, phase_train))
    mpool_3 = tf.nn.max_pool(conv2_3, ksize=[1, 4, 4, 1], strides=[1, 4, 4, 1], padding='VALID')
    dropout_3 = tf.nn.dropout(mpool_3, 0.5)

    conv2_4 = tf.add(tf.nn.conv2d(dropout_3, weights['wconv4'], strides=[1, 1, 1, 1], padding='SAME'), weights['bconv4'])
    conv2_4 = tf.nn.relu(batch_norm(conv2_4, 128, phase_train))
    mpool_4 = tf.nn.max_pool(conv2_4, ksize=[1, 4, 4, 1], strides=[1, 4, 4, 1], padding='VALID')
    dropout_4 = tf.nn.dropout(mpool_4, 0.5)

    gru1_in = tf.reshape(dropout_4,[-1, 15, 128])
    gru1 = tf.contrib.rnn.MultiRNNCell([tf.contrib.rnn.GRUCell(32) for _ in range(15)])
    gru1_out, state = tf.nn.dynamic_rnn (gru1, gru1_in, dtype=tf.float32, scope='gru1')
    
    gru2 = tf.contrib.rnn.MultiRNNCell([tf.contrib.rnn.GRUCell(32) for _ in range(15)])
    gru2_out, state = tf.nn.dynamic_rnn(gru2, gru1_out, dtype=tf.float32, scope='gru2')
    gru2_out = tf.transpose(gru2_out, [1, 0, 2])
    gru2_out = tf.gather(gru2_out, int(gru2_out.get_shape()[0]) - 1)
    dropout_5 = tf.nn.dropout(gru2_out, 0.3)

    flat = tf.reshape(dropout_5, [-1, weights['woutput'].get_shape().as_list()[0]])
    p_y_X = tf.nn.sigmoid(tf.add(tf.matmul(flat,weights['woutput']),weights['boutput']))
    return p_y_X, weights
