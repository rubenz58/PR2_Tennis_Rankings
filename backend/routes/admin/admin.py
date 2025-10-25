# Route used to check Railway logs of scheduler
import os
from flask import Blueprint, request, jsonify
from datetime import datetime

from ..api.authentification.middleware import jwt_required, admin_required
from tasks.scheduler import trigger_manual_update


admin_bp = Blueprint('admin', __name__)

def read_log_file_json(file_path, lines_to_show=50):
    """Read log file and return JSON-friendly data"""
    try:
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': f"Log file not found: {file_path}",
                'file_path': file_path,
                'exists': False
            }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        recent_lines = lines[-lines_to_show:] if total_lines > lines_to_show else lines
        
        # Get file metadata
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        last_modified = datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        
        return {
            'success': True,
            'file_path': file_path,
            'exists': True,
            'content': recent_lines,  # Array of lines
            'metadata': {
                'total_lines': total_lines,
                'shown_lines': len(recent_lines),
                'file_size_bytes': file_size,
                'file_size_kb': round(file_size / 1024, 1),
                'last_modified': last_modified,
                'lines_requested': lines_to_show
            }
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f"Error reading file: {str(e)}",
            'file_path': file_path,
            'exists': True
        }

@admin_bp.route('/logs', methods=['GET'])
@jwt_required
@admin_required
def get_logs_overview():
    """Get overview of all log files"""
    log_files = {
        'app': {
            'filename': 'app.log',
            'description': 'General Flask application logs',
            'path': 'logs/app.log'
        },
        'errors': {
            'filename': 'errors.log', 
            'description': 'Error logs and exceptions',
            'path': 'logs/errors.log'
        },
        'scraping': {
            'filename': 'scraping.log',
            'description': 'Weekly ATP ranking scraping logs',
            'path': 'logs/scraping.log'
        }
    }
    
    overview = {}
    total_files = 0
    total_size = 0
    
    for log_type, info in log_files.items():
        filepath = info['path']
        
        if os.path.exists(filepath):
            file_stats = os.stat(filepath)
            with open(filepath, 'r') as f:
                line_count = sum(1 for _ in f)
            
            overview[log_type] = {
                'filename': info['filename'],
                'description': info['description'],
                'exists': True,
                'lines': line_count,
                'size_bytes': file_stats.st_size,
                'size_kb': round(file_stats.st_size / 1024, 1),
                'last_modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
            }
            
            total_files += 1
            total_size += file_stats.st_size
        else:
            overview[log_type] = {
                'filename': info['filename'],
                'description': info['description'],
                'exists': False,
                'lines': 0,
                'size_bytes': 0,
                'size_kb': 0,
                'last_modified': None
            }
    
    return jsonify({
        'success': True,
        'logs': overview,
        'summary': {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_kb': round(total_size / 1024, 1),
            'timestamp': datetime.now().isoformat()
        }
    })

@admin_bp.route('/logs/app', methods=['GET'])
@jwt_required
@admin_required
def get_app_logs():
    """Get application log data"""
    # Get optional query parameter for number of lines
    from flask import request
    lines = request.args.get('lines', 50, type=int)
    lines = min(lines, 200)  # Cap at 200 lines max
    
    log_data = read_log_file_json('logs/app.log', lines)
    log_data['log_type'] = 'app'
    log_data['title'] = 'Application Logs'
    
    return jsonify(log_data)

@admin_bp.route('/logs/errors', methods=['GET'])
@jwt_required
@admin_required
def get_error_logs():
    """Get error log data"""
    from flask import request
    lines = request.args.get('lines', 50, type=int)
    lines = min(lines, 200)  # Cap at 200 lines max
    
    log_data = read_log_file_json('logs/errors.log', lines)
    log_data['log_type'] = 'errors'
    log_data['title'] = 'Error Logs'
    
    return jsonify(log_data)

@admin_bp.route('/logs/scraping', methods=['GET'])
@jwt_required
@admin_required
def get_scraping_logs():
    """Get scraping log data"""
    from flask import request
    lines = request.args.get('lines', 50, type=int)
    lines = min(lines, 200)  # Cap at 200 lines max
    
    log_data = read_log_file_json('logs/scraping.log', lines)
    log_data['log_type'] = 'scraping'
    log_data['title'] = 'Scraping Logs'
    
    return jsonify(log_data)

# Optional: Real-time log streaming endpoint
# GET /admin/api/logs/<type>/tail?lines=20
@admin_bp.route('/logs/<log_type>/tail', methods=['GET'])
@jwt_required
@admin_required
def tail_logs(log_type):
    """Get the last N lines of a specific log file (for real-time updates)"""
    from flask import request
    
    valid_log_types = ['app', 'errors', 'scraping']
    if log_type not in valid_log_types:
        return jsonify({
            'success': False,
            'error': f"Invalid log type. Must be one of: {', '.join(valid_log_types)}"
        }), 400
    
    lines = request.args.get('lines', 20, type=int)
    lines = min(lines, 100)  # Cap at 100 lines for tail
    
    file_path = f'logs/{log_type}.log'
    log_data = read_log_file_json(file_path, lines)
    log_data['log_type'] = log_type
    log_data['title'] = f'{log_type.title()} Logs (Tail)'
    
    return jsonify(log_data)

@admin_bp.route('/scheduler-status')
@jwt_required
@admin_required
def scheduler_status():
    """Check if scheduler is running"""
    try:
        from tasks.scheduler import get_scheduled_jobs
        jobs = get_scheduled_jobs()
        return {
            'jobs': [str(job) for job in jobs],
            'job_count': len(jobs),
            'status': 'scheduler_running' if jobs else 'no_jobs_found'
        }
    except Exception as e:
        return {'error': str(e)}
    
@admin_bp.route('/trigger-manual-update')
@jwt_required
@admin_required
def players_manual_update():
    """Trigger Manual Update of ATP Players Table"""
    try:
        trigger_manual_update()
        # All Flask routes need to return
        return {'success': True, 'message': 'Manual update completed successfully'}

    except Exception as e:
        print("Manual Update Failed")
        return {'success': False, 'error': str(e)}
