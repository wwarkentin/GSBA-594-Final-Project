"""Personal Peloton analytics. Run: python analyze_peloton.py --csv workouts.csv"""
from pathlib import Path
import argparse
import json
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.inspection import permutation_importance

RENAME = {'Workout Timestamp':'timestamp','Length (minutes)':'minutes',
          'Fitness Discipline':'discipline','Type':'type','Instructor Name':'instructor',
          'Title':'title','Avg. Watts':'watts','Total Output':'output_kj',
          'Avg. Resistance':'resistance','Avg. Cadence (RPM)':'cadence',
          'Avg. Heartrate':'heart_rate','Distance (mi)':'miles','Calories Burned':'calories'}

def load_data(path):
    """Keep local wall-clock dates: offsets and PST/PDT suffixes vary in export."""
    raw = pd.read_csv(path)
    df = raw.rename(columns=RENAME).copy()
    required = {'timestamp','minutes','discipline','type','watts','instructor'}
    if required - set(df):
        raise ValueError(f'Missing required columns: {sorted(required-set(df))}')
    # Strip only trailing timezone annotations; retain local day and hour.
    df['date'] = pd.to_datetime(df.timestamp.astype(str).str.replace(
        r'\s*\([^)]*\)\s*$', '', regex=True), errors='coerce')
    for col in ['minutes','watts','output_kj','resistance','cadence','heart_rate','miles','calories']:
        if col in df:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace('%','',regex=False),errors='coerce')
            df.loc[df[col] < 0, col] = np.nan
    audit = {'input_rows':len(df), 'exact_duplicate_rows':int(raw.duplicated().sum()),
             'invalid_dates':int(df.date.isna().sum()),
             'invalid_durations':int((df.minutes.isna() | df.minutes.le(0)).sum()),
             'timestamp_policy':'Local wall-clock time; timezone suffix removed, no UTC conversion.'}
    df = df.drop_duplicates().dropna(subset=['date','minutes'])
    df = df[df.minutes > 0].sort_values('date').reset_index(drop=True)
    for col in ['type','instructor','discipline']:
        df[col] = df[col].fillna('Unknown')
    audit['retained_rows'] = len(df)
    return df, audit, raw.isna().mean().rename('missing_fraction')

def savefig(out, name):
    plt.tight_layout()
    plt.savefig(out/name, dpi=160, bbox_inches='tight')
    plt.close()

def descriptive(df, out):
    """All activities for consistency; main cycling rides for performance."""
    weekly = df.set_index('date').resample('W-SUN').agg(
        workouts=('minutes','size'), minutes=('minutes','sum'))
    weekly.index.name = 'week_ending'
    weekly.to_csv(out/'weekly_training.csv')
    mix = df.groupby('discipline').agg(workouts=('minutes','size'), minutes=('minutes','sum'))
    mix.to_csv(out/'activity_summary.csv')
    fig, axes = plt.subplots(2,1,figsize=(11,6),sharex=True)
    weekly.workouts.plot(ax=axes[0], color='#176B87',title='Training consistency — all logged activities')
    axes[0].set_ylabel('Sessions / week')
    weekly.minutes.plot(ax=axes[1],color='#D77A28')
    axes[1].set_ylabel('Logged minutes / week')
    axes[1].set_xlabel('Week ending (first and last weeks may be partial)')
    savefig(out,'01_consistency.png')
    mix.minutes.sort_values().plot.barh(figsize=(9,5),color='#176B87',title='Logged minutes by activity')
    plt.xlabel('Minutes (includes meditation and stretching)')
    savefig(out,'02_activity_mix.png')
    cycling = df[df.discipline.eq('Cycling')].copy()
    # Short rides and explicit warm-up / cool-down types are excluded, not deleted.
    main = cycling[(cycling.minutes >= 15) & ~cycling.type.str.contains(
        r'warm|cool',case=False,regex=True) & cycling.watts.gt(0)].copy()
    main.groupby(['minutes','type']).watts.agg(['count','mean','median','std']).to_csv(out/'comparable_ride_groups.csv')
    fig, ax = plt.subplots(figsize=(11,5))
    for duration in main.minutes.value_counts().head(4).index.sort_values():
        group = main[main.minutes.eq(duration)]
        ax.scatter(group.date,group.watts,s=13,alpha=.25)
        smooth = group.set_index('date').watts.rolling('90D',min_periods=3).median()
        ax.plot(smooth.index,smooth,label=f'{duration:g} min (n={len(group)})')
    ax.set(title='Main rides: average output by duration',ylabel='Average watts',xlabel='Date')
    ax.legend(title='Lines: trailing 90-day median')
    savefig(out,'03_cycling_performance.png')
    main.groupby('instructor').watts.agg(['count','mean','median']).sort_values('count',ascending=False).to_csv(out/'instructor_summary.csv')
    main.to_csv(out/'main_cycling_rides.csv',index=False)
    return main

