
class PKMNTeam(object):
    def __init__(self):
        self.teamList = []
        
        
        return self
    
    def addPokemon(self, pokemonToAdd):
        if len(self.teamList) == 6:
            raise Exception("Can't add more than 6 pokemon to a team")
        



class Pokemon(object):
    def __init__(self, pokemon_name):
        self.pokemon_name = pokemon_name
        self.move1 = None
        self.move2 = None
        self.move3 = None
        self.move4 = None
    
    def addMove(self, moveToAdd, position):
        match position:
            case 1:
                self.move1 = moveToAdd
            case 2:
                self.move2 = moveToAdd
            case 3:
                self.move3 = moveToAdd
            case 4:
                self.move4 = moveToAdd