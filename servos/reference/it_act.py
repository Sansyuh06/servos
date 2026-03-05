"""
Indian IT Act reference lookup.

Provides offline access to relevant sections of the Information Technology
Act and related IPC clauses.  Sections are stored in memory with searchable
keywords.  The module offers simple lookup and automated suggestion logic
based on forensic findings.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from servos.models.schema import ForensicFindings


@dataclass
class ITActResult:
    section_id: str
    title: str
    description: str
    punishment: str
    keywords: List[str]
    relevance: float = 0.0


# core database
_SECTIONS: Dict[str, ITActResult] = {
    "43": ITActResult(
        section_id="43",
        title="Unauthorized access to computer material",
        description=(
            "Whoever, without permission of the owner or any other person who"
            " is in charge of a computer, computer system or computer network,"
            " accesses or secures access to such computer, computer system or"
            " computer network or computer resource shall be punished with"
            " imprisonment for a term which may extend to three years, or with"
            " fine which may extend to two lakh rupees, or with both."
        ),
        punishment="Imprisonment up to 3 years or fine up to ₹200,000 or both.",
        keywords=["unauthorized", "access", "computer", "damage"],
    ),
    "43A": ITActResult(
        section_id="43A",
        title="Compensation for failure to protect data",
        description=(
            "Where a body corporate, possessing, dealing or handling any"
            " sensitive personal data or information in a computer resource"
            " which it owns, controls or operates, is negligent in implementing"
            " and maintaining reasonable security practices and procedures and"
            " thereby causes wrongful loss or wrongful gain to any person,"
            " such body corporate shall be liable to pay damages by way of"
            " compensation to the person so affected."
        ),
        punishment="Liability to pay compensation to affected persons.",
        keywords=["data protection", "negligence", "body corporate"],
    ),
    "65": ITActResult(
        section_id="65",
        title="Tampering with source code",
        description=(
            "Whoever knowingly or intentionally conceals, destroys or alters any"
            " computer source code used for a computer, computer programme,"
            " computer system or computer network, when the source code is"
            " required to be kept or maintained by law for the purpose of"
            " investigation, shall be punished with imprisonment for a term"
            " which may extend to three years, or with fine which may extend to"
            " two lakh rupees, or with both."
        ),
        punishment="Imprisonment up to 3 years or fine up to ₹200,000 or both.",
        keywords=["source code", "tampering"],
    ),
    "66": ITActResult(
        section_id="66",
        title="Computer-related offences",
        description=(
            "Whoever commits hacking shall be punished with imprisonment for a"
            " term which may extend to three years or with fine which may extend"
            " to five lakh rupees, or with both."
        ),
        punishment="Imprisonment up to 3 years or fine up to ₹500,000 or both.",
        keywords=["hacking", "computer", "offence"],
    ),
    "66B": ITActResult(
        section_id="66B",
        title="Punishment for dishonestly receiving stolen computer resource",
        description=(
            "Whoever dishonestly receives or retains any stolen computer"
            " resource or communication device knowing or having reason to"
            " believe that the same is stolen, shall be punished with"
            " imprisonment for a term which may extend to three years, or"
            " with fine which may extend to one lakh rupees, or with both."
        ),
        punishment="Imprisonment up to 3 years or fine up to ₹100,000 or both.",
        keywords=["receiving stolen", "computer resource", "dishonest"],
    ),
    "66C": ITActResult(
        section_id="66C",
        title="Identity theft",
        description=(
            "Whoever, dishonestly or fraudulently, makes use of the electronic"
            " signature, password or any other unique identification feature of"
            " any other person, shall be punished with imprisonment for a term"
            " which may extend to three years and with fine which may extend to"
            " one lakh rupees."
        ),
        punishment="Imprisonment up to 3 years and fine up to ₹100,000.",
        keywords=["identity theft", "electronic signature", "password"],
    ),
    "66D": ITActResult(
        section_id="66D",
        title="Cheating by personation by using computer resource",
        description=(
            "Any person who cheats by personation by using any communication"
            " device or computer resource shall be punished with imprisonment"
            " for a term which may extend to three years and with fine which may"
            " extend to one lakh rupees."
        ),
        punishment="Imprisonment up to 3 years and fine up to ₹100,000.",
        keywords=["cheating", "personation"],
    ),
    "66E": ITActResult(
        section_id="66E",
        title="Violation of privacy",
        description=(
            "Whoever, intentionally or knowingly captures, publishes or"
            " transmits the image of a private area of any person without his"
            " or her consent, under circumstances violating the privacy of"
            " that person, shall be punished with imprisonment for a term"
            " which may extend to three years or with fine not exceeding"
            " two lakh rupees, or with both."
        ),
        punishment="Imprisonment up to 3 years or fine up to ₹200,000 or both.",
        keywords=["privacy", "image"],
    ),
    "66F": ITActResult(
        section_id="66F",
        title="Cyber terrorism",
        description=(
            "Whoever with intent or knowledge causes or is likely to cause"
            " the gross disruption of, or damage to, the critical information"
            " infrastructure or denies or causes the denial of access to any"
            " person authorized to access it, or causes the damage or"
            " destruction of any information, data, or computer resource shall"
            " be punished with imprisonment for life."
        ),
        punishment="Imprisonment for life.",
        keywords=["cyber terrorism", "critical infrastructure"],
    ),
    "67": ITActResult(
        section_id="67",
        title="Publishing obscene material in electronic form",
        description=(
            "Whoever publishes or transmits or causes to be published or"
            " transmitted in the electronic form any material which is lascivious"
            " or appeals to the prurient interest or if its effect is such as to"
            " tend to deprave or corrupt persons who are likely to read, see or"
            " hear the contents of such material shall be punished with"
            " imprisonment for a term which may extend to five years and with"
            " fine which may extend to ten thousand rupees."
        ),
        punishment="Imprisonment up to 5 years and fine up to ₹10,000.",
        keywords=["obscene", "material", "electronic"],
    ),
    "67A": ITActResult(
        section_id="67A",
        title="Publishing sexually explicit material in electronic form",
        description=(
            "Whoever publishes or transmits or causes to be published or"
            " transmitted in the electronic form any sexually explicit material"
            " shall be punished with imprisonment for a term which may extend to"
            " seven years and with fine which may extend to ten thousand"
            " rupees."
        ),
        punishment="Imprisonment up to 7 years and fine up to ₹10,000.",
        keywords=["sexually explicit", "material"],
    ),
    "67B": ITActResult(
        section_id="67B",
        title="Publishing or transmitting of material depicting children in"
                " sexual act etc.",
        description=(
            "Whoever publishes or transmits or causes to be published or"
            " transmitted in the electronic form any material depicting children"
            " in sexual act or conduct shall be punished with imprisonment for a"
            " term which may extend to five years and with fine which may extend"
            " to ten thousand rupees."
        ),
        punishment="Imprisonment up to 5 years and fine up to ₹10,000.",
        keywords=["child pornography"],
    ),
    "69": ITActResult(
        section_id="69",
        title="Power to issue directions for interception or monitoring of"
              " any information through any computer resource",
        description=(
            "Where any agency authorised by the Central Government or any"
            " officer authorised by that agency, is satisfied that it is"
            " necessary or expedient so to do in the interest of the"
            " sovereignty or integrity of India, defence of India, security of"
            " the State, friendly relations with foreign States or public"
            " order, for preventing incitement to the commission of any offence"
            " relating to the above, the agency may intercept, monitor or decrypt"
            " any information generated, transmitted, received or stored in any"
            " computer resource."
        ),
        punishment="As prescribed by law.",
        keywords=["interception", "monitoring", "government"],
    ),
    "72": ITActResult(
        section_id="72",
        title="Breach of confidentiality and privacy",
        description=(
            "Save as otherwise provided in this Act or any other law for the"
            " time being in force, any person who, in pursuance of any of the"
            " provisions of this Act or any other law for the time being in"
            " force, has secured access to any electronic record, book, register"
            " correspondence, information, document or other material, the"
            " disclosure of which is forbidden by any law for the time being in"
            " force, shall be punished with imprisonment for a term which may"
            " extend to two years, or with fine which may extend to one lakh"
            " rupees, or with both."
        ),
        punishment="Imprisonment up to 2 years or fine up to ₹100,000 or both.",
        keywords=["confidentiality", "privacy"],
    ),
    "75": ITActResult(
        section_id="75",
        title="Extraterritorial jurisdiction",
        description=(
            "Any offence or contravention under this Act committed by any"
            " person outside India shall be dealt with by the Court having"
            " jurisdiction in any place in India where the computer, computer"
            " system or computer network is located, or where the offence has"
            " caused or is likely to cause effect."
        ),
        punishment="Jurisdictional provisions as per law.",
        keywords=["extraterritorial", "jurisdiction"],
    ),
    "IPC419": ITActResult(
        section_id="IPC419",
        title="Cheating by personation",
        description=(
            "Whoever cheats by personation shall be punished with imprisonment"
            " of either description for a term which may extend to three years,"
            " or with fine, or with both."
        ),
        punishment="Imprisonment up to 3 years or fine or both.",
        keywords=["cheating", "personation"],
    ),
    "IPC420": ITActResult(
        section_id="IPC420",
        title="Cheating and dishonestly inducing delivery of property",
        description=(
            "Whoever cheats and dishonestly induces any person to deliver any"
            " property to any person, or to make, alter or destroy the whole or"
            " any part of a valuable security, or anything which is signed or"
            " sealed, and which is capable of being converted into a valuable"
            " security, shall be punished with imprisonment of either"
            " description for a term which may extend to seven years, and shall"
            " also be liable to fine."
        ),
        punishment="Imprisonment up to 7 years and fine.",
        keywords=["cheating", "dishonest", "property"],
    ),
    "IPC468": ITActResult(
        section_id="IPC468",
        title="Forgery for purpose of cheating",
        description=(
            "Whoever commits forgery with the intent to cheat shall be"
            " punished with imprisonment of either description for a term which"
            " may extend to seven years, and shall also be liable to fine."
        ),
        punishment="Imprisonment up to 7 years and fine.",
        keywords=["forgery", "cheating"],
    ),
}


def lookup(query: str) -> List[ITActResult]:
    """Keyword match against title/description/keywords, return top 3.

    Relevance is simple count of matched keywords; normalized by number of
    keywords to produce a float used for sorting.  Case-insensitive.
    """
    q = query.lower()
    results: List[ITActResult] = []
    for sec in _SECTIONS.values():
        score = 0.0
        # check title/description
        if sec.title.lower().find(q) != -1 or sec.description.lower().find(q) != -1:
            score += 1.0
        for kw in sec.keywords:
            if kw.lower() in q:
                score += 1.0
        if score > 0:
            r = ITActResult(**sec.__dict__)
            r.relevance = score
            results.append(r)
    results.sort(key=lambda r: r.relevance, reverse=True)
    return results[:3]


def suggest_sections_for_findings(findings: ForensicFindings) -> List[ITActResult]:
    """Heuristic suggestions based on the contents of *findings*.

    Returns a list of relevant sections ordered by perceived importance.
    """
    suggestions: Dict[str, float] = {}

    # malware -> 66 and 43
    if findings.malware and findings.malware.indicators:
        suggestions["66"] = suggestions.get("66", 0) + 1.0
        suggestions["43"] = suggestions.get("43", 0) + 0.5

    # identity artifacts: look for "username" or "password" in any artifact
    if findings.artifacts:
        for art in findings.artifacts.all_artifacts():
            txt = " ".join(str(v) for v in art.content.values()).lower()
            if any(term in txt for term in ("username", "password", "id", "ssn")):
                suggestions["66C"] = suggestions.get("66C", 0) + 1.0
                suggestions["66D"] = suggestions.get("66D", 0) + 0.5
                break

        # suspicious browser domains
        if findings.artifacts.browser_history:
            for art in findings.artifacts.browser_history:
                if art.suspicious_score and art.suspicious_score >= 0.5:
                    suggestions["66B"] = suggestions.get("66B", 0) + 1.0
                    suggestions["43"] = suggestions.get("43", 0) + 0.5
                    break

    # convert to ITActResult list
    results: List[ITActResult] = []
    for sec_id, score in suggestions.items():
        sec = _SECTIONS.get(sec_id)
        if sec:
            r = ITActResult(**sec.__dict__)
            r.relevance = score
            results.append(r)
    # sort descending relevance
    results.sort(key=lambda r: r.relevance, reverse=True)
    return results
