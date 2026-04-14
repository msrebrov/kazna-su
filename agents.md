# РОДИТЕЛЬСКИЙ КОМИТЕТ — Agent Reference

> **Version:** 1.1 | **Updated:** 2026-04-14
> This file is the single source of truth for AI agents working on this project.
> Update the Changelog and File Map at the end of every session.

---

## 1. Purpose & Problem

School parent committees in Russia collect money from parents 1–2 times per year (gifts, trips, events). Today this is done via personal cards/cash with manual tracking in Excel or notebooks — causing bank card blocks (115-ФЗ), lack of transparency, trust conflicts, and significant time burden on the treasurer.

**This service** provides a mobile app + backend that connects to a bank collective account (Ozon Bank), automates collection tracking, and gives every parent real-time visibility into transactions and receipts.

---

## 2. Service Architecture

```
[Max Messenger Bot / Telegram Bot / Flutter App (v2)]
           |
           v
  [NestJS API Gateway]  <-- REST/JSON, JWT via SMS OTP
           |
    +------+------+----------+
    |             |          |
[PostgreSQL] [Redis Cache] [Yandex Object Storage]
    |                          |
[OCR Service]           [Receipt photos / PDFs]
(Yandex Vision / ML Kit)
    |
[FCM Push / Telegram Bot]
    |
[Ozon Bank Collective Account]  <-- read-only webhook / manual sync (MVP)
```

**Data flow (MVP):**
1. Treasurer creates `Class` + links collective account number
2. Parents join via invite link / QR code
3. Treasurer creates `Collection` (goal, amount, deadline)
4. Parents pay directly to collective account via SBP/QR → confirm in app
5. Treasurer logs `Transaction` (expense) + attaches receipt photo
6. OCR auto-extracts amount + merchant name
7. All parents see live feed of transactions
8. Treasurer generates `Report` → PDF auto-sent to Max / Telegram group chat

---

## 3. User Roles & Permissions

| Action | Admin (казначей) | Parent | Observer (teacher) |
|--------|:---:|:---:|:---:|
| Create/edit Class | ✅ | ❌ | ❌ |
| Invite members | ✅ | ❌ | ❌ |
| Create Collection | ✅ | ❌ | ❌ |
| Log expense + receipt | ✅ | ❌ | ❌ |
| Confirm own contribution | ✅ | ✅ | ❌ |
| View balance & transactions | ✅ | ✅ | ✅ |
| View receipts | ✅ | ✅ | ✅ |
| Generate report | ✅ | ❌ | ❌ |
| Transfer Admin role | ✅ | ❌ | ❌ |
| Vote on expenditure | ✅ | ✅ | ❌ |

---

## 4. Core Entities (Data Model)

```
Class
  id, name, school, grade, bank_account_no, invite_code, created_at

Member
  id, class_id → Class, user_id → User, role (admin|parent|observer), joined_at

User
  id, phone (unique), name, push_token, telegram_id?

Collection
  id, class_id → Class, title, target_amount, current_amount,
  deadline, status (active|closed|cancelled), created_by → User

Transaction
  id, class_id → Class, collection_id? → Collection,
  type (income|expense), amount, category, description,
  receipt_url?, ocr_data (json), created_by → User, created_at

ContributionStatus
  id, collection_id → Collection, member_id → Member,
  amount_paid, paid_at?, status (pending|partial|paid)

Report
  id, class_id → Class, period_start, period_end,
  pdf_url, generated_by → User, generated_at

Vote
  id, class_id → Class, question, options (json),
  expires_at, results (json), created_by → User
```

---

## 5. Feature Catalogue

