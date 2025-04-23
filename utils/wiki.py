import wikipedia

# Changer la langue si nécessaire (par défaut c'est en anglais)
wikipedia.set_lang("fr")

def get_city_summary(city_name):
    try:
        summary = wikipedia.summary(city_name, sentences=3)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Page ambiguë pour {city_name} : {e.options[:3]}"
    except wikipedia.exceptions.PageError:
        return f"Aucune page trouvée pour {city_name}."
    except Exception as e:
        return f"Erreur : {str(e)}"

# Exemple
ville = "Lyon"
print(get_city_summary(ville))