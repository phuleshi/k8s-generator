import os
import sys
import subprocess
import json
import urllib.request
import urllib.parse
import urllib.error
from flask import Flask, request, jsonify, send_from_directory

# Add workspace directory to python path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from generate_k8s import ServiceSpec, write_all

app = Flask(__name__, static_folder='web')

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('web', path)

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.json or {}
    project = data.get('project', '').strip() or 'b2b'
    raw_services = data.get('services', [])
    
    if isinstance(raw_services, str):
        # If passed as comma-separated string
        services_list = [s.strip() for s in raw_services.split(',') if s.strip()]
    elif isinstance(raw_services, list):
        services_list = [s.strip() for s in raw_services if s.   strip()]
    else:
        services_list = []
        
    if not services_list:
        return jsonify({'error': 'Vui lòng nhập ít nhất một tên dịch vụ.'}), 400
        
    try:
        # Advanced parameters
        domain = data.get('domain', '').strip() or 'demo.baokim.vn'
        registry = data.get('registry', '').strip() or f"harbor.baokim.vn/{project}"
        image_tag = data.get('image_tag', '').strip() or 'latest'
        
        port_raw = data.get('port')
        port = int(port_raw) if port_raw is not None and str(port_raw).isdigit() else 80
        
        namespace = data.get('namespace', '').strip() or None
        
        rep_min_raw = data.get('replicas_min')
        replicas_min = int(rep_min_raw) if rep_min_raw is not None and str(rep_min_raw).isdigit() else 1
        
        rep_max_raw = data.get('replicas_max')
        replicas_max = int(rep_max_raw) if rep_max_raw is not None and str(rep_max_raw).isdigit() else 2
        
        cpu_request = data.get('cpu_request', '').strip() or '200m'
        mem_request = data.get('mem_request', '').strip() or '256Mi'
        mem_limit = data.get('mem_limit', '').strip() or '1Gi'
        
        needs_logs_volume = bool(data.get('needs_logs_volume', False))
        enable_autoscale = bool(data.get('enable_autoscale', True))
        
        extra_env_keys_raw = data.get('extra_env_keys', '')
        if isinstance(extra_env_keys_raw, str):
            extra_env_keys = [k.strip() for k in extra_env_keys_raw.split(',') if k.strip()]
        elif isinstance(extra_env_keys_raw, list):
            extra_env_keys = [k.strip() for k in extra_env_keys_raw if k.strip()]
        else:
            extra_env_keys = []

        # Build ServiceSpec instances
        services = []
        for name in services_list:
            services.append(ServiceSpec(
                name=name,
                project=project,
                image_tag=image_tag,
                port=port,
                replicas_min=replicas_min,
                replicas_max=replicas_max,
                cpu_request=cpu_request,
                mem_request=mem_request,
                mem_limit=mem_limit,
                needs_logs_volume=needs_logs_volume,
                enable_autoscale=enable_autoscale,
                domain=domain,
                registry=registry,
                namespace=namespace,
                extra_env_keys=extra_env_keys
            ))
            
        # Run generation logic
        outdir_path = os.path.abspath(f"./{project}")
        write_all(services, outdir_path)
        
        # Read the generated files from output directory
        generated_files = []
        if os.path.exists(outdir_path):
            for fn in sorted(os.listdir(outdir_path)):
                if fn.endswith(('.yaml', '.yml')):
                    file_path = os.path.join(outdir_path, fn)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    generated_files.append({
                        'name': fn,
                        'content': content
                    })
                    
        return jsonify({
            'success': True,
            'project': project,
            'outdir': outdir_path,
            'files': generated_files
        })
        
    except Exception as e:
        return jsonify({'error': f'Lỗi hệ thống: {str(e)}'}), 500

