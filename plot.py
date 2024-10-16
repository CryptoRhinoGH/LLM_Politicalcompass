import matplotlib.pyplot as plt
import pandas as pd
import re

# Function to extract economic and social scores from the string format 'ec=x, soc=y'
def extract_ec_soc(value):
    match = re.search(r'ec=(-?\d+\.\d+), soc=(-?\d+\.\d+)', value)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

# Extracting scores for the Gemini, GPT, and Perplexity datasets
def process_trial_data(df, model_name):
    trial_data = []
    for index, row in df.iterrows():
        for col in ['Far Left', 'Middle', 'Far Right']:
            if pd.notnull(row[col]):
                ec, soc = extract_ec_soc(row[col])
                trial_data.append({
                    'Model': model_name,
                    'Trial': row['Language'] if 'Trial' in row['Language'] else None,
                    'Political View': col,
                    'Economic Score': ec,
                    'Social Score': soc
                })
    return pd.DataFrame(trial_data)

# Load the uploaded CSV files
gemini_data = pd.read_csv('csv_results/gemini_cookie_results.csv')
gpt_data = pd.read_csv('csv_results/gpt_cookie_results.csv')
perplexity_data = pd.read_csv('csv_results/perplexity_cookie_results.csv')

# Process each dataset
gemini_processed = process_trial_data(gemini_data, 'Gemini')
gpt_processed = process_trial_data(gpt_data, 'GPT')
perplexity_processed = process_trial_data(perplexity_data, 'Perplexity')

# Combine all the processed data
combined_data = pd.concat([gemini_processed, gpt_processed, perplexity_processed], ignore_index=True)

# Calculate averages and standard deviations for each model and political view
grouped_combined = combined_data.groupby(['Model', 'Political View']).agg({
    'Economic Score': ['mean', 'std'],
    'Social Score': ['mean', 'std']
}).reset_index()

# Define the improved color palette
improved_colors = ['#FF5733', '#33FF57', '#3357FF']

# Plotting function for all models and political views
def create_avg_plot_combined(data, model_names, colors):
    plt.figure(figsize=(10, 8))
    for idx, model_name in enumerate(model_names):
        model_data = data[data['Model'] == model_name]
        views = model_data['Political View'].values
        econ_scores_mean = model_data[('Economic Score', 'mean')].values
        soc_scores_mean = model_data[('Social Score', 'mean')].values
        econ_scores_std = model_data[('Economic Score', 'std')].values
        soc_scores_std = model_data[('Social Score', 'std')].values

        for i, view in enumerate(views):
            plt.errorbar(econ_scores_mean[i], soc_scores_mean[i],
                         xerr=econ_scores_std[i], yerr=soc_scores_std[i],
                         fmt='o', color=colors[idx % len(colors)], capsize=5,
                         label=f'{model_name} - {view}: ({econ_scores_mean[i]:.2f}, {soc_scores_mean[i]:.2f}) ± ({econ_scores_std[i]:.2f}, {soc_scores_std[i]:.2f})')

    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.xlim(-10, 10)
    plt.ylim(-10, 10)
    plt.title('Averaged Economic and Social Scores for All Models and Political Views')
    plt.xlabel('Economic Score (Left: -10 to Right: +10)')
    plt.ylabel('Social Score (Libertarian: -10 to Authoritarian: +10)')
    plt.grid(True)
    plt.legend(loc='upper right', fontsize='small')
    plt.show()

# Generate the plot for all the models (Gemini, GPT, Perplexity)
create_avg_plot_combined(grouped_combined, ['Gemini', 'GPT', 'Perplexity'], improved_colors)
