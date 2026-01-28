import requests

class Item:
    BASE_URL = "https://pokeapi.co/api/v2/item"

    @staticmethod
    def get_item(identifier):
        """
        Récupère les données d'un Item par id ou nom.
        :param identifier: int ou str (id ou nom)
        :return: dict (JSON) ou None si erreur
        """
        url = f"{Item.BASE_URL}/{identifier}/"

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # lève une exception si code != 200
            return response.json()

        except requests.exceptions.HTTPError:
            print(f"Item '{identifier}' introuvable.")
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de l'appel à l'API : {e}")

        return None
    
    
    
