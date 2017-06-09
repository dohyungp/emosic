import numpy as np
import sklearn.metrics as sm
import tensorflow as tf
import genre_model as model

sound_data = np.load('npz/genre.npz')
X_data = sound_data['X']
y_data = sound_data['y']
print(X_data.shape, y_data.shape)

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, test_size=0.2)

batch_size = 3
learning_rate = 0.001
n_epoch = 50
n_samples = len(X_data)                             # change to 1000 for entire dataset
cv_split = 0.8
train_size = int(n_samples * cv_split)
test_size = n_samples - train_size

#model
with tf.variable_scope("genre_convolutional"):
    X = tf.placeholder("float", [None, 96, 1366, 1])
    phase_train = tf.placeholder(tf.bool, name='phase_train')
    y_, weights = model.cnn(X, phase_train)

#train
y = tf.placeholder("float", [None, 7])
lrate = tf.placeholder("float")
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=y_, labels=y))
train_op = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)
predict_op = y_


saver = tf.train.Saver(weights)
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    for i in range(n_epoch):
        training_batch = zip(range(0, len(X_train), batch_size),
                             range(batch_size, len(X_train)+1, batch_size))
        for start, end in training_batch:
            train_input_dict = {X: X_train[start:end],
                                y: y_train[start:end],
                                lrate: learning_rate,
                                phase_train: True}
            sess.run(train_op, feed_dict=train_input_dict)

        test_indices = np.arange(len(X_test))
        np.random.shuffle(test_indices)
        test_indices = test_indices[0:test_size]

        test_input_dict = {X: X_test[test_indices],
                           y: y_test[test_indices],
                           phase_train: False}

        predictions = sess.run(predict_op, feed_dict=test_input_dict)
        print('Epoch : ', i, 'AUC : ', sm.roc_auc_score(y_test[test_indices], predictions, average='samples'))
    save_path = saver.save(sess, 'emosic_model/genre/model.ckpt')
    print('Saved {}'.format(save_path))
