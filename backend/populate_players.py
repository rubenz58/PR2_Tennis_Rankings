from app import create_app
from models import Player, db

# Create the Flask app and push application context
app = create_app()

with app.app_context():
    # Clear existing players (optional - remove if you want to keep existing data)
    Player.query.delete()
    
    # Add 100 test players
    for i in range(1, 101):
        new_player = Player(
            ranking=i,
            name=f"Player {i}",
            points=1000-i*5  # More realistic point distribution
        )
        db.session.add(new_player)
    
    # Commit all at once (more efficient)
    db.session.commit()
    print("Successfully added 100 players to the database!")