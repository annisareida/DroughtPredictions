# 🌾 Drought Predictions with VAR-LSTM  

This repository contains the implementation of a hybrid **VAR-LSTM model** for drought prediction in Ogan Ilir Regency, Indonesia. The project focuses on forecasting rainfall and classifying drought severity using the **Standardized Precipitation Index (SPI)**. The system aims to support rice farmers in preparing planting seasons through early and accurate drought predictions.  

## 📊 Dataset  
The dataset was obtained from [NASA POWER](https://power.larc.nasa.gov/) covering the period **2010–2024**.  
- Input features multivariate climate variables:
   -🌡️ Air Temperature at 2m 
   -💧 Dew Point Temperature at 2m
   -🍃 Wind Speed at 10m 
   -☀️ All Sky Surface Shortwave Downward Irradiance  
- Target: rainfall prediction for generating SPI-based drought classification.  

## 🔄 Project Workflow  
1. **Data Collection**: Download historical climate data from NASA POWER (2010–2024).  
2. **Data Preprocessing**: Cleaning, normalization, and SPI calculation.  
3. **Modeling**:  
   - Train a **Multivariate LSTM** model to predict rainfall.  
   - Use a **VAR model** to generate future values of additional climate variables.  
   - Feed VAR results as inputs to LSTM for rainfall prediction.  
4. **Forecasting**: Predict rainfall for the next 2 years (2025–2026).  
5. **Drought Classification**: Apply the Standardized Precipitation Index (SPI) to categorize drought severity.  
6. **Deployment**: Display the predictions in an interactive dashboard.  

## 🌐 Dashboard Access  
The drought prediction dashboard can be accessed here:  
👉 [https://droughteye.streamlit.app/](https://droughteye.streamlit.app/)  

## 📈 Model Performance  
- **MAE**: 0.114  
- **RMSE**: 0.258  

## 📖 About  
This website was developed to present the research results of the **PKM-RE Team from Universitas Sriwijaya 2025**, titled:  
*“Application of Long Short-Term Memory in Rainfall Prediction for Drought Classification Based on the Standardized Precipitation Index in Ogan Ilir Regency.”*  

This research is supported by **PKM-RE 2025 funding from the Ministry of Education, Culture, Research, and Technology of the Republic of Indonesia (Kemendikbudristek RI).**  

---

✨ Developed by the **PKM-RE Universitas Sriwijaya Team 2025**  
