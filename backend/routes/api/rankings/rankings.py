from flask import Blueprint, request, jsonify
from models import Player, db
from ..authentification.middleware import jwt_required
import time


rankings_bp = Blueprint('rankings', __name__)

@rankings_bp.route('/players', methods=['GET'])
@jwt_required  # Require authentication to access rankings
def get_players():
    """
    Get players with pagination
    Query params:
    - offset: starting position (default: 0)
    - limit: number of players to return (default: 20, max: 50)
    
    Example: /api/rankings/players?offset=0&limit=20
    """
    # time.sleep(3)
    try:
        # Get query parameters
        offset = request.args.get('offset', 0, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        # Validate parameters
        if offset < 0:
            return jsonify({'error': 'Offset must be non-negative'}), 400
        
        if limit <= 0 or limit > 50:
            return jsonify({'error': 'Limit must be between 1 and 50'}), 400
        
        # Get total count for pagination metadata
        total_count = Player.query.count()
        
        # Query players with pagination, ordered by ranking
        players = Player.query.order_by(Player.ranking).offset(offset).limit(limit).all()
        
        # Convert to dictionaries
        players_data = [player.to_dict() for player in players]
        
        # Calculate pagination metadata
        has_more = (offset + limit) < total_count
        next_offset = offset + limit if has_more else None
        
        response = {
            'players': players_data,
            'pagination': {
                'offset': offset,
                'limit': limit,
                'total_count': total_count,
                'returned_count': len(players_data),
                'has_more': has_more,
                'next_offset': next_offset
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch players', 'details': str(e)}), 500