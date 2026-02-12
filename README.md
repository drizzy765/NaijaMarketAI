# 🇳🇬 AgroPulse: Nigerian Food Inflation Forecaster

![Python](https://img.shields.io/badge/Python-3.9-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Production-green) ![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red) ![Docker](https://img.shields.io/badge/Docker-Containerized-blue) ![License](https://img.shields.io/badge/License-MIT-grey)

**AgroPulse** is a machine learning system designed to analyze and predict food inflation drivers in Nigeria. By leveraging 12 years of historical market data (2012–2023), it identifies the mathematical relationship between fuel prices, transport costs, and staple food prices.

The project features a **Multi-Model AI Engine** that selects the best algorithm for each commodity, wrapped in a production-ready **FastAPI Microservice** and an interactive **Streamlit Dashboard**.

---

![live link](https://naijamarketai-dsyhazpefrewq54rvbtq8x.streamlit.app/)
## Key Features

* **Surgical Data Cleaning:** A custom pipeline that corrects historical unit errors (e.g., the 2016 "Yam Cliff" and 2020 "Garri Spike") using economic heuristics.
* **Multi-Model Intelligence:**
    * **ElasticNet (Linear):** Used for predictable commodities like *Beans Oloyin* ($R^2 = 0.94$).
    * **XGBoost (Tree):** Used to detect weak signals in volatile markets like *Rice*.
    * **Facebook Prophet:** Used for long-term 5-year strategic forecasting.
* **Production API:** A Dockerized REST API that serves real-time predictions and historical data.
* **Interactive Dashboard:** A "Financial Terminal" style frontend allowing users to simulate fuel price shocks and visualize future trends.

---

##  Model Performance Leaderboard

We evaluated four state-of-the-art models. The results revealed a "Tale of Two Markets":

| Commodity | Best Model | $R^2$ Score | Verdict |
| :--- | :--- | :--- | :--- |
| **Beans Oloyin** | **ElasticNet** | **0.94** | **Highly Predictable.** Strongly driven by transport/fuel costs. |
| **Rice Local** | **XGBoost** | **0.01** | *Volatile.** Driven by external shocks (borders, policy) not just fuel. |
| **Yam Tuber** | **Prophet** | N/A | **Stochastic.** Best viewed as a long-term seasonal trend. |

> **Key Insight:** Deep Learning (LSTM) failed to outperform simple linear models for this dataset, proving that for economic data, interpretability and stability often beat complexity.

---

##  Tech Stack

* **Analysis & Modeling:** Python, Pandas, Scikit-Learn, XGBoost, TensorFlow (LSTM), Prophet.
* **Backend API:** FastAPI, Uvicorn, Pydantic.
* **Frontend:** Streamlit, Plotly (for interactive financial charts).
* **DevOps:** Docker.

---

##  Project Structure

```bash
AgroPulse/
├──  analysis_notebooks/    # Jupyter notebooks for training & experiments
├──  all_models.pkl         # The trained Multi-Model Brain (Pickle)
├──  final_dataset_cleaned_v3.csv  # The cleaned historical data
├──  Dockerfile             # Instructions to build the container
├──  main.py                # FastAPI Backend Server
├──  frontend.py            # Streamlit Dashboard
└──  requirements.txt       # Python dependencies
