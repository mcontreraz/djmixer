# Support DJMixer — Help keep the Lite free forever

> **Free forever is the product, not a trial.** DJMixer's Lite edition will never
> ask anyone for a subscription. This page exists to pay for the AI capacity and
> the tools that let a very small team ship it.

DJMixer is a DJ software built from scratch — in the same league as Serato and
Traktor — by a team of AI agents (CTO, Coder, QA, Growth) owned by a Chilean
software engineer and music lover. The goal is simple: **any DJ who wants to be a
DJ should be able to start without paying monthly fees or buying expensive
software.**

- Latest work: the `main` branch of this repository.
- Licence: GPL-2.0-or-later (the complete source ships with every binary).
- Runtime: native C++17 / Qt 6 (QML), real-time audio — not a web wrapper.

---

## What your support pays for

| Item | Why it matters | Cost |
|---|---|---|
| **AI model capacity (tokens)** | The engineering team is a set of AI agents. They need paid model capacity to keep implementing, reverse-engineering reference behaviour, and reviewing audio DSP. This is the core ask. | By far the largest line: it scales with how much gets built. |
| **Reference hardware** | A MIDI controller and a second audio interface (two outputs, so PFL and the master can run at the same time) to test real-world DJ workflows: PFL, hot cues, scratch, jog sensitivity. | ≈250 USD one-off (≈60–120 for the controller, ≈120–180 for the interface). The controller the project already reverse-engineers is the owner's own Vestax VCI-100MK2, so it is not bought. |
| **Code signing** | macOS notarisation for the public binaries, so users don't get Gatekeeper warnings on download. This is the Apple Developer Program. | 99 USD/year. |
| **Domain + releases hosting** | The download page and the release mirror. | ≈15 USD/year for the domain. The page and the binaries run on GitHub Pages and GitHub Releases, at 0 USD. |

Nothing here is a "pro subscription". There is no paid tier gating the basics:
loading a track, mixing, looping, cueing and syncing are Lite features, forever.

---

**Código fuente:** se publica completo junto con el primer binario
(obligación de GPL-2.0-or-later). **El repositorio del código fuente es
privado hasta la primera release**; el repositorio público es el sitio del
proyecto: la página de financiación, las capturas, las notas de desarrollo y
las especificaciones técnicas.

## The promise

**The Lite edition launches free for everyone, and stays free forever.** No
price, no fee, no subscription, no trial that expires. This is not a launch
promotion — it is the reason the project exists: so any DJ who wants to be a
DJ can start without monthly fees or expensive software.

**A paid Pro version will exist.** That is a decision, not an open question.
The Pro is built from a separately licensed core and covers *growth* features —
stems and separation, recording, advanced key analysis, DVS, hardware mappings
and priority support are the candidates under discussion with the community —
and never the essentials of mixing. The basics stay in the Lite, free,
permanently. No date is announced for the Pro.

The full commitment is versioned in [`docs/promise.md`](docs/promise.md). If any
other page ever contradicts it, that document wins.

## Sponsor levels

**First goal: USDC 99 — this is the launch key.** The single donation that
signs and notarizes the macOS binary (Apple Developer Program). Until the
Apple Developer account exists, the release ships with a Gatekeeper warning
and four release issues stay blocked. USDC 99 today moves the Lite v1 out the
door; the rest of the milestone can come after.

| Amount | What it covers |
|---|---|
| **USDC 20** | A couple of nights of agent capacity |
| **USDC 100** | About a week of heavy model capacity |
| **USDC 500** | A full month with the whole team running |
| **USDC 2,000** | Several months, plus MIDI hardware and code signing for the public release |

**Current milestone target: USDC 500** — enough to ship the Lite v1 end to end:

- About a month of paid model capacity for the agent team (the real
  bottleneck: every engine decision, every reference study and every test
  iteration costs tokens) — roughly 390 USD of this tranche. That is what pays
  for the Lite v1 bundle, the signed binary and the audio validation that is
  still open (the automatic beatgrid is still being validated against real
  tracks, and the DJ-side feel — latency, jog, hot-cue timing under pressure —
  can only be checked by a human with a controller).
- Apple Developer account (99 USD/yr) so the macOS binary is signed and
  notarized — users download without a Gatekeeper warning
- Domain (≈15 USD/yr); the download page and the release binaries run on
  GitHub Pages and GitHub Releases (0 USD)

**Next tier: USDC 2,000** — adds the reference hardware (a MIDI controller and a
second audio interface, ≈250 USD) and several more months of capacity, so the
team can keep building after the launch instead of stopping at it.

Amounts are a guide to what the work costs, not a price list of features:
donating any amount gives you exactly the same free-forever Lite.

