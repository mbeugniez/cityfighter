import wikipedia
import wikipediaapi
from bs4 import BeautifulSoup

wikipedia.set_lang("fr")

DEFAULT_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Map_marker_icon_%E2%80%93_Nicolas_Mollet_%E2%80%93_City_%E2%80%93_Tourism_%E2%80%93_White.png/512px-Map_marker_icon_%E2%80%93_Nicolas_Mollet_%E2%80%93_City_%E2%80%93_Tourism_%E2%80%93_White.png"

def get_blason_et_site_wikipedia(city_name, departement=None, region=None):
    wiki_wiki = wikipediaapi.Wikipedia(
        language='fr',
        user_agent='CityFightingApp - Projet académique BUT3 STID (contact: a.souedane@gmail.com)'
    )

    essais = [
        f"{city_name} ({departement})" if departement else None,
        f"{city_name} ({region})" if region else None,
        f"{city_name} (commune)",
        f"{city_name}, France",
        f"{city_name} (France)",
        city_name
    ]

    page = None
    for titre in essais:
        if not titre:
            continue
        page = wiki_wiki.page(titre)
        if page.exists() and "commune" in page.summary.lower():
            break
        page = None

    if not page:
        return {
            "summary": "Aucune présentation disponible pour cette commune.",
            "image": DEFAULT_IMAGE_URL,
            "url": ""
        }

    try:
        result = wikipedia.page(page.title, auto_suggest=False, preload=False)
        images = result.images
        image = next(
            (img for img in images if img.endswith(('.jpg', '.jpeg', '.png')) and 'blason' not in img.lower()),
            DEFAULT_IMAGE_URL
        )
        summary_clean = BeautifulSoup(page.summary, "html.parser").text.strip().replace("\n", " ")
        if len(summary_clean) > 600:
            summary_clean = summary_clean[:600].rsplit('.', 1)[0] + "."

        return {
            "summary": summary_clean,
            "image": image,
            "url": result.url
        }

    except Exception:
        summary_clean = BeautifulSoup(page.summary, "html.parser").text.strip().replace("\n", " ")
        if len(summary_clean) > 600:
            summary_clean = summary_clean[:600].rsplit('.', 1)[0] + "."
        return {
            "summary": summary_clean,
            "image": DEFAULT_IMAGE_URL,
            "url": f"https://fr.wikipedia.org/wiki/{page.title.replace(' ', '_')}"
        }