def make_features(df, main):
    """Past-only features. Exclude ALL current-day outcomes for same-day safety."""
    days = pd.date_range(df.date.min().normalize(),df.date.max().normalize(),freq='D')
    daily = df.groupby(df.date.dt.normalize()).agg(
        minutes=('minutes','sum'), sessions=('minutes','size')) .reindex(days,fill_value=0)
    features = pd.DataFrame(index=days)
    for window in [7,28]:
        features[f'prior_{window}d_minutes'] = daily.minutes.shift(1).rolling(window,min_periods=1).sum().fillna(0)
        features[f'prior_{window}d_sessions'] = daily.sessions.shift(1).rolling(window,min_periods=1).sum().fillna(0)
    perf = main.groupby(main.date.dt.normalize()).watts.agg(['sum','count']).reindex(days,fill_value=0)
    features['prior_28d_watts'] = (perf['sum'].shift(1).rolling(28,min_periods=1).sum() /
                                   perf['count'].shift(1).rolling(28,min_periods=1).sum().replace(0,np.nan))
    rides = main.copy()
    rides['day'] = rides.date.dt.normalize()
    rides = rides.join(features,on='day')
    rides['weekday'] = rides.date.dt.dayofweek.astype(str)
    rides['hour'] = rides.date.dt.hour
    rides['elapsed_days'] = (rides.day - days.min()).dt.days
    return rides

def model_analysis(rides,out):
    """Fixed models; chronological holdout is evaluation, never model tuning."""
    unique_days = sorted(rides.day.unique())
    if len(rides)<80 or len(unique_days)<30:
        return {'status':'Skipped: fewer than 80 main rides or 30 distinct days.'}
    cutoff = unique_days[int(len(unique_days)*.8)]
    train,test = rides[rides.day<cutoff],rides[rides.day>=cutoff]
    numeric = ['minutes','hour','elapsed_days','prior_7d_minutes','prior_28d_minutes',
               'prior_7d_sessions','prior_28d_sessions','prior_28d_watts']
    categorical = ['type','instructor','weekday']
    cols = numeric+categorical
    def preprocessing():
        return ColumnTransformer([
            ('numeric',make_pipeline(SimpleImputer(strategy='median',keep_empty_features=True),StandardScaler()),numeric),
            ('category',OneHotEncoder(handle_unknown='ignore',sparse_output=False),categorical)])
    estimators = {'Training mean baseline':DummyRegressor(strategy='mean'),
                  'Ridge regression':Ridge(alpha=10),
                  'Random forest':RandomForestRegressor(n_estimators=200,min_samples_leaf=8,
                       max_depth=8,random_state=42,n_jobs=-1)}
    scores=[]
    predictions=test[['date','minutes','type','watts']].copy()
    for name,estimator in estimators.items():
        pipeline=make_pipeline(preprocessing(),estimator)
        pipeline.fit(train[cols],train.watts)
        pred=pipeline.predict(test[cols])
        predictions[name]=pred
        scores.append({'model':name,'MAE_watts':mean_absolute_error(test.watts,pred),
                       'RMSE_watts':np.sqrt(mean_squared_error(test.watts,pred)),
                       'R2':r2_score(test.watts,pred)})
        if name=='Random forest':
            importance=permutation_importance(pipeline,test[cols],test.watts,
                scoring='neg_mean_absolute_error',n_repeats=10,random_state=42,n_jobs=1)
            imp=pd.DataFrame({'feature':cols,'MAE_increase':importance.importances_mean,
                              'repeat_std':importance.importances_std}).sort_values('MAE_increase')
            imp.to_csv(out/'permutation_importance.csv',index=False)
            plt.figure(figsize=(9,6))
            plt.barh(imp.feature,imp.MAE_increase,xerr=imp.repeat_std,color='#176B87')
            plt.xlabel('Increase in holdout MAE after shuffling feature (watts)')
            plt.title('Random forest: exploratory predictive importance')
            savefig(out,'05_predictive_importance.png')
    scores=pd.DataFrame(scores)
    scores.to_csv(out/'model_scores.csv',index=False)
    predictions.to_csv(out/'holdout_predictions.csv',index=False)
    fig,axes=plt.subplots(1,3,figsize=(13,4),sharex=True,sharey=True)
    for ax,name in zip(axes,estimators):
        ax.scatter(test.watts,predictions[name],alpha=.6,s=18)
        low=min(test.watts.min(),predictions[name].min())
        high=max(test.watts.max(),predictions[name].max())
        ax.plot([low,high],[low,high],'k--',lw=1)
        ax.set(title=name,xlabel='Actual watts',ylabel='Predicted watts')
    savefig(out,'04_prediction_comparison.png')
    return {'status':'Completed','train_rides':len(train),'test_rides':len(test),
            'holdout_start':str(pd.Timestamp(cutoff).date()),'scores':scores.to_dict('records')}

