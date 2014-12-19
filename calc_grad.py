import numpy as np
import theano
import pylearn2
import audio_dataset

# Calculate gradient of MLP w.r.t. input data
# (assumes rectified linear units and softmax output layer)

def calc_grad(X0, model, label):

    X = model.get_input_space().make_theano_batch()
    Y = model.fprop( X, return_all=True )
    fprop = theano.function([X],Y)

    activations = fprop(X0)

    Wn = model.layers[-1].get_weights()
    bn = model.layers[-1].get_biases()
    Xn = activations[-1]

    # derivative of cost with respect to layer preceeding the softmax
    gradn = Wn[:,label] - Xn.dot(Wn.T) 

    for n in xrange(len(model.layers)-2, 0, -1):
        Wn = model.layers[n].get_weights()
        bn = model.layers[n].get_biases()
        Xn_1 = activations[n-1]

        if type(model.layers[n]) is pylearn2.models.mlp.RectifiedLinear:
            dact = lambda x: x>0
        elif type(model.layers[n]) is pylearn2.models.mlp.Linear:
            dact = lambda x: x
        elif type(model.layers[n]) is audio_dataset.PreprocLayer:
            dact = lambda x: x

        gradn = (dact(Xn_1.dot(Wn)) * gradn).dot(Wn.T)

    return gradn

#def test_grad:
eps  = 0.1
nvis = 100
nhid = 50
n_classes = 10

X0 = np.array(np.random.randn(1,nvis), dtype=np.float32)
label = np.random.randint(0,n_classes)

model = pylearn2.models.mlp.MLP(
    nvis=nvis,
    layers=[
        pylearn2.models.mlp.Linear(
            layer_name='pre',
            dim=513,
            irange=0.1
            ),
        pylearn2.models.mlp.RectifiedLinear(
            layer_name='h0',
            dim=nhid,
            irange=0.1),
        pylearn2.models.mlp.RectifiedLinear(
            layer_name='h1',
            dim=nhid,
            irange=0.1),
        pylearn2.models.mlp.RectifiedLinear(
            layer_name='h2',
            dim=nhid,
            irange=0.1),
        pylearn2.models.mlp.Softmax(
            n_classes=n_classes,
            layer_name='y',
            irange=0.1)
        ])

X = model.get_input_space().make_theano_batch()
Y = model.fprop( X )
fprop = theano.function([X],Y)

Y_plus  = np.log(fprop(X0 + eps)[:,label])
Y_minus = np.log(fprop(X0 - eps)[:,label])
D_num   = (Y_plus - Y_minus) / (2*eps)

D_est   = calc_grad(X0, model, label)

# check diff...

