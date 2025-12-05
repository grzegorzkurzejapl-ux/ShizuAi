import argparse
import textwrap
from dataclasses import dataclass
from typing import Optional, Tuple

import requests


class _Ansi:
    """Codes ANSI minimalistes pour la coloration sans dépendance externe."""

    LIGHTBLACK_EX = "\033[90m"
    RED = "\033[31m"
    LIGHTRED_EX = "\033[91m"
    RESET_ALL = "\033[0m"


Fore = _Ansi
Style = _Ansi


@dataclass
class WebSummary:
    snippet: str
    source: Optional[str] = None


def fetch_web_summary(query: str, timeout: float = 4.0) -> Optional[WebSummary]:
    """
    Récupère un résumé synthétique via l'API d'Instant Answer de DuckDuckGo.

    En cas d'échec réseau ou de réponse vide, on bascule silencieusement sur la réponse hors ligne.
    """

    query = query.strip()
    if not query:
        return None

    try:
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            headers={"User-Agent": "ShizuAi/1.0 (+https://example.com)"},
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        return None

    snippet = payload.get("AbstractText")
    if snippet:
        return WebSummary(snippet=snippet.strip(), source=payload.get("AbstractURL"))

    for topic in payload.get("RelatedTopics") or []:
        if isinstance(topic, dict) and topic.get("Text"):
            return WebSummary(snippet=topic["Text"], source=topic.get("FirstURL"))

    return None


def craft_offline_response(question: str) -> str:
    question = question.strip()
    if not question:
        return "Je suis ShizuAi. Pose-moi une question pour commencer !"

    lower_q = question.lower()
    if "bonjour" in lower_q or "salut" in lower_q:
        return "Bonjour ! Je suis ShizuAi, prête à t'aider. Tu cherches quoi aujourd'hui ?"

    if "qui es" in lower_q or "shizu" in lower_q:
        return "Je suis ShizuAi, une IA en Python qui peut répondre et chercher des infos sur le web."

    return textwrap.fill(
        (
            "Je vais analyser ta question et fournir une réponse concise. "
            "Active la recherche web si tu veux que je récupère aussi une source en ligne."
        ),
        width=90,
    )


def answer_question(question: str, use_web: bool = True, timeout: float = 4.0) -> Tuple[str, bool]:
    """Construit la réponse finale et indique si une donnée web a été utilisée."""

    web_summary = fetch_web_summary(question, timeout=timeout) if use_web else None
    offline_reply = craft_offline_response(question)

    if web_summary:
        response = textwrap.fill(
            (
                f"{offline_reply}\n\n"
                f"Recherche web : {web_summary.snippet}"
                + (f"\nSource : {web_summary.source}" if web_summary.source else "")
            ),
            width=90,
        )
        return response, True

    return offline_reply, False


def stylize_gradient(text: str) -> str:
    """Applique un dégradé gris/rouge sur chaque caractère."""

    palette = [Fore.LIGHTBLACK_EX, Fore.RED, Fore.LIGHTRED_EX]
    colored_chars = [palette[i % len(palette)] + ch for i, ch in enumerate(text)]
    return "".join(colored_chars) + Style.RESET_ALL


def banner(enabled: bool) -> None:
    if not enabled:
        print("ShizuAi")
        return

    title = stylize_gradient("ShizuAi")
    subtitle = (
        Fore.LIGHTBLACK_EX
        + "Assistant Python (hors ligne + recherche web DuckDuckGo optionnelle)"
        + Style.RESET_ALL
    )
    print(title)
    print(subtitle)
    print(Fore.LIGHTBLACK_EX + "Nuances de gris et de rouge activées." + Style.RESET_ALL)


def color_prefix(label: str, enabled: bool, web: bool) -> str:
    if not enabled:
        return label
    return (Fore.RED if web else Fore.LIGHTBLACK_EX) + label + Style.RESET_ALL


def interactive_session(
    default_use_web: bool = True,
    use_color: bool = True,
    timeout: float = 4.0,
    **_ignored: object,
) -> None:
    banner(use_color)
    print("Tape une question (ou vide pour quitter).")
    print(
        f"Recherche web activée par défaut : {'oui' if default_use_web else 'non'}; "
        f"délai web : {timeout:.1f}s.\n"
    )

    while True:
        try:
            question = input("Vous > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAu revoir !")
            break

        if not question:
            print("Session terminée. À bientôt !")
            break

        reply, from_web = answer_question(
            question, use_web=default_use_web, timeout=timeout
        )
        prefix = color_prefix("[Web]", use_color, web=from_web)
        offline_prefix = color_prefix("[Offline]", use_color, web=False)
        tag = prefix if from_web else offline_prefix
        print(f"{tag} {reply}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="ShizuAi - Assistant Python hors ligne avec option web")
    parser.add_argument(
        "question",
        nargs="*",
        help="Question à poser directement. Laisse vide pour une session interactive.",
    )
    parser.add_argument(
        "--no-web",
        action="store_true",
        help="Désactiver la récupération de résumés web (hors ligne uniquement).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Désactiver les couleurs gris/rouge dans le terminal.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=4.0,
        help="Délai maximal (en secondes) pour récupérer un résumé web.",
    )

    args = parser.parse_args()
    use_web = not args.no_web
    use_color = not args.no_color
    timeout = max(args.timeout, 0.1)
    if args.question:
        combined = " ".join(args.question)
        reply, from_web = answer_question(combined, use_web=use_web, timeout=timeout)
        prefix = color_prefix("[Web]", use_color, web=from_web)
        offline_prefix = color_prefix("[Offline]", use_color, web=False)
        tag = prefix if from_web else offline_prefix
        print(f"{tag} {reply}")
    else:
        interactive_session(
            default_use_web=use_web, use_color=use_color, timeout=timeout
        )


if __name__ == "__main__":
    main()
