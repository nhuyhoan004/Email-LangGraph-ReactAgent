# Email-LangGraph-ReactAgent

AI agent quan ly email, xay tren LangGraph ReAct agent + Claude (`claude-opus-5`)
va Gmail API.

Trang thai hien tai: **Phase 2 - agent chi doc, giao dien CLI**.

## Kien truc

```
CLI (cli.py)
   |
LangGraph ReAct agent (agent/graph.py)  -->  ChatAnthropic
   |
Tools (agent/tools.py)
   |
Gmail adapter (email_client/)  -->  Gmail API
```

Lop `email_client/` la Python thuan, khong biet gi ve LLM. Nho vay co the test
va debug rieng, khong lan loi giua model va Gmail API.

## Cai dat

```bash
python -m venv .venv
.venv\Scripts\activate        # PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### Google OAuth

1. Vao [Google Cloud Console](https://console.cloud.google.com/), tao project moi.
2. **APIs & Services > Library** -> bat **Gmail API**.
3. **OAuth consent screen** -> chon External -> them chinh email cua ban vao
   phan **Test users** (bat buoc, khong lam buoc nay se bi tu choi khi dang nhap).
4. **Credentials > Create credentials > OAuth client ID** -> kieu **Desktop app**.
5. Tai file JSON ve, doi ten thanh `credentials.json` va de o thu muc goc repo.

### Bien moi truong

```bash
cp .env.example .env      # roi dien ANTHROPIC_API_KEY
```

## Su dung

Buoc 1 - kiem tra ket noi Gmail, khong dung AI:

```bash
python scripts/check_inbox.py
python scripts/check_inbox.py "is:unread newer_than:7d"
```

Lan dau chay se mo trinh duyet de dang nhap Google, sau do luu `token.json`.

Buoc 2 - chat voi agent:

```bash
email-agent
# hoac: python -m email_agent.cli
```

Vi du cau hoi:
- "hom nay co mail nao can tra loi gap khong?"
- "tom tat cac email chua doc trong 3 ngay qua, nhom theo muc do khan"
- "tim email tu bo phan ke toan thang nay, co deadline gi khong?"

## Test

```bash
pytest
```

Test hien chi phu phan parser MIME - phan de vo nhat va khong can credentials.

## Pham vi quyen

Scope hien tai la `gmail.readonly`. Agent **khong the** gui, xoa, gan label hay
sua bat cu thu gi. Muon mo them, sua `GMAIL_SCOPES` trong `src/email_agent/config.py`
va **xoa `token.json`** de chay lai OAuth (token cu khong tu nang scope).

## Prompt injection

Noi dung email la do nguoi ngoai viet. Moi body email deu duoc boc trong the
`<email_content>` va system prompt yeu cau model coi do la du lieu, khong phai
chi thi. Day la ly do chinh de giu che do chi doc cho den khi co lop human-in-
the-loop o Phase 4.

## Lo trinh

- [x] Phase 1 - Gmail adapter + parser MIME, khong AI
- [x] Phase 2 - ReAct agent chi doc + CLI
- [ ] Phase 3 - Triage co cau truc, gan label (`gmail.modify`)
- [ ] Phase 4 - Soan draft + gui, co `interrupt()` cho nguoi duyet; `SqliteSaver`
- [ ] Phase 5 - Memory preference, digest theo lich, bo eval
