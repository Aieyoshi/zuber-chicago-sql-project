# Zuber Chicago — SQL Project (EDA + Hypothesis Testing)

Analysis of Chicago taxi trips using **SQL + Python** to understand competitor patterns and test whether weather affects trip duration.

---

## Project goals
1. Identify patterns in taxi company activity (competitors).
2. Find the most common dropoff neighborhoods.
3. Test the hypothesis:

> **“The average duration of trips from Loop to O’Hare changes on rainy Saturdays.”**

---

## Data
This repo uses the project-provided datasets:

- `project_sql_result_01.csv` — trips by taxi company (Nov 15–16, 2017)
- `project_sql_result_04.csv` — average number of dropoffs by neighborhood (Nov 2017)
- `project_sql_result_07.csv` — Loop → O’Hare trips on Saturdays with weather label (`Bad`/`Good`)

---

## Exploratory Data Analysis (EDA)

### Trips by company (Nov 15–16, 2017)
Top companies by trip count:
- **Flash Cab:** 19,558  
- **Taxi Affiliation Services:** 11,422  
- **Medallion Leasing:** 10,367  
- **Yellow Cab:** 9,888  
- **Taxi Affiliation Service Yellow:** 9,299  

### Top 10 dropoff neighborhoods (Nov 2017)
1. Loop — 10,727.47  
2. River North — 9,523.67  
3. Streeterville — 6,664.67  
4. West Loop — 5,163.67  
5. O'Hare — 2,546.90  
6. Lake View — 2,420.97  
7. Grant Park — 2,068.53  
8. Museum Campus — 1,510.00  
9. Gold Coast — 1,364.23  
10. Sheffield & DePaul — 1,259.77  

---

## Hypothesis Testing (Welch t-test)

### Setup
- **Significance level:** α = 0.05  
- **Test:** Welch’s t-test (two independent samples, `equal_var=False`)  
- **Validation:** Saturday ratio = **1.0** (dataset contains only Saturdays)  
- **Cleaning:** removed non-positive durations (`duration_seconds > 0`): **1068 → 1062**

### Samples
- **Bad:** n = 180  
- **Good:** n = 882  

### Descriptive stats (duration in seconds)
- **Bad mean:** 2427.21 s  
- **Good mean:** 2013.28 s  
- **Difference (Bad − Good):** 413.93 s (~ **6.90 min**)  

### Test result
- **t-statistic:** 6.9793  
- **p-value:** 2.417e-11  

✅ **Conclusion:** Reject H₀. There is strong statistical evidence that trip duration differs under **Bad** vs **Good** weather, and trips are **longer on average** during bad weather.

---

## Repository contents
- `project_8.ipynb` — final notebook (SQL + Python EDA + hypothesis test)
- `eda.ipynb` — additional EDA notebook
- `zuber_chicago.py` — reproducible script to load data, generate summaries/plots, and run the hypothesis test

---

## How to run (Windows / VS Code)
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install pandas matplotlib scipy
python zuber_chicago.py