## Donate with USDC

> **One network is live: Stellar (Soroban).** The Base, Polygon PoS and
> Ethereum addresses are published the day the project owner provides one for
> each of those networks — until then, send on Stellar only.
> `tools/check-funding.sh` has to pass before this page is announced anywhere,
> so a page with a missing or mistyped address can never go out.

USDC only — never ETH, never a yield-bearing asset, never a token. The project
budgets in USD, so a stablecoin keeps the accounting trivial and the donor's
intent unambiguous: this is a donation, not an investment.

**Networks accepted:**

| Network | Asset | Status |
|---|---|---|
| **Stellar (Soroban)** | native USDC, issuer `GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN` (Circle) | **Live** — primary network |
| Base | native USDC | Address published once the owner provides it |
| Polygon PoS | native USDC | Address published once the owner provides it |
| Ethereum | native USDC | Address published once the owner provides it |

Only the networks listed with a live address can receive. The USDC on a
different chain is a different asset, and a wrong-network transfer can be
unrecoverable.

**Address + memo (the two go together):**

```
Stellar (Soroban):  GATED25F24BNVPQKSZCTRSBSKGHPZVDQUCM6JXAAQHDRZDVZEWDC7NO7
Memo:               4WG9VNC4HF9H1TD4V5AJAN7XB4
```

The deposit goes to the project's AirTM custody account, which is how the
holder receives Stellar USDC. **Crediting is per memo**: a transfer that does
not carry the memo above may not be credited to the project until support
intervenes, so send both values from this sheet — or scan the QR, which
carries them together (SEP-7).

![Donation QR — address + memo (SEP-7)](donate-qr.png)

<details><summary>QR address-only (wallets that don't parse SEP-7 — you then
type the memo from the sheet by hand)</summary>

![Donation QR address-only](donate-qr-address.png)

</details>

**Before you send — check these five things:**

1. First 6 characters of the address match the ones published here
   (`GATED2…`).
2. Last 6 characters of the address match the ones published here
   (`…DC7NO7`).
3. The **memo field is filled with the project's memo** — an empty or wrong
   memo delays the credit.
4. You are on Stellar and the asset is USDC issued by the Circle issuer shown
   above.
5. Send a small test amount first, confirm it arrived, then send the rest.

> Only send on the network you intend; sending USDC on the wrong network can
> result in permanent loss of funds. Donations that are sent to a wrong
> address, or to a network that is not listed here, cannot be recovered.

## Support without crypto

If you would rather not touch crypto at all, these are the routes — no wallet,
no network, no fees:

| Route | What it is | Status |
|---|---|---|
| **GitHub Sponsors** | Recurring support straight from your GitHub account | Account being opened — the link goes in here the day it is live |
| **Patreon** | Membership tiers that fund the agent team's model capacity | Account being opened — the link goes in here the day it is live |

The Lite edition is free either way. Not donating USDC does not put you on a
smaller feature list.

---

## Important notes

- **These are donations, not investments.** There is no token, no equity, no
  share, no revenue share, and no promise of any return. You are supporting
  open-source development, full stop.
- **Tax:** donations may be taxable income for the donor in their jurisdiction
  (in Chile, the **SII** — Servicio de Impuestos Internos — treats a donation
  as income subject to the corresponding income tax). Talk to an accountant —
  this project is not giving tax advice and cannot advise you on yours.
- **The address is dedicated to this project.** Prefer an address you control
  yourself, separate from anything else, so the on-chain history is auditable.
- **No custody, no keys, no trading.** The project never holds or moves funds
  on anyone's behalf.

## Why open source?

Because GPL-2.0 is what makes the promise credible: anyone can read the
source, build it, fork it, and ship it. The plan is documented in
[`docs/business-model.md`](docs/business-model.md) (Lite free forever → paid
Pro, built from a de-GPL'd core) and the launch sequence in
[`docs/launch-plan.md`](docs/launch-plan.md).

## Transparency

The team is an AI agent team plus one human. The repository keeps the spec
history, the audio test suite, and the reference research that went into each
feature. Where the AI got something wrong, the tests and the git history show
it. If a feature is not working, the issue tracker says so.

## Publishing checklist (owner)

`tools/check-funding.sh` must pass before this page is announced anywhere.

```sh
./tools/check-funding.sh
```

It verifies that there are no placeholders left, that the published address
carries a valid checksum (Stellar strkey CRC16-XModem today, EVM `0x` when
those networks get their own address), that the "not an investment / tax / no
tax advice" block is intact, and that the promise wording still matches
[`docs/promise.md`](docs/promise.md).
