"""
Part one: loading the model
"""
 #Imports, ignore warnings
import warnings
warnings.filterwarnings('ignore')
import os
from tensorflow import keras
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from keras.models import model_from_json
import librosa
import librosa.display
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.utils import shuffle
import emot as e

# Read in the JSON file
json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()

# Load the model from JSON 
loaded_model = model_from_json(loaded_model_json)

# Load weights into new model
loaded_model.load_weights('saved_models/Emotion_Voice_Detection_Model.h5')
print('Loaded model from disk')
o = keras.optimizers.RMSprop(lr = 0.00001, decay = 1e-6)
# evaluate loaded model on test data
loaded_model.compile(loss ='categorical_crossentropy', optimizer = o, metrics = ['accuracy'])

"""
Part two: reading in the audio files
"""

# Method for reading in the audio files and extracting features
"""
- d is the directory the audio files, default is the current working directory.
- dur is the duration in seconds that will be read in.
- For this CNN to work, dur must be 2.5
"""
def readAudioFiles(d, dur, sample_rate):
    if d is None:
        d = 'dir'
        
    df = pd.DataFrame(columns=['feature'])
    file_names = []
    i = 0
    for audiofile in os.listdir(d):
        # Load file using librosa
        print(audiofile, "loaded")
        file_names.append(audiofile)
        X, sr = librosa.load(os.path.join(d, audiofile), res_type = 'kaiser_fast', duration = dur , sr = sample_rate, offset = 0.5)
        sr = np.array(sr)
        # Extract the MFCCS
        mfccs = np.mean(librosa.feature.mfcc(y = X, 
                                            sr = sr, 
                                            n_mfcc = 13),
                        axis=0)
        feature = mfccs
        # Add to data frame
        df.loc[i] = [feature]
        i += 1
    df = pd.DataFrame(df['feature'].values.tolist())
    df = shuffle(df)
    df = df.fillna(0)
    return df, file_names 

# Call the method
audio_features, file_names = readAudioFiles(d = 'the-office-audio-clips', dur = 2.5, sample_rate = 44100)

"""
Part three: predicting using the pre-trained CNN
"""
# Format features for the CNN 
audio_features_cnn = np.expand_dims(audio_features, axis = 2)

# Predict using the pretrained weights
preds = loaded_model.predict(audio_features_cnn, 
                             batch_size = 32, 
                             verbose = 1)


"""
Part four: inverse transform the predictions
"""
# Method to inverse transform the predictions
def inverseTransform(preds, emotion_dict):
    # Find the maximum value for each set of predictions and return it
    preds = preds.argmax(axis = 1)
    decoded = []
    preds = preds.tolist()
    # Conversion loop
    for i in range(9):
        key = preds[i]
        filename = file_names[i]
        val = emotion_dict[i]
        print('file name:', filename, '/', 'CNN prediction:', key, '/', 'predicted emotion:', val)
        decoded.append(val) 
    return decoded
"""
Note that the method will print the filename, the prediction that the CNN made, and the predicted emotion.
Let's just say that, emotion detection is sure hard! 

That's what she said... 
"""
emotions = e.emotions
pred_emo = inverseTransform(preds, emotions)
        