| Feature | MVP | v2 | v3 |
|---------|:---:|:---:|:---:|
| Class creation & invite | ✅ | | |
| Collections (goals) | ✅ | | |
| Manual transaction logging | ✅ | | |
| Receipt photo attach | ✅ | | |
| OCR receipt parsing | ✅ | | |
| Parent contribution status | ✅ | | |
| Soft payment reminders | ✅ | | |
| PDF report generation | ✅ | | |
| QR code for SBP payment | ✅ | | |
| Max Messenger Bot (primary) | ✅ | | |
| Telegram Bot (parallel) | ✅ | | |
| Push notifications (FCM) | ✅ | | |
| Treasurer handoff (1-tap) | ✅ | | |
| Bank statement CSV import | | ✅ | |
| Auto-match statement ↔ contributions | | ✅ | |
| Installment payments | | ✅ | |
| Voting on expenditures | | ✅ | |
| Auto-post expense card to chat | | ✅ | |
| Multi-class (school tier) | | ✅ | |
| School admin panel | | ✅ | |
| Direct bank API (Open Banking) | | | ✅ |
| International banks support | | | ✅ |
| White-label / SDK for schools | | | ✅ |

---

## 6. API Surface (Planned Endpoints)

```
Auth
  POST /auth/otp/send          { phone }
  POST /auth/otp/verify        { phone, code } → { token }

Classes
  POST   /classes              create class
  GET    /classes/:id          get class info + balance
  POST   /classes/:id/invite   generate/refresh invite link
  POST   /classes/:id/join     join via invite code
  PATCH  /classes/:id/transfer transfer admin role

Collections
  POST   /classes/:id/collections        create collection
  GET    /classes/:id/collections        list collections
  PATCH  /collections/:id               update
  DELETE /collections/:id               cancel
  GET    /collections/:id/contributions  contribution status per member

Transactions
  POST   /classes/:id/transactions       log income or expense
  GET    /classes/:id/transactions       list (filter: type, date, collection)
  POST   /transactions/:id/receipt       upload receipt photo → OCR
  DELETE /transactions/:id              soft delete

Contributions
  POST   /contributions/:id/confirm      parent confirms own payment

Reports
  POST   /classes/:id/reports            generate PDF for period
  GET    /classes/:id/reports            list reports

Votes
  POST   /classes/:id/votes              create vote
  POST   /votes/:id/answer               cast vote

Notifications
  POST   /classes/:id/remind             send soft reminder to unpaid members
```

---

## 7. Tech Stack & Infrastructure

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Mobile (priority)** | Max Messenger Bot (VK Team) | Zero install friction, parents already in Max; bot UI — no app install needed |
| **Mobile (v2)** | Flutter | iOS + Android native app from one codebase |
| **Backend** | NestJS (Node.js + TypeScript) | Modular, decorators, built-in DI |
| **Database** | PostgreSQL 15 | Main store |
| **Cache / queues** | Redis | Sessions, job queues, rate limiting |
| **File storage** | Yandex Object Storage (S3-compatible) | RF data residency (152-ФЗ) |
| **OCR** | Yandex Vision API | Receipt text extraction |
| **Auth** | SMS OTP via SMS.ru or SMSC | Passwordless, familiar UX |
| **Push** | FCM + Max / TG bot messages | Free, cross-platform |
| **Max Messenger** | Max Messenger Bot API | Primary bot interface, notifications |
| **Telegram** | Telegram Bot API | Secondary bot interface, notifications |
| **PDF generation** | Puppeteer or pdfmake | Reports |
| **Hosting** | Yandex Cloud (App Engine / Serverless) | RF residency, reasonable cost |
| **CI/CD** | GitHub Actions | Lint → test → deploy |

---

## 8. Legal Constraints (РФ)

- **152-ФЗ (Personal Data):** All PII stored exclusively in RF. Collect minimum: name + phone. No passports, addresses, or financial details beyond contribution amounts. Privacy Policy required in app stores.
- **115-ФЗ (AML):** Using a bank collective account (not a personal card) removes risk of transfer classification as income. App is NOT a payment agent — money flows directly to the bank account.
- **Tax:** Class committee collections are voluntary contributions. Properly documented they are not taxable income. A Terms of Service / public offer is required.
- **Required legal documents before launch:**
  1. Privacy Policy (обязательна для App Store / Google Play)
  2. Terms of Service / Public Offer
  3. Personal Data Processing Consent (shown on signup)
  4. Parent Committee Charter template (for schools)

