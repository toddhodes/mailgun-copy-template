import requests
import sys
import os
import json

MG_BASE_URL = os.environ.get('MG_BASE_URL', 'https://api.mailgun.net/v3')
MG_MAIL_DOMAIN = os.environ.get('MG_MAIL_DOMAIN', None)
MG_API_KEY = os.environ.get('MG_API_KEY', None)

def get_template_versions(name):
    url = f'{MG_BASE_URL}/{MG_MAIL_DOMAIN}/templates/{name}/versions'
    print(f"curl -u 'api:{MG_API_KEY}' '{url}'")
    r = requests.get(url, auth=('api', MG_API_KEY))
    if r.status_code == 200:
        # Some Mailgun accounts return {'template': {'versions': [...]}}
        # Some return {'versions': [...]}
        data = r.json()
        if 'template' in data and 'versions' in data['template']:
            return data['template']['versions']
        elif 'versions' in data:
            return data['versions']
        else:
            print(f"Unexpected response structure: {json.dumps(data)}")
            return None
    else:
        print(f"Failed to fetch template '{name}': {r.text}")
        return None

def get_version_content(template_name, version_id):
    url = f'{MG_BASE_URL}/{MG_MAIL_DOMAIN}/templates/{template_name}/versions/{version_id}'
    print(f"curl -u 'api:{MG_API_KEY}' '{url}'")
    r = requests.get(url, auth=('api', MG_API_KEY))
    if r.status_code == 200:
        data = r.json()
        # In most cases, the template body is under ['template']['template']
        # But print the response for debugging if missing
        if 'template' in data and 'template' in data['template']:
            return data['template']['template']
        else:
            print(f"Version content response missing 'template': {json.dumps(data)}")
            return None
    else:
        print(f"Failed to fetch version content '{version_id}' of template '{template_name}': {r.text}")
        return None

def create_template(name, description, template):
    r = requests.post(f'{MG_BASE_URL}/{MG_MAIL_DOMAIN}/templates', auth=('api', MG_API_KEY), data={
        'name': name,
        'description': description,
        'template': template
    })
    if r.status_code == 200 and r.json().get('message') == 'template has been stored':
        return r.json()['template']
    else:
        print(f"Failed to create template '{name}': {r.text}")
        return None

def print_template_versions_json(versions):
    print("Available versions (single-line JSON):")
    for v in versions:
        print(json.dumps(v, separators=(',', ':')))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage:')
        print('  python3 mailgun-copy-template.py <src> <dest> [version_tag]')
        print('  python3 mailgun-copy-template.py list-versions <src>')
        exit(1)
    elif MG_MAIL_DOMAIN is None or MG_API_KEY is None:
        print('Environment variables MG_MAIL_DOMAIN and MG_API_KEY are required.')
        exit(1)
    elif sys.argv[1] == 'list-versions':
        if len(sys.argv) != 3:
            print('Usage: python3 mailgun-copy-template.py list-versions <src>')
            exit(1)
        src_name = sys.argv[2]
        versions = get_template_versions(src_name)
        if versions:
            print_template_versions_json(versions)
        else:
            print("No versions found.")
        exit(0)
    else:
        src_name = sys.argv[1]
        dst_name = sys.argv[2] if len(sys.argv) > 2 else None
        version_tag = sys.argv[3] if len(sys.argv) > 3 else None

        if not dst_name:
            print('Destination template name required.')
            exit(1)

        versions = get_template_versions(src_name)
        if not versions:
            print("No versions found.")
            exit(1)

        if not version_tag:
            active_version = next((v for v in versions if v.get('active')), None)
            if active_version:
                version_tag = active_version['tag']
                print(f"No version_tag supplied, using active version: {version_tag}")
            else:
                version_tag = versions[0]['tag']
                print(f"No version_tag supplied and no active version found, using first version: {version_tag}")

        selected_version = next((v for v in versions if v['tag'] == version_tag), None)
        if not selected_version:
            print(f"Version '{version_tag}' not found.")
            exit(1)

        template_body = get_version_content(src_name, selected_version['id'])
        if not template_body:
            print(f"Could not retrieve template body for version '{version_tag}'.")
            exit(1)

        created = create_template(dst_name, selected_version.get('comment', ''), template_body)
        if created:
            print(f"Version '{version_tag}' from '{src_name}' copied to '{dst_name}' successfully.")
        else:
            print("Failed to copy template.")
