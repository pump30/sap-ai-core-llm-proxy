import requests
import json
import base64
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load service key
with open('sap-ai-key.json', 'r') as f:
    key_data = json.load(f)

# Get OAuth token
token_url = key_data['url'] + '/oauth/token'
auth_string = f"{key_data['clientid']}:{key_data['clientsecret']}"
encoded_auth = base64.b64encode(auth_string.encode()).decode()

token_response = requests.post(
    token_url,
    data={'grant_type': 'client_credentials'},
    headers={'Authorization': f'Basic {encoded_auth}'},
    timeout=30
)
token_response.raise_for_status()
access_token = token_response.json()['access_token']

base_url = key_data.get('serviceurls', {}).get('AI_API_URL') or key_data.get('base_url')

print("=" * 60)
print("SAP AI Core - Deployed vs Deployable Models")
print("=" * 60)

# 1. Get deployed models
print("\n1. Deployed Models (RUNNING):")
print("-" * 40)
deployments_response = requests.get(
    f'{base_url}/v2/lm/deployments',
    headers={
        'Authorization': f'Bearer {access_token}',
        'AI-Resource-Group': 'default'
    },
    timeout=60
)
deployments = deployments_response.json()

deployed_models = set()
for dep in deployments.get('resources', []):
    if dep.get('status') == 'RUNNING':
        model_info = dep.get('details', {}).get('resources', {}).get('backend_details', {}).get('model', {})
        model_name = model_info.get('name', 'unknown')
        deployed_models.add(model_name)
        print(f"  [DEPLOYED] {model_name}")

print(f"\nTotal deployed: {len(deployed_models)}")

# 2. Get all configurations (deployable models)
print("\n2. All Deployable Configurations:")
print("-" * 40)
configs_response = requests.get(
    f'{base_url}/v2/lm/configurations',
    headers={
        'Authorization': f'Bearer {access_token}',
        'AI-Resource-Group': 'default'
    },
    timeout=60
)
configs = configs_response.json()

# Group by model name
config_models = {}
for config in configs.get('resources', []):
    config_name = config.get('name', '')
    exec_id = config.get('executableId', '')
    
    # Try to extract model name from parameters
    model_name = None
    for param in config.get('parameterBindings', []):
        if param.get('key') == 'modelName':
            model_name = param.get('value')
            break
    
    if model_name:
        if model_name not in config_models:
            config_models[model_name] = {'configs': [], 'executable': exec_id}
        config_models[model_name]['configs'].append(config_name)

# Categorize
image_models = []
text_models = []
other_models = []

for model_name, info in config_models.items():
    lower_name = model_name.lower()
    status = "[Y]" if model_name in deployed_models else "[N]"
    
    if any(x in lower_name for x in ['dall', 'image', 'stable', 'sdxl']):
        image_models.append((model_name, info['executable'], status))
    elif any(x in lower_name for x in ['embed', 'ada-002']):
        other_models.append((model_name, info['executable'], status))
    else:
        text_models.append((model_name, info['executable'], status))

print("\n[IMAGE] Image Models:")
if image_models:
    for m, e, s in sorted(image_models):
        print(f"  {s} {m} ({e})")
else:
    print("  (No image models available)")

print("\n[TEXT] Text Models:")
for m, e, s in sorted(text_models)[:30]:
    print(f"  {s} {m} ({e})")
if len(text_models) > 30:
    print(f"  ... and {len(text_models) - 30} more")

print("\n[EMBED] Embedding/Other Models:")
for m, e, s in sorted(other_models):
    print(f"  {s} {m} ({e})")

print("\n" + "=" * 60)
print("Summary:")
print(f"  - Deployed models: {len(deployed_models)}")
print(f"  - Deployable configs: {len(config_models)}")
not_deployed = [m for m in config_models if m not in deployed_models]
print(f"  - Not deployed but deployable: {len(not_deployed)}")
print("=" * 60)
