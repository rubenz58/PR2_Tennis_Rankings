import './Rankings.css';

import { useRankings } from '../../contexts/RankingsContext';

export const Rankings = () => {

    const { nextOffset, limit, players } = useRankings();

    return (
        <div>
            <h1>Rankings</h1>
            <h2>Offset: {nextOffset}</h2>
            <h2>Limit: {limit}</h2>
            <h2>NumPlayers: {Object.keys(players).length}</h2>
        </div>
    );
}