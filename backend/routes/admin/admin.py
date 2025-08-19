# Route used to check Railway logs of scheduler
from flask import Blueprint, request, jsonify
from ..api.authentification.middleware import jwt_required


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/logs', methods=['GET'])
@jwt_required
def view_logs():
    """View log files - REMOVE in production!"""
    import os
    try:
        logs = {}
        log_dir = 'logs'
        
        # List all log files
        if os.path.exists(log_dir):
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    filepath = os.path.join(log_dir, filename)
                    with open(filepath, 'r') as f:
                        # Get last 100 lines
                        lines = f.readlines()
                        logs[filename] = ''.join(lines[-100:])
        
        return f"<pre>{str(logs)}</pre>"
    except Exception as e:
        return f"Error reading logs: {e}"

@admin_bp.route('/scheduler-status')
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