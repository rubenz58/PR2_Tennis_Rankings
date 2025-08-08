import './Rankings.css';
import { useRankings } from '../../contexts/RankingsContext';

export const Rankings = () => {
  const { nextOffset, limit, players } = useRankings();
  
  return (
    <div className="rankings-container">
      <div className="rankings-header">
        <h1 className="rankings-title">ATP Rankings</h1>
        <div className="rankings-count">
          {Object.keys(players).length} Players
        </div>
      </div>
      
      <div className="players-list">
        {Object.values(players).map(player => {
          // Add special classes for top rankings
          let rowClass = 'player-row';
          if (player.ranking <= 10) rowClass += ' top-10';
          if (player.ranking === 1) rowClass += ' rank-1';
          
          return (
            <div key={player.ranking} className={rowClass}>
              <div className="player-ranking">#{player.ranking}</div>
              <div className="player-name">{player.name}</div>
              <div className="player-points">{player.points.toLocaleString()} pts</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}