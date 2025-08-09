# spectator_tiles.py

class SpectatorTile:
    """Represents a spectator tile placed on the board"""
    
    def __init__(self, player_name, position, side='cheering'):
        self.player_name = player_name
        self.position = position
        self.side = side  # 'cheering' (+1 movement) or 'booing' (-1 movement)
    
    def get_movement_modifier(self):
        """Get the movement modifier for this tile"""
        return 1 if self.side == 'cheering' else -1
    
    def __repr__(self):
        symbol = "+" if self.side == 'cheering' else "-"
        return f"SpectatorTile({self.player_name}, pos={self.position}, {symbol})"


class PyramidTicket:
    """Represents a pyramid ticket taken by a player"""
    
    def __init__(self, player_name):
        self.player_name = player_name
        self.value = 1  # Each pyramid ticket is worth 1 EP at end of leg
    
    def __repr__(self):
        return f"PyramidTicket({self.player_name})"


class SpectatorTileManager:
    """Manages spectator tiles on the board"""
    
    def __init__(self, track_length=16):
        self.track_length = track_length
        self.tiles = {}  # position -> SpectatorTile
    
    def can_place_tile(self, position):
        """Check if a spectator tile can be placed at this position"""
        # Cannot place on position 1 or finish line (16), and position must be empty
        if position <= 1 or position >= self.track_length:
            return False
        return position not in self.tiles
    
    def place_tile(self, player_name, position, side='cheering'):
        """Place a spectator tile at the given position"""
        if not self.can_place_tile(position):
            return False
        
        tile = SpectatorTile(player_name, position, side)
        self.tiles[position] = tile
        return True
    
    def get_tile_at_position(self, position):
        """Get the spectator tile at a position, if any"""
        return self.tiles.get(position, None)
    
    def get_movement_modifier(self, position):
        """Get movement modifier for a position (0 if no tile)"""
        tile = self.get_tile_at_position(position)
        return tile.get_movement_modifier() if tile else 0
    
    def get_tile_owner(self, position):
        """Get the owner of the tile at a position"""
        tile = self.get_tile_at_position(position)
        return tile.player_name if tile else None
    
    def get_available_positions(self, board):
        """Get all positions where spectator tiles can be placed"""
        available = []
        for pos in range(2, self.track_length):  # Positions 2 to 15
            # Check if position is empty (no camels) and no tile already there
            if not board.tiles[pos] and self.can_place_tile(pos):
                available.append(pos)
        return available
    
    def remove_tile(self, position):
        """Remove spectator tile at position"""
        if position in self.tiles:
            tile = self.tiles.pop(position)
            return tile
        return None
    
    def get_player_tile_position(self, player_name):
        """Get the position of a player's spectator tile, if any"""
        for position, tile in self.tiles.items():
            if tile.player_name == player_name:
                return position
        return None
    
    def move_tile(self, player_name, new_position, side='cheering'):
        """Move a player's existing spectator tile to a new position"""
        # Find and remove the player's existing tile
        old_position = self.get_player_tile_position(player_name)
        if old_position is None:
            return False  # Player has no tile to move
        
        # Check if new position is valid
        if not self.can_place_tile(new_position):
            return False
        
        # Remove old tile and place new one
        self.remove_tile(old_position)
        return self.place_tile(player_name, new_position, side)
    
    def __repr__(self):
        return f"SpectatorTileManager({len(self.tiles)} tiles placed)"


class PyramidTicketManager:
    """Manages pyramid tickets"""
    
    def __init__(self):
        self.available_tickets = 5  # 5 pyramid tickets available per leg
        self.used_tickets = []
    
    def can_take_ticket(self):
        """Check if pyramid tickets are available"""
        return self.available_tickets > 0
    
    def take_ticket(self, player_name):
        """Take a pyramid ticket for a player"""
        if not self.can_take_ticket():
            return None
        
        ticket = PyramidTicket(player_name)
        self.available_tickets -= 1
        self.used_tickets.append(ticket)
        return ticket
    
    def reset_for_new_leg(self):
        """Reset pyramid tickets for new leg"""
        self.available_tickets = 5
        self.used_tickets = []
    
    def get_available_count(self):
        """Get number of available pyramid tickets"""
        return self.available_tickets
    
    def __repr__(self):
        return f"PyramidTicketManager({self.available_tickets} available, {len(self.used_tickets)} used)"