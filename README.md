# Email LangGraph ReAct Agent

Trợ lý AI quản lý email trên giao diện dòng lệnh, được xây dựng bằng LangGraph ReAct và Gmail API. Agent có thể tìm kiếm, đọc, tóm tắt và phân loại thông tin trong hộp thư bằng ngôn ngữ tự nhiên.

> **Trạng thái:** Phase 2 — agent chỉ đọc, chạy trên giao diện CLI. Agent chưa thể gửi, xóa, lưu trữ hoặc gắn nhãn email.

## Tính năng

- Trò chuyện bằng tiếng Việt để tìm và tóm tắt email.
- Tìm kiếm bằng cú pháp Gmail, ví dụ: `is:unread newer_than:7d`.
- Đọc một email hoặc toàn bộ chuỗi hội thoại (thread).
- Liệt kê các nhãn hiện có trong hộp thư.
- Hỗ trợ OpenAI, OpenRouter, Google Gemini và Anthropic Claude.
- Duy trì ngữ cảnh trong suốt một phiên CLI.
- Phân tách lớp Gmail khỏi lớp LLM để dễ kiểm thử và gỡ lỗi.
- Chỉ yêu cầu quyền `gmail.readonly` trong giai đoạn hiện tại.

## Kiến trúc

```text
CLI (cli.py)
   │
LangGraph ReAct agent (agent/graph.py) ──> OpenAI / OpenRouter / Gemini / Claude
   │
LangChain tools (agent/tools.py)
   │
Gmail adapter (email_client/) ───────────> Gmail API
```

Thư mục `email_client/` là mã Python độc lập với LLM. Nhờ đó, kết nối Gmail và bộ phân tích MIME có thể được kiểm tra riêng trước khi khởi chạy agent.

## Yêu cầu

- Python 3.12 trở lên.
- `pip`.
- Tài khoản Google có Gmail.
- Một Google Cloud project đã bật Gmail API.
- API key của ít nhất một nhà cung cấp LLM được hỗ trợ.

## Cài đặt nhanh

Thực hiện các lệnh sau tại thư mục gốc của repository.

### 1. Tạo môi trường ảo

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

macOS hoặc Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Cài đặt dự án

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Chế độ editable (`-e`) cài lệnh `email-agent` và cho phép thay đổi mã nguồn mà không phải cài lại package.

### 3. Thiết lập Google OAuth

