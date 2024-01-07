import pickle

with open('companies.pkl', 'rb') as f:
    companies = pickle.load(f)

with open('urls.pkl', 'rb') as f:
    urls = pickle.load(f)
