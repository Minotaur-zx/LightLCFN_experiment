from model_MF import *
from test_model import *
from read_data import *
from print_save import *

def train_model(para):
    [_,_,_,LR,LAMDA,EMB_DIM,BATCH_SIZE, SAMPLE_RATE,N_EPOCH,_,_,] = para
    ## paths of data
    train_path = DIR + 'train_data.json'
    save_embeddings_path = DIR + 'pre_train_feature' + str(EMB_DIM) + '.json'
    ## load train data
    [train_data, train_data_interaction, user_num, item_num] = read_data(train_path)
    ## define the model
    model = model_MF(n_users=user_num, n_items=item_num, emb_dim=EMB_DIM, lr=LR, lamda=LAMDA)

    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    sess = tf.Session(config=config)
    sess.run(tf.global_variables_initializer())

    ## split the training samples into batches
    batches = list(range(0, len(train_data_interaction), BATCH_SIZE))
    batches.append(len(train_data_interaction))

    ## training iteratively
    F1_max = 0
    for epoch in range(N_EPOCH):
        for batch_num in range(len(batches)-1):
            train_batch_data = []
            for sample in range(batches[batch_num], batches[batch_num+1]):
                (user, pos_item) = train_data_interaction[sample]
                sample_num = 0
                while sample_num < SAMPLE_RATE:
                    neg_item = int(random.uniform(0, item_num))
                    if not (neg_item in train_data[user]):
                        sample_num += 1
                        train_batch_data.append([user, pos_item, neg_item])
            train_batch_data = np.array(train_batch_data)
            _, loss = sess.run([model.updates, model.loss],
                               feed_dict={model.users: train_batch_data[:,0],
                                          model.pos_items: train_batch_data[:,1],
                                          model.neg_items: train_batch_data[:,2]})
        F1, NDCG = test_model(sess, model)
        if F1[0] > F1_max:
            F1_max = F1[0]
            user_embeddings, item_embeddings = sess.run([model.user_embeddings, model.item_embeddings])
        ## print performance
        print_value([epoch + 1, loss, F1_max, F1, NDCG])
        if not loss < 10 ** 10:
            break
    save_embeddings([user_embeddings.tolist(), item_embeddings.tolist()], save_embeddings_path)