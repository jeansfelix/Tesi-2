from customized_hist import retrieve_data

import numpy as np
import tensorflow as tf


t, v, test = retrieve_data()

X_train, y_train = t
X_validation, y_validation = v
X_test, y_test = test

# help function to sampling data
def get_sample(num_samples, X_data, y_data):
	positions = np.arange(len(y_data))
	np.random.shuffle(positions)

	X_sample = []
	y_sample = []

	for posi in positions[:num_samples]:
		X_sample.append(X_data[posi])
		y_sample.append(y_data[posi])

	return X_sample, y_sample


######################## creating the model architecture #######################################
#com 300 nodes, obtivemos 37.4%, com 500 batch e 20000 rounds
#com 1000 nodes, obtivemos 37.8% com 500 batch e 20000 rounds
#alterar de softmax para apenas tanh reduziu os resultados para ~10% com 500 batch e 20000 rounds
#combinar tanh na hidden com softmax no estimated produziu 37.6% com 1000 nodes, 500 batch e 20000 rounds
#combinar tanh na hidden com softmax no estimated produziu 39.4% com 1000 nodes, 1000 batch e 20000 rounds
#aumentar peso do treino para 0.8 produziu 36.2% com 1000 nodes, 1000 batches e 20000 rounds
#fazendo o mesmo que acima, mas reduzindo para 100 batches e 1000 rounds produziu 38.2%
#aumentando para 5000 nodes, produzimos 38.4%
#
num_nodes_hidden_layer = 5000

# input placeholder
x = tf.placeholder(tf.float32, [None, 32])

# output placeholder
y_ = tf.placeholder(tf.float32, [None, 10])


# weights of the neurons in first layer
W1 = tf.Variable(tf.random_normal([32, 20], stddev=0.35))
b1 = tf.Variable(tf.random_normal([20], stddev=0.35))

# weights of the neurons in second layer
W2 = tf.Variable(tf.random_normal([20,10], stddev=0.35))
b2 = tf.Variable(tf.random_normal([10], stddev=0.35))

# hidden_layer value
hidden_layer = tf.nn.tanh(tf.matmul(x, W1) + b1)

# output of the network
y_estimated = tf.nn.softmax(tf.matmul(hidden_layer, W2) + b2)


# function to measure the error
cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y_estimated), reduction_indices=[1]))

# how to train the model
train_step = tf.train.GradientDescentOptimizer(0.2).minimize(cross_entropy)


# how to evaluate the model
correct_prediction = tf.equal(tf.argmax(y_estimated,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))


######################## training the model #######################################

# applying a value for each variable (in this case W and b)
init = tf.initialize_all_variables()


# a session is dependent of the enviroment where tensorflow is running
sess = tf.Session()
sess.run(init)

num_batch_trainning = 5000
total_rounds_of_trainning = 10000
for i in range(total_rounds_of_trainning): # trainning 1000 times

	# randomizing positions
	X_sample, y_sample = get_sample(num_batch_trainning, X_train, y_train)

	# where the magic happening
	sess.run(train_step, feed_dict={x: X_sample, y_:  y_sample})

	# print the accuracy result
	if i % 100 == 0:
		print i, "of", total_rounds_of_trainning, ": ",
                val = (sess.run(accuracy, feed_dict={x: X_validation, y_: y_validation}))	
                train =(sess.run(accuracy, feed_dict={x: X_train, y_: y_train})) 
                print "train={}, val={}".format(train, val)

print "\n\n\n"
print "TEST RESULT: ", (sess.run(accuracy, feed_dict={x: X_test, y_: y_test}))
