import requests

BASE = 'http://127.0.0.1:8000/api'

# 1. Register a new user
register = requests.post(f'{BASE}/auth/register/', json={
    'username': 'testuser2',
    'email': 'testuser2@example.com',
    'password': 'test123'
})
print('Register:', register.status_code, register.json())

# 2. Login with the new user
login = requests.post(f'{BASE}/auth/token/', json={
    'username': 'testuser2',
    'password': 'test123'
})
print('Login:', login.status_code, login.json())
token = login.json().get('access')

# 3. Create a lead as the new user
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
lead = requests.post(f'{BASE}/leads/', headers=headers, json={
    'name': 'Test Lead',
    'company': 'Test Company',
    'status': 'new'
})
print('Create lead:', lead.status_code, lead.json())

# 4. List leads for this user
leads = requests.get(f'{BASE}/leads/', headers=headers)
print('List leads:', leads.status_code, leads.json())
