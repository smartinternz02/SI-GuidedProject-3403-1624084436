import numpy as np
import pandas as pd
import pickle
import requests
from flask import Flask,request,render_template,jsonify
import json

API_KEY = "SiIArWxq8AMlYkusjyyIrYYAStVbjcasqaJuClp59xQy"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}


# NOTE: manually define and pass the array(s) of values to be scored in the next line

app=Flask(__name__,template_folder="templates")
model=pickle.load(open('PRJ.pkl','rb'))
@app.route('/',methods=['GET'])
def home():
    return render_template('home.html')
@app.route('/upload',methods=['GET'])
def upload():
    return render_template('upload.html')
@app.route('/pred',methods=['GET'])
def pred():
    return render_template('result.html')

@app.route('/predict',methods=['GET','POST'])
def predict():
    layer_height=float(request.form['lh'])
    wall_thickness=float(request.form['wt'])
    infill_density=request.form['id']
    infill_pattern=request.form['ip']
    nozzle_temperature=request.form['nt']
    bed_temperature=request.form['bt']
    print_speed=request.form['ps']
    fan_speed=request.form['fs']
    roughness=request.form['rough']
    tension_strength=request.form['ts']
    elongation=float(request.form['elong'])
    if(infill_pattern=='grid'):infill_pattern=0
    else:infill_pattern=1
    arr=[[layer_height,wall_thickness,infill_density,infill_pattern,nozzle_temperature,bed_temperature,print_speed,fan_speed,roughness,tension_strength,elongation]]
    payload_scoring = {"input_data": [{"field": [["layer_height","wall_thickness","infill_density","infill_pattern","nozzle_temperature","bed_temperature","print_speed","fan_speed","roughness","tension_strength","elongation"]], "values": arr}]}
    response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/922c1df6-e8cb-465c-a2ee-83e6a86a2d1c/predictions?version=2021-07-05', json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})
    print("Scoring response")
    predictions=response_scoring.json()
    #print(predictions)
    output=predictions['predictions'][0]['values'][0][1][0]
    if(output==0.0):
        return render_template("result.html",prediction_text="The suggested material is ABS(Acrylonitrile Butadiene Styrene).")
    elif(output==1.0):
        return render_template("result.html",prediction_text="The suggested material is PLA(Poly-actic Acid).")
    else:
        return render_template("result.html",prediction_text="Invalid data")
    
    
if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000,debug=False)