1. Mở [Google Cloud Console](https://console.cloud.google.com/) và tạo hoặc chọn một project.
2. Vào **APIs & Services > Library**, tìm **Gmail API**, rồi bật API này.
3. Trong **Google Auth platform**, cấu hình màn hình đồng ý OAuth tại các mục **Branding**, **Audience** và **Data Access**.
4. Nếu ứng dụng ở trạng thái **Testing** và có audience là **External**, thêm địa chỉ Gmail cần đăng nhập vào danh sách **Test users**.
5. Vào **Google Auth platform > Clients**, chọn **Create client**, rồi chọn loại ứng dụng **Desktop app**.
6. Tải tệp JSON, đổi tên thành `credentials.json` và đặt tại thư mục gốc của repository.

Xem thêm hướng dẫn chính thức: [Gmail API Python quickstart](https://developers.google.com/workspace/gmail/api/quickstart/python).

Không commit `credentials.json` hoặc `token.json`. Hai tệp này đã được khai báo trong `.gitignore`.

### 4. Cấu hình biến môi trường

Tạo tệp `.env` từ tệp mẫu.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS hoặc Linux:

```bash
cp .env.example .env
```

Mở `.env`, chọn một provider và điền API key tương ứng:

```dotenv
EMAIL_AGENT_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Để trống để dùng model mặc định của provider.
EMAIL_AGENT_MODEL=

GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
```

Các provider được hỗ trợ:

| `EMAIL_AGENT_PROVIDER` | Biến API key bắt buộc | Model mặc định |
| --- | --- | --- |
| `openai` | `OPENAI_API_KEY` | `gpt-4o-mini` |
| `openrouter` | `OPENROUTER_API_KEY` | `openai/gpt-4o-mini` |
| `google` | `GOOGLE_API_KEY` | `gemini-2.0-flash` |
| `claude` | `ANTHROPIC_API_KEY` | `claude-opus-5` |

Chỉ cần cấu hình key của provider đang chọn. Có thể đặt `EMAIL_AGENT_MODEL` thành tên model khác mà provider đó hỗ trợ.

Cấu hình Gmail độc lập với cấu hình LLM. Vì vậy, script `scripts/check_inbox.py` không cần API key AI.

## Sử dụng

### Bước 1: Kiểm tra kết nối Gmail

Chạy script kiểm tra trước khi dùng agent:

```bash
python scripts/check_inbox.py
```

Hoặc truyền một truy vấn Gmail:

```bash
python scripts/check_inbox.py "is:unread newer_than:7d"
```

Ở lần chạy đầu tiên, trình duyệt sẽ mở trang đăng nhập và xin quyền đọc Gmail. Sau khi cấp quyền thành công, thông tin xác thực được lưu trong `token.json` để tái sử dụng cho những lần sau.

Script này hiển thị tối đa 10 email phù hợp và một phần nội dung của email đầu tiên. Nếu script chạy thành công, phần OAuth, Gmail API và parser MIME đang hoạt động.

### Bước 2: Khởi chạy agent

```bash
email-agent
```

Nếu lệnh trên chưa có trong `PATH`, dùng:

```bash
python -m email_agent.cli
```

Nhập `thoat`, `exit`, `quit` hoặc `q` để kết thúc phiên.

Một số câu hỏi mẫu:

- `Hôm nay có email nào cần trả lời gấp không?`
- `Tóm tắt các email chưa đọc trong ba ngày qua, nhóm theo mức độ khẩn cấp.`
- `Tìm email từ bộ phận kế toán trong tháng này và cho biết có hạn chót nào không.`
- `Đọc toàn bộ chuỗi trao đổi về hợp đồng với công ty ABC.`
- `Liệt kê các nhãn hiện có trong hộp thư.`

### Mẫu truy vấn Gmail hữu ích

| Mục đích | Truy vấn |
| --- | --- |
| Email chưa đọc | `is:unread` |
| Email trong hộp thư đến | `in:inbox` |
| Email trong bảy ngày gần đây | `newer_than:7d` |
| Email từ một người cụ thể | `from:sender@example.com` |
| Email có tệp đính kèm | `has:attachment` |
| Email trong tab Chính | `category:primary` |
| Kết hợp nhiều điều kiện | `is:unread newer_than:7d category:primary` |

Xem đầy đủ cú pháp tại [Tìm kiếm trong Gmail](https://support.google.com/mail/answer/7190?hl=vi).

## Cách agent xử lý dữ liệu

Agent hiện cung cấp bốn tool chỉ đọc:

| Tool | Chức năng |
| --- | --- |
| `search_emails` | Tìm email và trả về metadata, không tải toàn bộ nội dung. |
| `get_email` | Đọc nội dung đầy đủ của một email theo ID. |
| `get_thread` | Đọc toàn bộ email trong một chuỗi hội thoại. |
| `list_labels` | Liệt kê các nhãn hiện có trong Gmail. |

Các giới hạn mặc định:

- Mỗi lần tìm kiếm trả về tối đa 25 email.
- Nội dung mỗi email được cắt ở 4.000 ký tự để kiểm soát context và chi phí token.
- Agent chỉ liệt kê tên tệp đính kèm, chưa tải hoặc đọc nội dung tệp.
- Lịch sử trò chuyện chỉ được lưu trong RAM và mất khi thoát chương trình.

Khi agent đọc một email, nội dung liên quan sẽ được gửi đến provider LLM đã chọn để xử lý. Không nên dùng dự án với hộp thư chứa dữ liệu nhạy cảm nếu chính sách của provider hoặc tổ chức của bạn không cho phép.

## Bảo mật

### Quyền Gmail

Scope hiện tại là:

```text
https://www.googleapis.com/auth/gmail.readonly
```

Với scope này, agent không thể gửi, xóa, lưu trữ, gắn nhãn hoặc sửa email. Nếu thay đổi `GMAIL_SCOPES` trong `src/email_agent/config.py`, cần xóa `token.json` và thực hiện lại OAuth vì token cũ không tự nhận thêm quyền.

### Prompt injection trong email

Nội dung email là dữ liệu không đáng tin cậy do người bên ngoài viết. Trước khi gửi nội dung cho model, agent bọc dữ liệu trong thẻ `<email_content>` và system prompt yêu cầu model không làm theo chỉ thị nằm trong email.

Đây là một lớp giảm thiểu rủi ro, không phải bảo đảm an toàn tuyệt đối. Dự án duy trì chế độ chỉ đọc cho đến khi có bước phê duyệt của người dùng đối với các hành động làm thay đổi hộp thư.

### Tệp bí mật

Không commit các tệp sau:

- `.env`: chứa API key của LLM.
- `credentials.json`: chứa OAuth client ID và client secret.
- `token.json`: chứa access token và refresh token của tài khoản Google.

Nếu một tệp bí mật đã bị commit hoặc chia sẻ, hãy thu hồi key/token tương ứng; chỉ xóa tệp khỏi Git là chưa đủ.

## Kiểm thử

Chạy toàn bộ test:

```bash
pytest
```

Hoặc chạy chi tiết hơn:

```bash
pytest -v
```

Bộ test hiện kiểm tra:

- Phân tích MIME, ưu tiên plain text và chuyển HTML thành text.
- Xử lý multipart lồng nhau, giới hạn độ dài body và tên tệp đính kèm.
- Đọc cấu hình Gmail và lựa chọn provider/model.
- Khởi tạo đúng adapter cho từng provider mà không gửi request ra API.

Các test không cần `credentials.json`, `token.json` hoặc API key thật.

## Cấu trúc dự án

```text
.
├── scripts/
│   └── check_inbox.py          # Kiểm tra Gmail độc lập với LLM.
├── src/email_agent/
│   ├── agent/
│   │   ├── graph.py            # Khởi tạo model và LangGraph ReAct agent.
│   │   ├── prompts.py          # System prompt và quy tắc an toàn.
│   │   └── tools.py            # Các LangChain tool chỉ đọc Gmail.
│   ├── email_client/
│   │   ├── auth.py             # OAuth và lưu token Google.
│   │   ├── gmail.py            # Adapter cho Gmail API.
│   │   ├── models.py           # Kiểu dữ liệu email.
│   │   └── parser.py           # Phân tích MIME, base64url và HTML.
│   ├── cli.py                  # Giao diện chat trên terminal.
│   └── config.py               # Cấu hình tập trung từ biến môi trường.
├── tests/                      # Unit test không gọi API bên ngoài.
├── .env.example               # Mẫu cấu hình.
├── pyproject.toml              # Metadata, dependency và entry point.
└── README.md
```

## Xử lý lỗi thường gặp

### `Không tìm thấy credentials.json`

Kiểm tra tệp OAuth đã được tải về, đổi tên đúng và đặt tại đường dẫn trong `GOOGLE_CREDENTIALS_FILE`.

### Không đăng nhập được do ứng dụng đang ở chế độ thử nghiệm

Trong Google Auth platform, thêm tài khoản Gmail vào **Audience > Test users**. Nếu dùng tài khoản Google Workspace, lựa chọn audience còn phụ thuộc chính sách của tổ chức.

### Quyền OAuth không cập nhật

Xóa `token.json`, sau đó chạy lại `python scripts/check_inbox.py` để cấp quyền mới. Chỉ thực hiện việc này khi bạn chủ động thay đổi scope.

### Thiếu API key

Đảm bảo `EMAIL_AGENT_PROVIDER` khớp với biến key tương ứng. Ví dụ, provider `google` cần `GOOGLE_API_KEY`; `OPENAI_API_KEY` không được dùng thay thế.

### `email-agent` không được nhận diện

Kích hoạt đúng môi trường ảo và chạy lại `python -m pip install -e ".[dev]"`. Trong mọi trường hợp, có thể dùng `python -m email_agent.cli`.

### PowerShell chặn script kích hoạt môi trường ảo

Có thể kích hoạt tạm thời cho phiên hiện tại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Chỉ thay đổi execution policy khi bạn hiểu chính sách bảo mật của máy đang sử dụng.

## Lộ trình

- [x] Phase 1 — Gmail adapter và parser MIME, không dùng AI.
- [x] Phase 2 — ReAct agent chỉ đọc và giao diện CLI.
- [ ] Phase 3 — Triage có cấu trúc và gắn nhãn với `gmail.modify`.
- [ ] Phase 4 — Soạn draft, gửi email, phê duyệt bằng `interrupt()` và lưu state bằng `SqliteSaver`.
- [ ] Phase 5 — Ghi nhớ tùy chọn, tạo digest theo lịch và xây dựng bộ eval.

## Giấy phép

Repository hiện chưa khai báo giấy phép sử dụng. Nếu dự định phát hành công khai hoặc nhận đóng góp, hãy bổ sung tệp `LICENSE` phù hợp.
