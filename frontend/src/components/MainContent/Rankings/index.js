import './Rankings.css';
import { useRankings } from '../../../contexts/RankingsContext';
import { LoadingSpinner, useInfiniteScroll } from '../../FrontEndUtils';

export const Rankings = () => {
  // Will rerender anytime useRankings changes.
  const {
    players,
    getNewPlayers,
    hasMore,
    loadingPlayers,
  } = useRankings();

  const triggerRef = useInfiniteScroll();

  // if (loadingPlayers && Object.keys(players).length === 0) {
  //   console.log("LOADING");
  //   return (
  //     <div className="rankings-container">
  //       <div className="rankings-header">
  //         <h1 className="rankings-title">ATP Rankings</h1>
  //         <div className="rankings-count">Loading...</div>
  //       </div>
  //       <div className="rankings-loading">
  //         <div className="rankings-loading-spinner"></div>
  //         <div className="rankings-loading-text">Loading tennis rankings...</div>
  //       </div>
  //     </div>
  //   );
  // }
  
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

        <div ref={triggerRef} style={{ height: '20px' }}>
          {loadingPlayers && <LoadingSpinner/>}
        </div>
      </div>
    </div>
  );
}