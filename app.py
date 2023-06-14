from model import extractValue
import streamlit as st
import numpy as np
import cv2
import pandas as pd

def saveImage(byteImage):
    nparr = np.fromstring(byteImage, np.uint8)
    imgFile = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
   
    return imgFile

st.set_page_config(
    page_title = 'Document OCR Reader',
    page_icon = '🗎'
)

st.header("Read OCR Document Table")
st.subheader("Upload Image First")
fileUpload = st.file_uploader("Choose a file", type = ['jpg', 'png'])

if fileUpload:
    file = fileUpload.read()
    path = saveImage(file)

    st.subheader("Uploaded Image")
    imageUploadedHolder = st.empty()
    imageUploadedHolder.image(path)
    with st.spinner('Wait for it... Detecting and OCR the image'):
        imageResults, textResult, tabelDataframe = extractValue(path)

        st.subheader("Result Image")
        imageDetectedHolder = st.empty() 
        imageDetectedHolder.image(imageResults)

        st.subheader("Text Result")
        st.text(f"Tanggal : {textResult['tgl']}")
        st.text(f"Blok : {textResult['blok']}")
        cols=pd.Series(tabelDataframe.columns)

        for dup in cols[cols.duplicated()].unique(): 
            cols[cols[cols == dup].index.values.tolist()] = [dup + '.' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]

        # rename the columns with the cols list.
        tabelDataframe.columns=cols

        st.dataframe(tabelDataframe)