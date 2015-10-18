import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy
import scipy.stats
import statsmodels.api as sm
from ggplot import *


# For all problems we work with the improved dataset

turnstile_data=pd.read_csv("turnstile_weather_v2.csv")

'''
# P R O B L E M  S E T  3.1
# E X P L O R A T O R Y  D A T A  A N A L Y S I S  -  H I S T O G R A M 
'''

def entries_histogram(turnstile_weather):
    plt.figure()
    turnstile_weather['ENTRIESn_hourly'][turnstile_weather['rain']==0].\
    hist(bins=100,stacked=True,color='g', alpha=0.7,label='No Rain')
    turnstile_weather['ENTRIESn_hourly'][turnstile_weather['rain']==1].\
    hist(bins=100,stacked=True,color='b', alpha=0.4,label='Rain')
    plt.title("Hourly Entries by weather conditions (rain/no rain)")
    plt.xlabel("Hourly Entries")
    plt.xlim([0,10000])
    plt.ylabel("Frequency")
    plt.legend()
    return plt

plot = entries_histogram(turnstile_data)
plot.savefig("histogram_rain.png")

# Alternatively we can get some summary statistics

turnstile_data_rain=turnstile_data[["rain", "ENTRIESn_hourly"]]
turnstile_data_rain["rain_string"] = \
np.where(turnstile_data_rain["rain"] == 1, "raining", "not raining")
turnstile_data_rain.groupby("rain_string").describe()


'''
# P R O B L E M  S E T  3.2
# M A N N - W H I T N E Y  U  T E S T 
'''

def mann_whitney_plus_means(turnstile_weather):
    entries_rain=turnstile_weather['ENTRIESn_hourly'][turnstile_weather['rain']==1]
    entries_norain=turnstile_weather['ENTRIESn_hourly'][turnstile_weather['rain']==0]
    with_rain_mean=np.mean(entries_rain)
    without_rain_mean=np.mean(entries_norain)
    U,p=scipy.stats.mannwhitneyu(entries_rain,entries_norain)
    m_u=len(entries_rain)*len(entries_norain)/2
    sigma_u = np.sqrt(len(entries_rain)*len(entries_norain)*(len(entries_rain)+len(entries_norain)+1)/12)
    z=(U-m_u)/sigma_u
    p=2*(1-scipy.stats.norm.cdf(np.absolute(z)))      
    return with_rain_mean, without_rain_mean, U, p 


print mann_whitney_plus_means(turnstile_data)

 

'''
# P R O B L E M  S E T  3.3
# L I N E A R  R E G R E S S I O N - G R A D I E N T  D E S C E N T
'''
 
def normalize_features(array):
   array_normalized = (array-array.mean())/array.std()
   mu = array.mean()
   sigma = array.std()
   return array_normalized, mu, sigma

def compute_cost(features, values, theta):
    m = len(values)
    sse = np.square(np.dot(features, theta) - values).sum()
    cost = sse / (2*m)
    return cost

def gradient_descent(features, values, theta, alpha, num_iterations):
    cost_history=[]
    m=len(values)
    for i in range(num_iterations):
        cost_history=cost_history+[compute_cost(features,values,theta)]
        theta=theta-alpha/m*np.dot(np.dot(features,theta)-values, features)
    return theta, pd.Series(cost_history)
    

def predictions(dataframe):
    # Select Features (try different features!)
    dataframe['weekdayrain']=dataframe['weekday']*dataframe['rain']
    features = dataframe[['rain','weekday','weekdayrain','meantempi']]
    # Add UNIT to features using dummy variables
    dummy_units = pd.get_dummies(dataframe['UNIT'], prefix='unit')
    dummy_units=dummy_units.drop('unit_R012',1)
    dummy_hour = pd.get_dummies(turnstile_data['hour'], prefix='hour')
    dummy_hour=dummy_hour.drop('hour_0',1)
    features = features.join(dummy_units)
    features = features.join(dummy_hour)
    # Values
    values = dataframe['ENTRIESn_hourly']
    m = len(values)
    features, mu, sigma = normalize_features(features)
    features['ones'] = np.ones(m) # Add a column of 1s (y intercept)
    # Convert features and values to numpy arrays
    features_array = np.array(features)
    values_array = np.array(values)
    # Set values for alpha, number of iterations.
    alpha = 0.1 # please feel free to change this value
    num_iterations = 75 # please feel free to change this value
    # Initialize theta, perform gradient descent
    theta_gradient_descent = np.zeros(len(features.columns))
    theta_gradient_descent, cost_history = gradient_descent(features_array, 
                                                            values_array, 
                                                            theta_gradient_descent, 
                                                            alpha, 
                                                            num_iterations)
    plot = None
    # -------------------------------------------------
    # Uncomment the next line to see your cost history
    # -------------------------------------------------
    plot = plot_cost_history(alpha, cost_history)
    # 
    # Please note, there is a possibility that plotting
    # this in addition to your calculation will exceed 
    # the 30 second limit on the compute servers.
    
    predictions = np.dot(features_array, theta_gradient_descent)
    return predictions, plot


