#!/usr/bin/env python3
"""genera-funding.py — construye las paginas de funding en HTML, en tres idiomas.

Una sola plantilla, tres juegos de cadenas. El bloque de direccion, los niveles
y los enlaces son los mismos en los tres idiomas; lo que cambia es el texto.

Uso: python3 tools/genera-funding.py
Salida: funding.html (es), funding.en.html (en), funding.pt.html (pt)
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent

CSS = """
:root{--bg:#0d0d10;--panel:#16161c;--line:#26262f;--text:#e8e8ee;--muted:#9a9aa8;
--accent:#ff3b30;--green:#2fa84f;--blue:#2a6fb0}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:900px;margin:0 auto;padding:0 20px}
header{border-bottom:1px solid var(--line)}
header .wrap{display:flex;align-items:center;justify-content:space-between;height:62px}
.logo{font-weight:800;letter-spacing:.16em;font-size:15px}
.logo span{color:var(--accent)}
nav a{color:var(--muted);text-decoration:none;margin-left:20px;font-size:14px}
nav a:hover{color:var(--text)}
.langs{margin-left:16px;border-left:1px solid var(--line);padding-left:14px}
.langs a{color:var(--muted);text-decoration:none;font-size:12px;font-weight:700;
letter-spacing:.08em;margin-left:8px}
.langs a.on{color:var(--accent)}
h1{font-size:clamp(28px,4.6vw,44px);line-height:1.12;margin:56px 0 16px;letter-spacing:-.02em}
h2{font-size:22px;margin:44px 0 12px}
p{margin:0 0 14px}
.lead{font-size:18px;color:var(--muted);max-width:680px}
.donate{background:linear-gradient(180deg,#141a16,#121216);border:1px solid #1e5a3f;
border-radius:14px;padding:26px;margin:26px 0}
.addr{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:15px;background:#0b0b0e;
border:1px solid var(--line);border-radius:9px;padding:16px;word-break:break-all;margin:14px 0}
.btn{display:inline-block;background:var(--green);color:#04160a;font-weight:700;padding:12px 22px;
border-radius:9px;text-decoration:none;font-size:15px}
.btn.ghost{background:transparent;border:1px solid var(--line);color:var(--text);font-weight:500}
.btn.blue{background:var(--blue);color:#04121f}
table{width:100%;border-collapse:collapse;margin:20px 0;font-size:15px}
th,td{text-align:left;padding:10px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-weight:600;font-size:13px;text-transform:uppercase;letter-spacing:.05em}
td.amount{font-weight:700;white-space:nowrap;color:#5fd08a}
.note{color:var(--muted);font-size:14px;border-left:3px solid var(--line);padding-left:14px;margin:18px 0}
code{background:#0b0b0e;padding:2px 7px;border-radius:5px;font-size:13.5px;
font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
a{color:#7fb0e0}
footer{border-top:1px solid var(--line);margin-top:64px;padding:28px 0 60px;color:var(--muted);font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:22px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:20px}
.card h3{margin:0 0 8px;font-size:16px}
.card p{color:var(--muted);font-size:14.5px;margin:0}
"""

ADDR = "GATED25F24BNVPQKSZCTRSBSKGHPZVDQUCM6JXAAQHDRZDVZEWDC7NO7"
ISSUER = "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN"
YT = "https://www.youtube.com/watch?v=m7lIbyha2kQ"
SP = "https://open.spotify.com/track/2lzdEocFpWso7knzCtL46g"
CH = "https://www.youtube.com/@ElReingeniero"

T = {
 "es": {
  "lang": "es", "code": "funding.html", "on": "ES",
  "h1": "Apoya DJMixer",
  "lead": "La versión Lite es gratis para todo el mundo, para siempre. Lo que se pide aquí es el coste de mantener el equipo de agentes que la construye: capacidad de modelos, hardware para probarla y la firma de código para que la descarga no salga con avisos.",
  "promise_h": "El compromiso",
  "promise": "La Lite se lanza gratis para todo el mundo y lo seguirá siendo: sin precio, sin cuota, sin suscripción, sin trial que expire. Existirá una versión Pro de pago para lo que un DJ necesita cuando crece (stems, grabación, DVS), nunca para lo esencial de mezclar. El compromiso está versionado en el repo y manda sobre cualquier otro texto.",
  "ask_h": "El pedido",
  "ask": "El cuello de botella real es la capacidad de modelos de IA que consume el equipo de cuatro agentes (CTO, Coder, QA, Growth). Cada decisión de motor, cada estudio de referencia y cada iteración de tests cuesta tokens. Eso es lo que frena la release.",
  "addr_h": "Donar con USDC",
  "addr_p": "Red Stellar (Soroban), USDC nativo de Circle. La cuenta es multisig 2-de-6: recibir no requiere firma, así que las donaciones entran al instante. Antes de enviar, comprueba los 6 primeros y los 6 últimos caracteres y manda primero un monto pequeño de prueba.",
  "levels_h": "Niveles",
  "c1h": "Qué paga el dinero", "c1": "Capacidad de modelos para el equipo de agentes, un MIDI controller para validar con hardware real y la cuenta de Apple Developer (99 USD/año) para que la descarga salga firmada y sin el aviso de Gatekeeper.",
  "c2h": "Sin cripto también", "c2": "GitHub Sponsors y Patreon se abren con la primera donations. La Lite es gratis igual: no donar no te pone en una lista de features más pequeña.",
  "c3h": "El álbum va incluido", "c3": "La Lite se publica con el álbum completo de McBaez, gratis. El software y el proyecto musical son el mismo.",
  "comp_h": "Cumplimiento",
  "comp": "Esto es una donación, no una inversión: no hay token, ni participación, ni promesa de retorno. Las donaciones pueden ser ingreso imponible para quien dona (en Chile, SUNAT): eso lo consulta cada uno con su contador, el proyecto no da consejo fiscal. La dirección es de uso exclusivo del proyecto.",
  "track_h": "El artista",
  "track": "Relaunch, de McBaez (McDiscJockey) — deep garage / 2-step '90s. Si lo escuchas una vez, es una reproducción; si te gusta, un like. El canal donde se sigue todo esto es El Reingeniero.",
  "cta": "Leer el sitio y las especificaciones",
  "more": "Sitio, capturas y las 17 especificaciones técnicas",
  "foot": "DJMixer · software de DJ libre y gratis para siempre · GPL-2.0-or-later · construido por un equipo de agentes de IA con un humano al mando.",
 },
 "en": {
  "lang": "en", "code": "funding.en.html", "on": "EN",
  "h1": "Support DJMixer",
  "lead": "The Lite edition is free for everyone, forever. What is being asked for here is the cost of keeping the agent team that builds it: model capacity, hardware to test it on, and code signing so the download does not arrive with warnings.",
  "promise_h": "The promise",
  "promise": "The Lite launches free for everyone and stays that way: no price, no fee, no subscription, no trial that expires. A paid Pro will exist for what a DJ needs once they grow (stems, recording, DVS) - never for the essentials of mixing. The commitment is versioned in the repository and overrides any other text.",
  "ask_h": "The ask",
  "ask": "The real bottleneck is the AI model capacity that the team of four agents (CTO, Coder, QA, Growth) consumes. Every engine decision, every reference study and every test iteration costs tokens. That is what gates the release.",
  "addr_h": "Donate with USDC",
  "addr_p": "Stellar (Soroban) network, Circle-native USDC. The account is a 2-of-6 multisig: receiving needs no signature, so donations arrive unattended. Before sending, check the first 6 and last 6 characters and send a small test amount first.",
  "levels_h": "Levels",
  "c1h": "What the money pays for", "c1": "Model capacity for the agent team, a MIDI controller to validate with real hardware, and the Apple Developer account (99 USD/year) so the download is signed and nobody gets a Gatekeeper warning.",
  "c2h": "No crypto needed", "c2": "GitHub Sponsors and Patreon open with the first donations. The Lite is free either way: not donating does not put you on a smaller feature list.",
  "c3h": "The album ships with it", "c3": "The Lite is released with McBaez's complete album, free. The software project and the music project are the same thing.",
  "comp_h": "Compliance",
  "comp": "This is a donation, not an investment: no token, no equity, no promise of a return. Donations may be taxable income for the donor (in Chile, SUNAT) - each donor should check with their own accountant; the project gives no tax advice. The address is dedicated to the project.",
  "track_h": "The artist",
  "track": "Relaunch by McBaez (McDiscJockey) - deep garage / 2-step '90s. One listen is a play; if you like it, a like. The channel where all of this continues is El Reingeniero.",
  "cta": "Read the site and the technical specs",
  "more": "Site, screenshots and the 17 technical specifications",
  "foot": "DJMixer · free and forever open-source DJ software · GPL-2.0-or-later · built by a team of AI agents with one human in charge.",
 },
 "pt": {
  "lang": "pt", "code": "funding.pt.html", "on": "PT",
  "h1": "Apoie o DJMixer",
  "lead": "A versão Lite é gratuita para todo mundo, para sempre. O que se pede aqui é o custo de manter a equipe de agentes que a constrói: capacidade de modelos, hardware para testá-la e a assinatura de código para o download não chegar com avisos.",
  "promise_h": "O compromisso",
  "promise": "A Lite é lançada gratuita para todo mundo e continua assim: sem preço, sem mensalidade, sem assinatura, sem trial que expire. Existirá uma versão Pro paga para o que um DJ precisa quando cresce (stems, gravação, DVS), nunca para o essencial de misturar. O compromisso está versionado no repositório e prevalece sobre qualquer outro texto.",
  "ask_h": "O pedido",
  "ask": "O gargalo real é a capacidade de modelos de IA que a equipe de quatro agentes (CTO, Coder, QA, Growth) consome. Cada decisão de motor, cada estudo de referência e cada iteração de testes custa tokens. É isso que trava o lançamento.",
  "addr_h": "Doar com USDC",
  "addr_p": "Rede Stellar (Soroban), USDC nativo da Circle. A conta é multisig 2-de-6: receber não exige assinatura, então as doações entram na hora. Antes de enviar, confira os 6 primeiros e 6 últimos caracteres e mande primeiro um valor pequeno de teste.",
  "levels_h": "Níveis",
  "c1h": "O que o dinheiro paga", "c1": "Capacidade de modelos para a equipe de agentes, um MIDI controller para validar com hardware real e a conta Apple Developer (99 USD/ano) para o download sair assinado e sem o aviso do Gatekeeper.",
  "c2h": "Sem cripto também", "c2": "GitHub Sponsors e Patreon abrem com a primeira doação. A Lite é grátis de qualquer forma: não doar não te coloca numa lista de recursos menor.",
  "c3h": "O álbum vem junto", "c3": "A Lite é lançada com o álbum completo de McBaez, grátis. O projeto de software e o projeto musical são o mesmo.",
  "comp_h": "Conformidade",
  "comp": "Isto é uma doação, não um investimento: não há token, participação ou promessa de retorno. Doações podem ser income tributável para quem doa (no Chile, SUNAT) - cada doador deve consultar seu contador; o projeto não dá orientação tributária. O endereço é exclusivo do projeto.",
  "track_h": "O artista",
  "track": "Relaunch, de McBaez (McDiscJockey) - deep garage / 2-step '90s. Uma escuta é uma reprodução; se gostar, é um like. O canal onde isso continua é o El Reingeniero.",
  "cta": "Ver o site e as especificações técnicas",
  "more": "Site, capturas e as 17 especificações técnicas",
  "foot": "DJMixer · software de DJ livre e grátis para sempre · GPL-2.0-or-later · feito por uma equipe de agentes de IA com um humano no comando.",
 },
}

TPL = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{h1} — DJMixer</title>
<meta name="description" content="DJMixer: software de DJ nativo (C++/Qt6) en la liga de Serato y Traktor. La Lite es gratis para todo el mundo, para siempre. Apoya el proyecto con USDC.">
<meta property="og:title" content="{h1} — DJMixer">
<meta property="og:image" content="https://mcontreraz.github.io/djmixer/media/03-decks.png">
<style>{css}</style>
</head>
<body>
<header><div class="wrap">
  <div class="logo">DJ <span>·</span> MIXER</div>
  <nav>
    <a href="index{es}.html">{site}</a>
    <a href="{code}">{funding}</a>
    <div class="langs">
      <a href="funding.html"{on_es}>ES</a>
      <a href="funding.en.html"{on_en}>EN</a>
      <a href="funding.pt.html"{on_pt}>PT</a>
    </div>
  </nav>
</div></header>

<div class="wrap">
<h1>{h1}</h1>
<p class="lead">{lead}</p>

<h2>{promise_h}</h2>
<p>{promise}</p>

<h2>{ask_h}</h2>
<p>{ask}</p>

<div class="donate">
  <h3 style="margin-top:0">{addr_h}</h3>
  <p style="color:var(--muted);font-size:15px">{addr_p}</p>
  <div class="addr">{addr}</div>
  <p style="color:var(--muted);font-size:14px">Issuer (Circle, Stellar): <code>{issuer}</code></p>
  <a class="btn" href="{yt}">▶ YouTube</a>
  <a class="btn ghost" href="{sp}">Spotify</a>
  <a class="btn ghost" href="{ch}">El Reingeniero</a>
</div>

<h2>{levels_h}</h2>
<table>
  <tr><th>{amount_h}</th><th>{covers_h}</th></tr>
  <tr><td class="amount">USDC 20</td><td>{l1}</td></tr>
  <tr><td class="amount">USDC 100</td><td>{l2}</td></tr>
  <tr><td class="amount">USDC 500</td><td>{l3}</td></tr>
  <tr><td class="amount">USDC 2,000</td><td>{l4}</td></tr>
</table>
<p class="note"><strong>{goal_h}:</strong> {goal}</p>

<div class="grid">
  <div class="card"><h3>{c1h}</h3><p>{c1}</p></div>
  <div class="card"><h3>{c2h}</h3><p>{c2}</p></div>
  <div class="card"><h3>{c3h}</h3><p>{c3}</p></div>
</div>

<h2>{track_h}</h2>
<p>{track}</p>

<h2>{comp_h}</h2>
<p class="note">{comp}</p>

<p style="margin-top:34px">
  <a class="btn" href="https://mcontreraz.github.io/djmixer/">{cta}</a>
  <a class="btn ghost" style="margin-left:8px" href="https://github.com/mcontreraz/djmixer">{more}</a>
</p>

<footer><p>{foot}</p></footer>
</div>
</body>
</html>
"""

COMMON = {
 "amount_h": {"es": "Importe", "en": "Amount", "pt": "Valor"},
 "covers_h": {"es": "Cubre", "en": "Covers", "pt": "Cobre"},
 "l1": {"es": "Un par de noches de capacidad de modelos.", "en": "A couple of nights of model capacity.", "pt": "Um par de noites de capacidade de modelos."},
 "l2": {"es": "Una semana de carga pesada del equipo.", "en": "A week of heavy team load.", "pt": "Uma semana de carga pesada da equipe."},
 "l3": {"es": "Un mes con el equipo completo corriendo.", "en": "A full month with the whole team running.", "pt": "Um mês com a equipe inteira rodando."},
 "l4": {"es": "Varios meses, más MIDI controller y la firma de código para la release.", "en": "Several months, plus a MIDI controller and code signing for the release.", "pt": "Vários meses, mais MIDI controller e assinatura de código para o lançamento."},
 "goal_h": {"es": "Objetivo del primer tramo", "en": "First milestone target", "pt": "Meta do primeiro trecho"},
 "goal": {"es": "USDC 2.000 — el presupuesto de la release Lite de punta a punta: meses de capacidad de modelos, hardware para validar con un DJ real y la firma para que la descarga no salga con el aviso de Gatekeeper.",
         "en": "USDC 2,000 - the budget for the Lite release end to end: months of model capacity, hardware to validate with a real DJ, and signing so the download does not arrive with a Gatekeeper warning.",
         "pt": "USDC 2.000 - o orçamento do lançamento Lite de ponta a ponta: meses de capacidade de modelos, hardware para validar com um DJ real e a assinatura para o download não chegar com o aviso do Gatekeeper."},
 "site": {"es": "Sitio", "en": "Site", "pt": "Site"},
 "funding": {"es": "Financiación", "en": "Funding", "pt": "Financiamento"},
}

for lang, t in T.items():
    def c(k):
        v = COMMON[k]
        return v[lang]
    html = TPL.format(
        lang=t["lang"], css=CSS, h1=t["h1"], lead=t["lead"], code=t["code"],
        promise_h=t["promise_h"], promise=t["promise"],
        ask_h=t["ask_h"], ask=t["ask"],
        addr_h=t["addr_h"], addr_p=t["addr_p"], addr=ADDR, issuer=ISSUER,
        yt=YT, sp=SP, ch=CH,
        levels_h=t["levels_h"], amount_h=c("amount_h"), covers_h=c("covers_h"),
        l1=c("l1"), l2=c("l2"), l3=c("l3"), l4=c("l4"),
        goal_h=c("goal_h"), goal=c("goal"),
        c1h=t["c1h"], c1=t["c1"], c2h=t["c2h"], c2=t["c2"], c3h=t["c3h"], c3=t["c3"],
        track_h=t["track_h"], track=t["track"],
        comp_h=t["comp_h"], comp=t["comp"],
        cta=t["cta"], more=t["more"], foot=t["foot"],
        site=c("site"), funding=c("funding"),
        es="" if lang == "es" else ".en",
        on_es=' class="on"' if lang == "es" else "",
        on_en=' class="on"' if lang == "en" else "",
        on_pt=' class="on"' if lang == "pt" else "",
    )
    (OUT / t["code"]).write_text(html)
    print("generado:", t["code"], f"({len(html)} bytes)")
