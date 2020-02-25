#!flask/bin/python
from flask import Flask, abort, jsonify
from flask import request
import torch
import torch.nn as nn
from torch.autograd import Variable
import joblib
import numpy as np
import time

app = Flask(__name__)

PATH = 'model/'

historic_size = 50

input_dim = 1        # input dimension
hidden_dim = 20      # hidden layer dimension
layer_dim = 3        # number of hidden layers
output_dim = 1       # output dimension

@app.route('/')
def index():
    return "Hello, World!"

'''
Input : array of breathing value of the size of historic_size
Output: airflow estimation + time of execution
'''
@app.route('/getEstimation', methods=['POST'])
def getEstimation():
    t = time.time()
    print(request.json)
    if not request.json or not 'value' in request.json or len(request.json['value']) != historic_size:
        abort(400)
    x = BREATH.transform(np.array(request.json['value']).reshape(-1, 1)).reshape(1, historic_size, 1)   # rescale breathing
    y = model(Variable(torch.from_numpy(x).type(torch.FloatTensor)))                             # prediction
    y = AIRFLOW.inverse_transform(y.cpu().detach().numpy().reshape(-1, 1)).reshape(-1)                          # rescale airflow
    t = time.time() - t                                                                                 # duration estimation
    return jsonify({'airflow' : str(y[0]),'time' : str(t)})


class LSTMModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, layer_dim, output_dim):
        super(LSTMModel, self).__init__()
        # Number of hidden dimensions
        self.hidden_dim = hidden_dim

        # Number of hidden layers
        self.layer_dim = layer_dim

        # LSTM
        self.lstm = nn.LSTM(input_dim, hidden_dim, layer_dim, batch_first=True, dropout=0.2)

        # Readout layer
        self.f1 = nn.Linear(hidden_dim, 10)
        self.d1 = nn.Dropout(p=0.2)
        self.f5 = nn.Linear(10, output_dim)

    def forward(self, x):
        # Initialize hidden state with zeros
        h0 = Variable(torch.zeros(self.layer_dim, x.size(0), self.hidden_dim).type(torch.FloatTensor))

        # Initialize cell state
        c0 = Variable(torch.zeros(self.layer_dim, x.size(0), self.hidden_dim).type(torch.FloatTensor))

        # One time step
        out, (hn, cn) = self.lstm(x, (h0, c0))

        # Index hidden state of last time step
        out = torch.relu(self.f1(out[:, -1, :]))
        out = self.d1(out)
        out = torch.relu(self.f5(out))
        return out


'''
This function load all the models form the file one time before the lauch of the app 
'''
if __name__ == '__main__':
    # Load rescaler
    BREATH = joblib.load(PATH + 'rescale_breath_model.sav')
    print('Breath scaler load successfully')
    AIRFLOW = joblib.load(PATH + 'rescale_airflow_model.sav')
    print('Airflow scaler load successfully')

    # Load LSTM model
    model = LSTMModel(input_dim, hidden_dim, layer_dim, output_dim)
    model.load_state_dict(torch.load(PATH + 'Airflow_estimation_LSTM_model.sav', map_location=lambda storage, loc: storage))
    model.eval()
    print('LSTM load successfully')

    # Start the app
    app.run(debug=True, port=5000)