@app.route('/api/open-folder', methods=['POST'])
def api_open_folder():
    if os.environ.get('RENDER'):  # Render tự set biến này
        return jsonify({'error': 'Tính năng mở folder chỉ dùng được khi chạy local.'}), 400
    try:
        data = request.json or {}
        project = data.get('project', '').strip() or 'b2b'
        outdir_path = os.path.abspath(f"./{project}")
        if not os.path.exists(outdir_path):
            os.makedirs(outdir_path, exist_ok=True)
        
        if sys.platform == 'win32':
            os.startfile(outdir_path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', outdir_path])
        else:
            subprocess.Popen(['xdg-open', outdir_path])
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gitlab-push', methods=['POST'])
def api_gitlab_push():
    try:
        data = request.json or {}
        gitlab_url = data.get('gitlab_url', '').strip() or 'https://gitlab.com'
        token = data.get('token', '').strip()
        project = data.get('project', '').strip()
        branch = data.get('branch', 'main').strip() or 'main'
        subfolder = data.get('subfolder', '').strip().strip('/')
        commit_message = data.get('commit_message', '').strip() or 'Deploy k8s manifests'
        files = data.get('files', [])

        # Auto-parse full Git repository clone URL if provided
        if gitlab_url and (gitlab_url.endswith('.git') or '/' in gitlab_url.replace('://', '', 1).split('/', 1)[-1]):
            try:
                parsed = urllib.parse.urlparse(gitlab_url)
                if parsed.scheme and parsed.netloc:
                    gitlab_url = f"{parsed.scheme}://{parsed.netloc}"
                    parsed_project = parsed.path.strip('/')
                    if parsed_project.endswith('.git'):
                        parsed_project = parsed_project[:-4]
                    
                    if not project:
                        project = parsed_project
            except Exception as e:
                print(f"DEBUG - Exception parsing clone URL: {e}")

        if not token:
            return jsonify({'error': 'Access Token không được để trống.'}), 400
        if not project:
            return jsonify({'error': 'Project ID hoặc Path không được để trống.'}), 400
        if not files:
            return jsonify({'error': 'Không có file nào để đẩy.'}), 400

        project_encoded = urllib.parse.quote_plus(project)
        existing_files = set()
        
        # Fetch the repository tree to determine if we should use 'create' or 'update' action
        tree_url = f"{gitlab_url.rstrip('/')}/api/v4/projects/{project_encoded}/repository/tree"
        params = {'ref': branch, 'per_page': 100}
        if subfolder:
            params['path'] = subfolder
        
        tree_query = urllib.parse.urlencode(params)
        tree_request_url = f"{tree_url}?{tree_query}"
        
        print(f"DEBUG - GitLab Tree URL: {tree_request_url}")
        
        req = urllib.request.Request(tree_request_url)
        req.add_header('PRIVATE-TOKEN', token)
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    tree_data = json.loads(response.read().decode('utf-8'))
                    for item in tree_data:
                        if item.get('type') == 'blob':
                            existing_files.add(item.get('path'))
        except urllib.error.HTTPError as e:
            if e.code in [401, 403]:
                return jsonify({'error': 'Access Token không hợp lệ hoặc không có quyền truy cập dự án này.'}), e.code
            elif e.code == 404:
                # Path or branch not found is fine, they will be created by commit actions
                pass
        except Exception as ex:
            print(f"DEBUG - Exception checking repository tree: {ex}")

        # Build commit actions
        actions = []
        for file in files:
            file_name = file.get('name')
            file_content = file.get('content')
            
            if subfolder:
                full_file_path = f"{subfolder}/{file_name}"
            else:
                full_file_path = file_name
                
            action_type = 'update' if full_file_path in existing_files else 'create'
            
            actions.append({
                'action': action_type,
                'file_path': full_file_path,
                'content': file_content
            })

        commit_payload = {
            'branch': branch,
            'commit_message': commit_message,
            'actions': actions
        }
        
        commit_url = f"{gitlab_url.rstrip('/')}/api/v4/projects/{project_encoded}/repository/commits"
        print(f"DEBUG - GitLab Commit URL: {commit_url}")
        commit_req = urllib.request.Request(
            commit_url,
            data=json.dumps(commit_payload).encode('utf-8'),
            headers={
                'PRIVATE-TOKEN': token,
                'Content-Type': 'application/json'
            },
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(commit_req, timeout=15) as response:
                if response.status in [200, 201]:
                    commit_result = json.loads(response.read().decode('utf-8'))
                    return jsonify({
                        'success': True,
                        'commit_id': commit_result.get('id'),
                        'web_url': commit_result.get('web_url')
                    })
                else:
                    return jsonify({'error': f'Phản hồi từ GitLab không hợp lệ (Status {response.status}).'}), 500
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode('utf-8')
                print(f"DEBUG - GitLab HTTPError {e.code} Body: {err_body}")
                err_json = json.loads(err_body)
                if isinstance(err_json, dict):
                    err_msg = err_json.get('message') or err_json.get('error') or err_body
                else:
                    err_msg = err_body
            except Exception as ex:
                print(f"DEBUG - Exception parsing error body: {ex}")
                err_msg = e.reason
            return jsonify({'error': f'GitLab trả về lỗi: {err_msg}'}), e.code
            
    except Exception as e:
        return jsonify({'error': f'Lỗi hệ thống: {str(e)}'}), 500

if __name__ == '__main__':
    print("=== Kubernetes Manifest Generator Web UI ===")
    print("Mo trinh duyet truy cap: http://127.0.0.1:5000")
    import webbrowser
    import threading
    def open_browser(): webbrowser.open_new('http://127.0.0.1:5000')
    if __name__ == '__main__': threading.Timer(1.5, open_browser).start()
    app.run(host='127.0.0.1', port=5000, debug=False)