def plot_cost_history(alpha, cost_history):
   cost_df = pd.DataFrame({
      'Cost_History': cost_history,
      'Iteration': range(len(cost_history))
   })
   return ggplot(cost_df, aes('Iteration', 'Cost_History')) + \
      geom_point() + ggtitle('Cost History for alpha = %.3f' % alpha )

print predictions(turnstile_data)


'''
# P R O B L E M  S E T  3.4
# P L O T T I N G  R E S I D U A L S
'''

def plot_residuals(turnstile_weather, predictions):
    plt.figure()
    (turnstile_weather['ENTRIESn_hourly'] - predictions).hist()
    plt.title('Residual Plot')
    plt.xlabel('Residuals')
    plt.ylabel('Frequency')
    plt.ylim(0,36000)
    return plt

print plot_residuals(turnstile_data, predictions(turnstile_data)[0])
plot.savefig("histogram_residuals.png")

'''
The underlying assumption is that the residuals (i.e.) are normally and independently distributed with a mean
of 0 and some constant variance.
Basically the model should predict values higher than actual and lower than actual with equal likelihood.
Moreover, the level of the error should be independent of when the observation occured.

The Histogram of the Residual can be used to check whether the variance and also the error is normally 
distributed. A symmetric bell-shaped histogram which is evenly distributed around zero indicates 
that the normality assumption is likely to be true. If the histogram indicates that random error 
is not normally distributed, it suggests that the model's underlying assumptions may have been violated.
Our model predicts the higher values more likely

'''
turnstile_data['residuals']=turnstile_data["ENTRIESn_hourly"]-predictions(turnstile_data)[0]

(k2, pvalue) = scipy.stats.normaltest(turnstile_data["residuals"])
print k2, pvalue

# Null hypothesis can be rejected. The data are not normal.


'''
# P R O B L E M  S E T  3.5
# C O M P U T I N G  R  S Q U A R E D
'''

def compute_r_squared(data, predictions):
    sse=np.square(predictions-data).sum()
    sst=np.square(data-data.mean()).sum()
    r_squared=1-sse/sst
    return r_squared

print compute_r_squared(turnstile_data['ENTRIESn_hourly'], predictions(turnstile_data)[0])


'''
# P R O B L E M  S E T  3.6
# C O M P U T I N G  R  S Q U A R E D
'''
'''
One of the advantages of the statsmodels implementation is that it gives you
easy access to the values of the coefficients theta. This can help you infer relationships 
between variables in the dataset.
'''

def predictions_ols(weather_turnstile):
    values=weather_turnstile['ENTRIESn_hourly']
    m=len(values)
    weather_turnstile['weekdayrain']=weather_turnstile['weekday']*weather_turnstile['rain']
    features = weather_turnstile[['rain','weekday','weekdayrain','meantempi']]
    features['ones'] = np.ones(m)
    dummy_hour = pd.get_dummies(weather_turnstile['hour'], prefix='hour')
    dummy_hour=dummy_hour.drop('hour_0',1)
    dummy_units = pd.get_dummies(weather_turnstile['UNIT'], prefix='unit')
    dummy_units=dummy_units.drop('unit_R012',1)
    features = features.join(dummy_units)
    features = features.join(dummy_hour)
    model = sm.OLS(values, features).fit(use_correction=True,use_t=True)
    new=model.get_robustcov_results(cov_type='HAC',maxlags=1)
    return new.predict(features), new.summary()

print predictions_ols(turnstile_data)








