---

## 9. Monetization

| Tier | Price | Limits | Key extras |
|------|-------|--------|------------|
| Free | 0 ₽ | 1 class, ≤ 35 members | Basic features |
| Premium | 299–499 ₽/month/class | Unlimited members | Unlimited OCR, auto-reports, analytics, priority support |
| School | 990–2990 ₽/month | All classes in school | Multi-class, school admin panel, branding |
| B2B (banks) | CPA deal | — | Revenue share for collective account acquisition |

**Market size (RF):** ~42 000 schools, ~500 000 classes. At 5% Premium conversion: ~25 000 classes × 399 ₽/mo ≈ 10M ₽/month.

**International expansion:** Kazakhstan, Belarus, Uzbekistan (same committee model), then EU (PTA model). Architecture must stay bank-agnostic.

---

## 10. File Map

```
/Users/main/Code/kazna.su/
├── .github/workflows/
│   └── deploy.yml              ← GitHub Actions: SSH deploy on push to main
├── agents.md                   ← THIS FILE (AI reference, update every session)
├── create_doc.py               ← One-off script: generated the concept DOCX
├── index.html                  ← Production landing page (copy of main.html)
├── main.html                   ← Source landing page (брендбук)
├── nginx.conf                  ← Nginx vhost config (template, installed on server)
├── robots.txt                  ← SEO robots config
├── SERVER-CONNECT.md           ← Server connection & deploy reference
├── SERVER-CONNECT-TEMPLATE.md  ← Template for new projects
├── .gitignore
└── output/
    └── Концепция_Родительский_Комитет.docx   ← Full product concept document
```

> **Convention:** Update this map when adding directories or significant files.

---

## 11. Key Decisions & Rationale

1. **Max Messenger Bot + Telegram Bot first, native app second**
   — Max Messenger has growing adoption in Russian school communities; bot interface means zero install friction for parents. Telegram Bot runs in parallel for parents who prefer TG. Native Flutter app planned for v2 after product validation.

2. **Bank-agnostic architecture from day 1**
   — Ozon Bank collective account is the current trigger, but Tinkoff, Sber, Alfa may launch equivalents. Use `bank_account_no` as a plain string; no hard coupling to Ozon APIs.

3. **Manual sync in MVP, no direct bank API**
   — Avoid regulatory complexity of Open Banking. Treasurer imports bank statement CSV or enters transactions manually. Validate product before building integration.

4. **Soft reminders only, never public shaming**
   — Reminders are private (push/bot to the individual parent). Never expose "who hasn't paid" in a group view. This prevents conflict and legal risk.

5. **Minimize PII**
   — Name + phone only. No financial profile, no passport data. Reduces 152-ФЗ compliance burden and data breach risk.

6. **One-tap treasurer handoff**
   — Burnout is real. Admin transfer must take one action and carry full history, settings, and roles. Losing a treasurer mid-year must not break the class.

7. **OCR is UX polish, not core**
   — OCR speeds up receipt entry but manual entry is always the fallback. Never block a workflow on OCR success.

8. **Installment payments in v2, not MVP**
   — Reduces the friction of large one-time asks. Out of scope for MVP to keep complexity low.

---

## 12. Changelog

| Date | Session summary |
|------|----------------|
| 2026-04-05 | Initial project setup. Generated concept DOCX (`create_doc.py`). Created `agents.md` from concept document. |
| 2026-04-14 | Updated platform strategy: Max Messenger Bot as primary entry + Telegram Bot in parallel (replacing Telegram Mini App). Updated architecture, tech stack, features, and key decisions. |
| 2026-04-14 | Created GitHub repo (msrebrov/kazna-su), set up CI/CD (GitHub Actions SSH deploy), deployed landing page to VPS, configured nginx + SSL (Let's Encrypt) at kazna.su. |

> **AI instructions:** At the end of each session, append a one-line row to this table describing what was built or changed.