def run(csv_path,output_dir='results'):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'axes.spines.top':False,'axes.spines.right':False,'font.size':10})
    df,audit,missing=load_data(csv_path)
    missing.to_csv(out/'source_missingness.csv')
    main=descriptive(df,out)
    rides=make_features(df,main)
    model=model_analysis(rides,out)
    summary={'start':str(df.date.min()),'end':str(df.date.max()),'workouts':len(df),
             'cycling_workouts':int(df.discipline.eq('Cycling').sum()),'main_rides':len(main),
             'logged_hours':round(float(df.minutes.sum()/60),1),'audit':audit,'model':model}
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    notes='''# Interpretation notes
- Minutes are exported session lengths, not verified active time. Meditation is included in overall logged activity.
- Missing cycling metrics for other disciplines are structural; they are not filled with zero.
- Warm-ups/cool-downs and rides under 15 minutes are excluded from the performance models.
- Duration/type groups improve comparability but do not control for effort, equipment, illness, or class difficulty.
- Historical performance is descriptive; rising watts alone does not establish physiological fitness gains.
- All lagged features exclude current-day data. Later holdout rides can use completed earlier holdout days, matching sequential one-ride-ahead use.
- The latest 20% of distinct ride days is held out. Models have fixed settings; no tuning on this holdout.
- Baseline predicts the training-set mean. Lower MAE/RMSE is better; negative R2 means worse than the test-set mean.
- Permutation importance is exploratory prediction evidence, not a causal effect. Correlated features can share importance.
- No heart rate, current-ride cadence/resistance, distance, calories, or total output enters the prediction model.
- Average watts and total output are mathematically related; using one to predict the other would leak the target.
- No weight records, recovery ratings, FTP tests, or clinical measures are provided. This project cannot attribute weight loss or prescribe training intensity.
- Timestamp timezone labels are removed to retain exported local dates, without asserting a home timezone.
- Recent training totals are bounded by this export; early historical windows are incomplete.
'''
    (out/'interpretation_notes.md').write_text(notes,encoding='utf-8')
    print(json.dumps(summary,indent=2))
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv',type=Path,default=Path(__file__).with_name('workouts.csv'))
    parser.add_argument('--out',type=Path,default=Path(__file__).with_name('results'))
    args=parser.parse_args()
    run(args.csv,args.out)
