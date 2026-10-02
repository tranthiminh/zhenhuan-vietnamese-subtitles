# Workflow cloud-first

## Mục tiêu

Giảm tối đa việc chạy nặng trên máy cá nhân. GitHub Actions chỉ tải audio tạm thời vào runner, gọi Gemini API, tạo output rồi upload artifact.

## Dữ liệu không commit

Không commit video/audio phim có bản quyền vào repository. `.gitignore` đã chặn các định dạng media phổ biến.

## API key

Đặt `GEMINI_API_KEY` trong GitHub Actions Secrets. Không ghi API key vào file `.env` rồi commit.

## Hai lượt transcription

### Accuracy pass

- model: `gemini-3.5-transcribe`
- `language_codes`: `zh-CN`
- `custom_vocabulary`: lấy từ toàn bộ glossary
- không bật word timestamps

### Timing pass

- model: `gemini-3.5-transcribe`
- `language_codes`: `zh-CN`
- word-level timestamps
- không dùng custom vocabulary

### Alignment + Vietnamese translation

Một Gemini general model nhận cả hai output cùng glossary và style guide. Nó được yêu cầu ưu tiên văn bản từ accuracy pass nhưng dùng timing pass để xây timecode SRT.
