# UPDATED Fri 28 Jan 2022 08:40:00 PM CET

import streamlit as st
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from meteostat import Point, Daily
from datetime import datetime

import saqc


st.title('KIT 200m-Tower')


#@st.cache
def load_data():
    data = pd.read_csv('data.csv')
    data.index = pd.to_datetime(data.time)
    return data

#@st.cache
def flag_data(data):
    qc = saqc.SaQC(data)
    qc = qc.roll(field='temp', target='temp_mean', func=np.mean, window='12H')
    qc = qc.roll(field='temp', target='temp_median', func=np.median, window='12H')
    qc = qc.processGeneric(['temp', 'temp_mean'], target='temp_residues', func=lambda x, y: x - y)
    qc = qc.roll(field='temp_residues', target='residues_mean', window='25H', func=np.mean)
    qc = qc.roll(field='temp_residues', target='residues_std', window='25H', func=np.std)

    qc = qc.processGeneric(field=['temp_residues','temp_mean','temp_median'], target='temp_scores', func=lambda x,y,z: abs((x-y) / z))
    qc = qc.processGeneric(field=['temp_scores', "residues_mean", "residues_std"], target="residues_norm", func=lambda this, mean, std: (this - mean) / std)
    qc = qc.flagRange('temp_scores', max=30)

    return qc

data_load_state = st.text('Loading data...')
data = load_data()

data_load_state.text("Done!")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

st.subheader('Temperature - Hourly')
st.line_chart(data.temp)

st.subheader('SaQC - Projected Outliers')
'''
Simple example of the SaQC (System for automated Quality Control) tool.

https://rdm-software.pages.ufz.de/saqc/index.html

Showing possible outliers according to the z-score of a 12 hour rolling mean.
'''
qc = flag_data(data)

fig, ax = plt.subplots(figsize=(6,4))

d = qc.data

# ax.plot(d.index, d.temp, 'r')
# ax.plot(d.index, d.temp[qc.data.temp_scores > 30], "g^")

d.temp.plot(ax=ax,rot=45)
d[d.temp_scores > 30].plot(kind="scatter", x="time", y="temp",
                     c="red", marker="s", ax=ax, alpha=0.5)

st.pyplot(fig,clear_figure=True)
