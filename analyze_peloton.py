"""Connected fitness performance prediction using a masked feature release.
Run: python analyze_peloton.py
Original measurements, exact dates and conversion keys are not distributed.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT=Path(__file__).resolve().parent
NUMERIC=['planned_duration_index','start_time_index','elapsed_time_index',
 'exercise_7d_index','exercise_28d_index','exercise_days_7d_index','recent_output_index']
CATEGORICAL=['class_type','instructor_code','weekday_code']
FEATURES=NUMERIC+CATEGORICAL
TARGET='output_index'
CANDIDATES=['Training mean','Class group mean','Recent 28-day mean','Ridge regression','Random forest']


def load_data(path=ROOT/'data/model_features.csv'):
    df=pd.read_csv(path).sort_values('day_index',kind='stable').reset_index(drop=True)
    required={'ride_id','day_index',TARGET,*FEATURES}
    if required-set(df):raise ValueError(f'Missing columns: {sorted(required-set(df))}')
    if df.ride_id.duplicated().any() or df[TARGET].isna().any():
        raise ValueError('Ride IDs must be unique and the target must be observed.')
    return df


def make_pipeline_for(name):
    preprocessing=ColumnTransformer([
      ('numeric',make_pipeline(SimpleImputer(strategy='median',keep_empty_features=True),StandardScaler()),NUMERIC),
      ('categorical',OneHotEncoder(handle_unknown='ignore',sparse_output=False),CATEGORICAL)])
    estimator=Ridge(alpha=10) if name=='Ridge regression' else RandomForestRegressor(
      n_estimators=150,max_depth=8,min_samples_leaf=8,random_state=42,n_jobs=-1)
    return make_pipeline(preprocessing,estimator)


def predict(name,train,test):
    mean=float(train[TARGET].mean())
    if name=='Training mean':return np.repeat(mean,len(test))
    if name=='Recent 28-day mean':return test.recent_output_index.fillna(mean).to_numpy()
    if name=='Class group mean':
        group=train.groupby(['planned_duration_index','class_type'])[TARGET].mean()
        return np.array([group.get((r.planned_duration_index,r.class_type),mean) for r in test.itertuples()])
    model=make_pipeline_for(name).fit(train[FEATURES],train[TARGET])
    return model.predict(test[FEATURES])


def scores(y,pred):
    return {'MAE_index':float(mean_absolute_error(y,pred)),
       'RMSE_index':float(np.sqrt(mean_squared_error(y,pred))),
       'R2':float(r2_score(y,pred)),
       'bias_index':float(np.mean(pred-np.asarray(y)))}


def development_cv(data):
    days=np.array(sorted(data.day_index.unique()))
    rows=[]
    for fold,(a,b) in enumerate(TimeSeriesSplit(n_splits=3).split(days),1):
        train=data[data.day_index.isin(days[a])];valid=data[data.day_index.isin(days[b])]
        for name in CANDIDATES:
            prediction=predict(name,train,valid)
            rows.append({'fold':fold,'model':name,'train_rides':len(train),'validation_rides':len(valid),
              'train_end_day':int(train.day_index.max()),'validation_start_day':int(valid.day_index.min()),
              'validation_end_day':int(valid.day_index.max()),**scores(valid[TARGET],prediction)})
    return pd.DataFrame(rows)


def split(data):
    days=sorted(data.day_index.unique());cutoff=days[int(.8*len(days))]
    return data[data.day_index<cutoff],data[data.day_index>=cutoff]


def run(out=ROOT/'results'):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    data=load_data();train,test=split(data)
    cv=development_cv(train);cv.to_csv(out/'development_cv_folds.csv',index=False)
    ranking=cv.groupby('model').MAE_index.agg(['mean','std']).sort_values('mean')
    ranking.to_csv(out/'development_cv_summary.csv')
    selected=ranking.index[0]
    results=[];predictions=test[['ride_id','day_index',TARGET]].copy()
    for name in CANDIDATES:
        pred=predict(name,train,test);predictions[name]=pred
        results.append({'model':name,'selected_by_development_cv':name==selected,**scores(test[TARGET],pred)})
    result=pd.DataFrame(results)
    baseline=float(result.loc[result.model.eq('Training mean'),'MAE_index'].iloc[0])
    result['MAE_improvement_vs_training_mean_percent']=(baseline-result.MAE_index)/baseline*100
    result.to_csv(out/'model_scores.csv',index=False);predictions.to_csv(out/'evaluation_predictions.csv',index=False)
    sensitivity=pd.read_csv(ROOT/'data/sensitivity_groups.csv')
    cases=[]
    for col,label in [('longer_class','Longer-class subset'),('recent_development','Recent development window')]:
        ids=sensitivity.loc[sensitivity[col],'ride_id']
        subset=train[train.ride_id.isin(ids)]
        table=development_cv(subset).groupby('model').MAE_index.mean().reset_index()
        table['scenario']=label;table['development_rides']=len(subset);cases.append(table)
    pd.concat(cases).to_csv(out/'development_sensitivity.csv',index=False)
    ax=result.set_index('model').MAE_index.sort_values().plot.barh(figsize=(10,5),color='#126B82')
    ax.set(title='Later-period prediction error',xlabel='MAE in output-index units (lower is better)')
    plt.tight_layout();plt.savefig(out/'model_errors.png',dpi=160);plt.close()
    fig,axes=plt.subplots(1,2,figsize=(11,4.5))
    for ax,name in zip(axes,['Ridge regression','Random forest']):
        ax.scatter(test[TARGET],predictions[name],alpha=.65,s=20,color='#126B82')
        lo=min(test[TARGET].min(),predictions[name].min());hi=max(test[TARGET].max(),predictions[name].max())
        ax.plot([lo,hi],[lo,hi],'k--',lw=1);ax.set(title=name,xlabel='Observed output index',ylabel='Predicted output index')
    plt.tight_layout();plt.savefig(out/'prediction_comparison.png',dpi=160);plt.close()
    trends=pd.read_csv(ROOT/'data/activity_trends.csv')
    fig,ax=plt.subplots(figsize=(11,4.5))
    for col in ['exercise_minutes_index','mobility_minutes_index','mindfulness_minutes_index']:
        ax.plot(trends.relative_week,trends[col],label=col.replace('_index','').replace('_',' '),alpha=.8)
    ax.set(title='Indexed logged activity over relative time',xlabel='Relative week',ylabel='Activity index (within-series standardized)');ax.legend()
    plt.tight_layout();plt.savefig(out/'activity_trends.png',dpi=160);plt.close()
    summary={'model_rides':len(data),'development_rides':len(train),'evaluation_rides':len(test),
      'selected_by_development_cv':selected,'lowest_later_period_MAE':result.sort_values('MAE_index').iloc[0].model,
      'evaluation_status':'Exploratory later-period comparison, previously inspected. No new blind test claimed.',
      'output_unit':'Masked output index, not original power units.',
      'privacy':'Data minimization and masking reduce exposure but are not guaranteed anonymization.'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    print(result.to_string(index=False));return data,result,summary

if __name__=='__main__':run()
