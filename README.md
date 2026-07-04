# ExamForge AI锝滄湡鏈涔犺祫鏂欑敓鎴愬櫒

鎶婅浠躲€佹暀鏉愩€佺瑪璁般€佹壂鎻忚瘯鍗峰拰寰€骞撮锛屼竴閿暣鐞嗘垚鍙洿鎺ュ涔犵殑璧勬枡鍖呫€?
Turn lecture slides, textbooks, notes, scanned papers, and past exams into exam-ready study packs.

浣滆€咃細SiriZhao  
GitHub锛歔https://github.com/SiriZhao](https://github.com/SiriZhao)

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![React](https://img.shields.io/badge/React-19-61dafb)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178c6)
![Windows](https://img.shields.io/badge/Windows-supported-0078d4)
![Release](https://img.shields.io/badge/release-planned-orange)
![Stars](https://img.shields.io/badge/stars-welcome-yellow)

> 褰撳墠鎴浘寰呰ˉ鍏呫€傛寮忓彂甯冨墠寤鸿琛ュ厖棣栭〉銆佺敓鎴愮粨鏋溿€侀珮棰戣€冪偣銆佹ā鎷熷嵎鍜屽ぇ妯″瀷璁剧疆椤垫埅鍥俱€?
## 涓枃浠嬬粛

ExamForge AI 鏄竴涓潰鍚戝ぇ瀛︾敓鏈熸湯澶嶄範鍦烘櫙鐨勬湰鍦?AI 澶嶄範璧勬枡鐢熸垚宸ュ叿銆傚畠涓嶆槸鏅€氱殑鏂囨。闂瓟鏈哄櫒浜猴紝鑰屾槸鍥寸粫鈥滄湡鏈墠濡備綍蹇€熸暣鐞嗗涔犳潗鏂欌€濊繖涓€鍏蜂綋鍦烘櫙锛屽府鍔╃敤鎴蜂粠璇剧▼璧勬枡涓彁鍙栭噸鐐广€佸垎鏋愰珮棰戣€冪偣銆佺敓鎴愭ā鎷熼鍜岃蹇嗗崱鐗囥€?
瀹冪殑榛樿鏈湴鏁寸悊妯″紡鏃犻渶 API Key锛屽彲浠ュ湪鏈湴瀹屾垚鍩虹澶嶄範璧勬枡鐢熸垚锛涘鏋滀綘甯屾湜鑾峰緱鏇磋嚜鐒躲€佹洿瀹屾暣鐨勮〃杈撅紝涔熷彲浠ラ€夋嫨鎺ュ叆澶фā鍨嬫湇鍔¤繘琛屽寮恒€傞」鐩敮鎸?PPTX銆丳DF銆丏OCX銆丮arkdown銆佸浘鐗囧拰鎵弿鐗堣瘯鍗凤紝骞跺彲瀵煎嚭 Markdown銆乄ord銆丳DF 涓?Anki CSV銆?
## English Introduction

ExamForge AI is an open-source local exam preparation assistant for students. It transforms messy course materials into structured study packs, including chapter summaries, high-frequency topics, priority rankings, mock exams, flashcards, and sprint plans.

It is not a generic document chatbot. ExamForge AI is built for final-week exam preparation, works locally by default, supports optional LLM providers, and is designed for lecture slides, notes, textbooks, scanned papers, and past exams.

## v0.4.0 Cloud Web App

ExamForge AI now supports two release shapes:

1. Cloud Web App: deploy the Docker image and let users open a browser link to upload materials, generate review packs, and download Markdown / Word / PDF / Anki CSV.
2. Windows Desktop App: keep the existing exe packaging flow for local private use.

### Online Use

If a deployment sets `PUBLIC_BASE_URL`, share that URL with users. If no public instance is provided, deploy your own instance with Docker, Render, Railway, or Fly.io.

### Docker Deployment

```bash
docker build -t examforge-ai:0.4.0 .
docker run --rm -p 8000:8000 --env-file .env.example examforge-ai:0.4.0
```

Then open:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/api/health`

### Render / Railway / Fly.io

The repository includes a root `Dockerfile`, `render.yaml`, and `fly.toml`.

Required environment variables for cloud mode:

- `APP_MODE=cloud`
- `DEFAULT_LLM_PROVIDER=deepseek`
- `DEFAULT_LLM_MODEL=deepseek-v4-flash`
- `DEFAULT_LLM_BASE_URL=https://api.deepseek.com`
- `DEEPSEEK_API_KEY=your key` (optional, set as a platform secret)
- `MAX_UPLOAD_MB=50`

Railway can build directly from the root Dockerfile. Fly.io can use:

```bash
fly launch
fly secrets set DEEPSEEK_API_KEY=your_key
fly deploy
```

### Cloud vs Desktop

| Mode | Best for | Strengths | Notes |
| --- | --- | --- | --- |
| Cloud Web | Users who want a link | No local OCR/Python/Node/Tesseract/Poppler install | Use HTTPS and consider material privacy |
| Desktop | Private or offline use | Files stay on the user's machine | Requires downloading the exe |
| Local Dev | Contributors | Vite + FastAPI debugging | Requires dev dependencies |

### Privacy, Disclaimer, and Commercial Use Notes

- License: this project uses the MIT License. See [LICENSE](LICENSE).
- Privacy: see [docs/privacy.md](docs/privacy.md).
- Disclaimer: see [docs/disclaimer.md](docs/disclaimer.md).
- Commercial deployments should review third-party dependency licenses, LLM provider terms, OCR provider terms, school/institution rules, data retention policy, and local regulations.
- Public cloud deployments should add rate limiting, access control, monitoring, abuse prevention, and budget controls before large-scale use.

### Why Not Just ChatGPT / NotebookLM?

ExamForge AI first performs OCR, file parsing, past-exam signal extraction, multi-file evidence integration, and quality checks. Then it lets the LLM reorganize the material and exports Word, PDF, Markdown, and Anki CSV. It is a review-pack production workflow, not just a chat box.

| Capability | ExamForge AI | Generic LLM chat |
| --- | --- | --- |
| OCR cleanup | Automated | Depends on upload quality |
| Multi-file evidence integration | Built in | Requires manual prompting |
| Past-exam question type inference | Built in | Unstable |
| Study goal / exam type / detail / style | Built in | Requires repeated prompting |
| Anki CSV export | Built in | Usually manual |
| Word/PDF/Markdown export | Built in | Requires copy/paste formatting |
| Quality scoring and fallback | Built in | Not available |
| Cloud and desktop modes | Built in | Not available |

## 涓轰粈涔堝仛杩欎釜椤圭洰 / Why ExamForge AI

鏈熸湯鍓嶇殑璧勬枡閫氬父涓嶆槸涓€涓共鍑€鐨勭煡璇嗗簱锛岃€屾槸涓€鍫嗗垎鏁ｇ殑 PPT銆佹暀鏉愭埅鍥俱€佽鍫傜瑪璁般€佽€佸笀鍒掗噸鐐广€佹壂鎻忚瘯鍗峰拰寰€骞撮銆傚緢澶氬鐢熺湡姝ｉ渶瑕佺殑涓嶆槸缁х画鍜屾枃妗ｈ亰澶╋紝鑰屾槸灏藉揩寰楀埌涓€浠藉彲浠ョ洿鎺ュ紑濮嬪涔犵殑璧勬枡鍖呫€?
ExamForge AI 鐨勭洰鏍囨槸鎶婅繖浜涢浂鏁ｆ潗鏂欐暣鐞嗘垚鏇村彲鎵ц鐨勫涔犺緭鍑猴細鍏堢湅鍝簺绔犺妭銆佸摢浜涜€冪偣鍑虹幇棰戠巼楂樸€佸彲浠ョ粌鍝簺棰樸€佹渶鍚庡嚑澶╂€庝箞瀹夋帓銆?
Most AI document tools answer questions. ExamForge AI focuses on producing structured review outputs.

## v0.4.0 鏂拌兘鍔?
- 澶嶄範鐩爣閫夋嫨锛? 澶╅€熼€氥€? 澶╁啿鍒恒€? 澶╃郴缁熷涔犮€侀噸鐐硅儗璇点€侀噸鐐瑰埛棰樸€丄nki 鏁寸悊銆佸線骞撮鎶撻噸鐐瑰拰骞宠　妯″紡銆?- 鑰冭瘯绫诲瀷閫夋嫨锛氶棴鍗枫€佸紑鍗枫€佹満鑰冦€佺紪绋嬨€佸疄楠屻€佽鏂?璁鸿堪銆佸彛璇?灞曠ず銆佽绋嬭鏂?鎶ュ憡銆?- 棰樺瀷鍙嶆帹锛氱粨鍚?OCR銆佸線骞撮銆佹枃浠剁被鍨嬪拰棰樺共绾跨储锛岃嚜鍔ㄦ€荤粨鐪熷疄棰樺瀷锛屼笉寮哄埗濂楀浐瀹氶鍨嬪簱銆?- 鐢熸垚璐ㄩ噺璇勫垎锛氬睍绀鸿祫鏂欏畬鏁村害銆佽€冪偣瑕嗙洊搴︺€佹ā鎷熼璐ㄩ噺銆丄nki 鍙敤鎬с€佸鍑哄氨缁害鍜岃瘉鎹暣鍚堝害銆?- 鐢熸垚杩囩▼鎽樿锛氬睍绀烘枃浠跺鐞嗐€丳DF 鏂囨湰灞傘€丱CR銆佺紦瀛樸€佽瘉鎹潡銆侀鍨嬬嚎绱€丄I 璋冪敤鍜屽洖閫€鐘舵€併€?- 閲嶆柊浼樺寲鎶ュ憡锛氭棤闇€閲嶆柊涓婁紶銆丱CR 鎴栬В鏋愭枃浠讹紝鍗冲彲鎸夎儗璇点€佸埛棰樸€丄nki銆侀€熼€氥€佺簿绠€鎴栨ā鎷熷嵎璁粌浼樺寲褰撳墠鎶ュ憡銆?- 鏇村己 Anki 鍗＄墖鍜屾ā鎷熷嵎锛氬崱鐗囨敮鎸佺被鍨嬨€佷紭鍏堢骇銆佹潵婧愭彁绀猴紱妯℃嫙棰樻敮鎸佸叧鑱斾富棰樺拰 source hint銆?
## ExamForge AI 涓庢櫘閫氬ぇ妯″瀷鑱婂ぉ鐨勫尯鍒?
| 鑳藉姏 | ExamForge AI | 鏅€氬ぇ妯″瀷鑱婂ぉ |
| --- | --- | --- |
| OCR 娓呮礂 | 鑷姩澶勭悊 | 渚濊禆鐢ㄦ埛涓婁紶璐ㄩ噺 |
| 澶氭枃浠惰瘉鎹暣鍚?| 鏀寔 | 闇€瑕佹墜鍔ㄨ鏄?|
| 寰€骞撮棰樺瀷鍙嶆帹 | 鏀寔 | 涓嶇ǔ瀹?|
| 澶嶄範鐩爣瀹氬埗 | 鏀寔 | 闇€瑕佸弽澶嶆彁绀?|
| Anki CSV 瀵煎嚭 | 鏀寔 | 閫氬父闇€瑕佹墜鍔ㄦ暣鐞?|
| Word/PDF 瀵煎嚭 | 鏀寔 | 闇€瑕佸鍒舵帓鐗?|
| 璐ㄩ噺璇勫垎 | 鏀寔 | 鏃?|
| 鏈湴瀹夊叏搴曠 | 鏀寔 | 鏃?|

## 鏍稿績鍔熻兘 / Features

| 鍔熻兘 | 涓枃璇存槑 | English |
|---|---|---|
| 澶氭牸寮忎笂浼?| 鏀寔 PPTX銆丳DF銆丏OCX銆丮arkdown銆丳NG銆丣PG銆丣PEG 绛夎绋嬫潗鏂欍€?| Upload slides, PDFs, documents, Markdown notes, and images. |
| 鎵弿浠?OCR | 鏀寔鍥剧墖鍜屾壂鎻忚瘯鍗锋枃鏈瘑鍒紝鍙厤缃湰鍦版垨绗笁鏂?OCR銆?| Extract text from scanned papers and images with configurable OCR providers. |
| 绔犺妭閲嶇偣鎬荤粨 | 浠庤绋嬭祫鏂欎腑鏁寸悊绔犺妭鎽樿銆佸叧閿瘝銆佸叕寮忋€佸涔犲缓璁€?| Generate chapter summaries, keywords, formulas, and study suggestions. |
| 楂橀鑰冪偣鍒嗘瀽 | 鑷姩璇嗗埆鏇村儚寰€骞撮鐨勬潗鏂欙紝骞剁粺璁￠噸澶嶅嚭鐜扮殑棰樺瀷鍜屽叧閿瘝銆?| Detect past-exam-like materials and summarize recurring topics and question types. |
| 绔犺妭浼樺厛绾ф帓搴?| 缁煎悎璧勬枡鍑虹幇棰戠巼銆佸線骞撮棰戠巼鍜岄鍨嬫潈閲嶏紝杈撳嚭 0-100 閲嶈搴︺€?| Rank chapters with priority scores based on material frequency and exam signals. |
| 妯℃嫙鍗风敓鎴?| 鎸夐€夋嫨棰樸€佸～绌洪銆佺畝绛旈銆佽杩伴鐢熸垚妯℃嫙鍗凤紝骞堕檮鍙傝€冪瓟妗堛€?| Generate mock exams with multiple question types and reference answers. |
| Anki 鍗＄墖瀵煎嚭 | 浠庨珮棰戣€冪偣鍜屽悕璇嶈В閲婄敓鎴?CSV 鍗＄墖锛屽瓧娈典负 `Front, Back, Tags`銆?| Export Anki-compatible CSV flashcards from key topics and definitions. |
| Markdown / Word / PDF 瀵煎嚭 | 鏀寔灏嗗涔犳姤鍛婂鍑轰负 Markdown銆乄ord 鍜?PDF銆?| Export study packs as Markdown, Word, and PDF files. |
| 鏈湴杩愯 | 榛樿鍦ㄦ湰鏈哄惎鍔ㄥ墠鍚庣鏈嶅姟锛屾湰鍦版暣鐞嗘ā寮忔棤闇€ API Key銆?| Run locally; local organizing mode works without an API key. |
| 鍙€夊ぇ妯″瀷澧炲己 | 鍙€氳繃閰嶇疆鎺ュ叆 OpenAI 鍏煎鎺ュ彛鎴栬嚜瀹氫箟鏈嶅姟澧炲己鐢熸垚璐ㄩ噺銆?| Optionally connect LLM providers for higher-quality generation. |

## 杞欢鎴浘 / Screenshots

> 褰撳墠鎴浘寰呰ˉ鍏呫€傛寮忓彂甯冨墠寤鸿琛ュ厖棣栭〉銆佺敓鎴愮粨鏋溿€侀珮棰戣€冪偣銆佹ā鎷熷嵎鍜屽ぇ妯″瀷璁剧疆椤垫埅鍥俱€?
| 椤甸潰 | 鐘舵€?|
|---|---|
| 棣栭〉 / Home | 寰呰ˉ鍏?|
| 鐢熸垚缁撴灉 / Report | 寰呰ˉ鍏?|
| 楂橀鑰冪偣 / Topics | 寰呰ˉ鍏?|
| 妯℃嫙鍗?/ Mock Exam | 寰呰ˉ鍏?|
| 澶фā鍨嬭缃?/ LLM Settings | 寰呰ˉ鍏?|

## 蹇€熷紑濮?/ Quick Start

### Windows 鍙屽嚮鍚姩

鏅€氱敤鎴峰彲浠ョ洿鎺ュ弻鍑绘牴鐩綍涓嬬殑锛?
```powershell
.\start.bat
```

鍚姩鑴氭湰浼氭鏌?Python銆丯ode.js銆佺鍙ｅ崰鐢ㄥ拰渚濊禆瀹夎鎯呭喌锛屽苟鎵撳紑鏈湴椤甸潰銆?
### 寮€鍙戠幆澧冩墜鍔ㄥ惎鍔?
鍚庣锛?
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

鍓嶇锛?
```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

娴忚鍣ㄦ墦寮€锛?
```text
http://127.0.0.1:5173
```

### 涓€閿紑鍙戝惎鍔ㄨ剼鏈?
```powershell
.\scripts\start-dev.ps1
```

鐜璇婃柇锛?
```powershell
.\scripts\doctor.ps1
```

## 浣跨敤绀轰緥 / Try with Demo Files

椤圭洰鎻愪緵浜嗚櫄鏋勮绋嬬ず渚嬶紝閫傚悎 GitHub 灞曠ず鍜屾湰鍦版祴璇曪紝涓嶅寘鍚湡瀹炶绋嬬増鏉冨唴瀹癸細

- `examples/demo_course_material.md`
- `examples/demo_past_exam.md`
- `examples/demo_output.md`

浣犲彲浠ュ惎鍔ㄥ簲鐢ㄥ悗涓婁紶 `examples` 鐩綍涓殑 demo 鏂囦欢锛岃瀵熺珷鑺傞噸鐐广€侀珮棰戣€冪偣銆佹ā鎷熷嵎鍜?Anki 鍗＄墖鐨勭敓鎴愭晥鏋溿€?
## 鏀寔鐨勬枃浠剁被鍨?/ Supported Files

| 绫诲瀷 | 鎵╁睍鍚?| 璇存槑 |
|---|---|---|
| 璇句欢 | `.pptx` | 瑙ｆ瀽骞荤伅鐗囨枃瀛楀唴瀹广€?|
| 鏂囨。 | `.pdf`, `.docx`, `.md` | 瑙ｆ瀽鏁欐潗鎽樺綍銆佽鍫傜瑪璁般€佸涔犺祫鏂欍€?|
| 鍥剧墖 | `.png`, `.jpg`, `.jpeg` | 鍙厤鍚?OCR 璇嗗埆鎵弿浠舵垨鎷嶇収璇曞嵎銆?|
| 寰€骞撮 | `.pdf`, `.docx`, `.md`, 鍥剧墖 | 绯荤粺浼氭牴鎹枃浠跺悕鍜屽唴瀹圭壒寰佸垽鏂槸鍚︽洿鍍忓線骞磋瘯鍗枫€?|

## OCR Providers

榛樿鎯呭喌涓嬶紝鏂囧瓧鐗?PDF銆丳PTX銆丏OCX 鍜?Markdown 涓嶄緷璧?OCR銆傚鐞嗘壂鎻忚瘯鍗锋垨鍥剧墖鏃讹紝鍙互閫夋嫨 OCR Provider锛?
| Provider | 鐢ㄩ€?| 澶囨敞 |
|---|---|---|
| Local Tesseract | 鏈湴 OCR | 闇€瑕佹湰鏈哄畨瑁?Tesseract 鎴栧噯澶囧搴旇瑷€鏁版嵁銆?|
| RapidOCR | 鏈湴 OCR | 渚濊禆 `rapidocr_onnxruntime`銆?|
| Baidu OCR | 浜?OCR | 闇€瑕佽嚜琛岄厤缃櫨搴?OCR 鍑嵁銆?|
| OpenAI Vision | 瑙嗚妯″瀷 OCR | 闇€瑕佸吋瀹圭殑 API Key 鍜屾帴鍙ｅ湴鍧€銆?|
| Custom API | 鑷畾涔?OCR | 閫傚悎鎺ュ叆瀛︽牎鎴栦釜浜洪儴缃茬殑 OCR 鏈嶅姟銆?|

OCR 鏄彲閫夎兘鍔涖€傛病鏈?OCR 鏃讹紝杞欢浠嶅彲澶勭悊鏂囧瓧鐗堣绋嬫潗鏂欍€?
## LLM Providers

鏈湴鏁寸悊妯″紡鏃犻渶 API Key锛岄€傚悎鍏堝揩閫熺敓鎴愭湰鍦板畨鍏ㄥ簳绋裤€? 
濡傛灉闇€瑕佹洿鑷劧鐨勬€荤粨琛ㄨ揪銆佹洿瀹屾暣鐨勯鐩В閲婏紝鍙互鍦ㄩ珮绾ц缃腑閰嶇疆 OpenAI 鍏煎鎺ュ彛鎴栬嚜瀹氫箟澶фā鍨嬫湇鍔°€?
寤鸿閫氳繃鐜鍙橀噺鎴栨湰鍦伴厤缃紶鍏ュ瘑閽ワ紝涓嶈鎶?API Key 鎻愪氦鍒?GitHub銆?
```powershell
copy .env.example .env
```

## 澶фā鍨嬪寮鸿鏄?/ LLM Enhancement

ExamForge AI 榛樿鏀寔鏈湴鏁寸悊妯″紡锛屾棤闇€ API Key锛屼篃鍙互鏈湴鐢熸垚鍩虹澶嶄範璧勬枡銆? 
濡傛灉浣犲笇鏈涘緱鍒版洿绯荤粺銆佹洿鑷劧銆佹洿鎺ヨ繎浜哄伐鏁寸悊鐨勫涔犺祫鏂欙紝鍙互寮€鍚ぇ妯″瀷澧炲己銆?
澶фā鍨嬪寮哄彲浠ユ彁鍗囷細

- 绔犺妭鎬荤粨璐ㄩ噺
- 楂橀鑰冪偣褰掔撼
- 绔犺妭浼樺厛绾цВ閲?- 妯℃嫙棰樿川閲?- Anki 鍗＄墖璐ㄩ噺
- 鑰冨墠鍐插埡璁″垝绯荤粺鎬?
DeepSeek 鎺ㄨ崘閰嶇疆锛?
- Provider锛欴eepSeek
- Base URL锛歚https://api.deepseek.com`
- Model锛歚deepseek-v4-flash`

鍏煎璇存槑锛歚deepseek-chat` 鍜?`deepseek-reasoner` 浣滀负鏃у吋瀹规ā鍨嬪悕淇濈暀銆傚鏋滀綘宸茬粡鎵嬪姩濉啓杩欎簺妯″瀷鍚嶏紝绋嬪簭涓嶄細寮哄埗瑕嗙洊銆?
閰嶇疆姝ラ锛?
1. 鎵撳紑楂樼骇璁剧疆
2. 鍚敤澶фā鍨嬪寮?3. 閫夋嫨鏈嶅姟鍟?4. 濉啓 API Key銆丅ase URL 鍜屾ā鍨嬪悕绉?5. 鐐瑰嚮鈥滄祴璇曞ぇ妯″瀷杩炴帴鈥?6. 杩炴帴鎴愬姛鍚庨噸鏂扮敓鎴?
闅愮鎻愰啋锛氫娇鐢ㄤ簯绔ぇ妯″瀷鎴栦簯绔?OCR 鏃讹紝涓婁紶璧勬枡鍐呭鍙兘浼氬彂閫佺粰瀵瑰簲鏈嶅姟鍟嗗鐞嗐€傝鍕夸笂浼犳晱鎰熶釜浜轰俊鎭€佹棤鎺堟潈璧勬枡鎴栦笉閫傚悎涓婁紶鍒扮涓夋柟鏈嶅姟鐨勫唴瀹广€?
Rule-based mode works without an API key. LLM enhancement is optional and can improve summaries, topic extraction, mock exams, flashcards, and sprint plans.

## 瀵煎嚭鏍煎紡 / Export Formats

| 鏍煎紡 | 鏂囦欢绫诲瀷 | 浣跨敤鍦烘櫙 |
|---|---|---|
| Markdown | `.md` | 閫傚悎缁х画缂栬緫銆佸彂甯冨埌绗旇杞欢鎴栫増鏈鐞嗐€?|
| Word | `.docx` | 閫傚悎鎵撳嵃銆佷氦浣滀笟寮忔暣鐞嗘垨浜屾鎺掔増銆?|
| PDF | `.pdf` | 閫傚悎鍥哄畾鏍煎紡鍒嗕韩鍜屽綊妗ｃ€?|
| Anki | `.csv` | 閫傚悎瀵煎叆 Anki锛屽瓧娈典负 `Front, Back, Tags`銆?|

## 椤圭洰缁撴瀯 / Project Structure

```text
.
鈹溾攢 backend/                 # FastAPI 鍚庣
鈹? 鈹溾攢 app/                  # API銆佽В鏋愩€丱CR銆佺敓鎴愩€佸鍑烘湇鍔?鈹? 鈹溾攢 tests/                # 鍚庣娴嬭瘯
鈹? 鈹溾攢 uploads/              # 鏈湴涓婁紶鐩綍锛屼粎淇濈暀 .gitkeep
鈹? 鈹斺攢 outputs/              # 鏈湴瀵煎嚭鐩綍锛屼粎淇濈暀 .gitkeep
鈹溾攢 frontend/                # React + TypeScript 鍓嶇
鈹? 鈹斺攢 src/                  # 椤甸潰銆佺粍浠躲€佹牱寮忓拰娴嬭瘯
鈹溾攢 examples/                # 铏氭瀯绀轰緥鏉愭枡
鈹溾攢 scripts/                 # 鍚姩銆佹祴璇曘€佹竻鐞嗐€佹墦鍖呰剼鏈?鈹溾攢 installer/               # Inno Setup 瀹夎鍖呴厤缃?鈹溾攢 docs/                    # 椤圭洰鏂囨。
鈹溾攢 desktop_main.py          # Windows exe 鍚姩鍏ュ彛
鈹斺攢 ExamReviewAgent.spec     # PyInstaller 鎵撳寘閰嶇疆
```

## 寮€鍙戣€呰繍琛屾柟寮?/ Development

瀹夎骞惰繍琛屽悗绔祴璇曪細

```powershell
cd backend
python -m pytest
```

瀹夎骞惰繍琛屽墠绔祴璇曪細

```powershell
cd frontend
npm install
npm run test -- --run
```

鍓嶇鏋勫缓锛?
```powershell
cd frontend
npm run build
```

涓€閿祴璇曞悗绔€佸墠绔拰鍓嶇鏋勫缓锛?
```powershell
.\scripts\test-all.ps1
```

娓呯悊鏈湴涓婁紶銆佸鍑哄拰缂撳瓨锛?
```powershell
.\scripts\reset-local-data.ps1
```

## Windows exe 浣跨敤璇存槑 / Windows App

鍙戝竷 GitHub Release 鍚庯紝鏅€氱敤鎴峰彲浠ヤ粠 Release 椤甸潰涓嬭浇浠ヤ笅鏂囦欢锛?
- `ExamForgeAISetup-0.4.0.exe`锛氭帹鑽愭櫘閫氱敤鎴蜂笅杞斤紝瀹夎鍚庝粠寮€濮嬭彍鍗曞惎鍔ㄣ€?- `ExamForgeAI.exe`锛氫究鎼虹増锛屽彲鐩存帴杩愯娴嬭瘯銆?
瀹夎鍚庡惎鍔細

```text
ExamForge AI 鏈熸湯澶嶄範璧勬枡鐢熸垚鍣?```

杩愯鏁版嵁淇濆瓨鍦ㄧ敤鎴风洰褰曪紝涓嶆薄鏌撳畨瑁呯洰褰曪細

```text
%LOCALAPPDATA%\ExamForgeAI
```

鍖呭惈锛?
- `uploads`锛氭湰鍦颁笂浼犳枃浠躲€?- `outputs`锛氬鍑虹殑澶嶄範璧勬枡銆?- `logs`锛氬惎鍔ㄥ拰杩愯鏃ュ織銆?
## 鎵撳寘 exe 鏂瑰紡 / Packaging

鏈湴鎵撳寘 Windows exe锛?
```powershell
.\scripts\build-windows.ps1
```

璺宠繃娴嬭瘯鎵撳寘锛?
```powershell
.\scripts\build-windows.ps1 -SkipTests
```

璺宠繃瀹夎鍖呯敓鎴愶細

```powershell
.\scripts\build-windows.ps1 -SkipInstaller
```

鎴愬姛鍚庤緭鍑猴細

```text
dist\ExamForgeAI.exe
dist\installer\ExamForgeAISetup-0.4.0.exe
```

鎵撳寘璇存槑瑙侊細

```text
docs/windows-packaging.md
```

## GitHub Release

鎺ㄩ€佸舰濡?`v0.4.0` 鐨?tag 鍚庯紝GitHub Actions 浼氬皾璇曞湪 Windows 鐜涓瀯寤?exe 骞跺垱寤?Release锛?
```powershell
git tag v0.4.0
git push origin v0.4.0
```

濡傛灉椤圭洰浠撳簱灏氭湭寮€鍚?Actions 鎴?Release 鏉冮檺锛岃鍏堟鏌?`.github/workflows/windows-release.yml` 鐨勬潈闄愰厤缃€?
## Roadmap

浠ヤ笅鏂瑰悜浼氱户缁凯浠ｏ紝鍏蜂綋瀹炵幇浠?Release 鐗堟湰涓哄噯锛?
- 鏇寸ǔ瀹氱殑鎵弿浠剁増闈㈠垎鏋愬拰棰樼洰鍒囧垎銆?- 鏇寸粏绮掑害鐨勭珷鑺傛槧灏勫拰璇剧▼澶х翰璇嗗埆銆?- 鏇村鏈湴妯″瀷鍜屽浗浜уぇ妯″瀷 Provider銆?- 鏇村畬鏁寸殑妗岄潰绔綋楠岋紝渚嬪鎵樼洏鍥炬爣銆佽嚜鍔ㄦ洿鏂板拰绂荤嚎妯″瀷绠＄悊銆?- 鏇翠赴瀵岀殑瀵煎嚭妯℃澘鍜屾墦鍗版牱寮忋€?- CI 鐘舵€併€佽鐩栫巼鍜?Star History 鍥捐〃鎺ュ叆鐪熷疄浠撳簱鏁版嵁銆?
## 甯歌闂 / FAQ

### 娌℃湁 API Key 鑳界敤鍚楋紵

鍙互銆傛湰鍦版暣鐞嗘ā寮忔棤闇€ API Key锛屽彲浠ョ敓鎴愬熀纭€澶嶄範璧勬枡銆傚ぇ妯″瀷澧炲己鏄彲閫夊姛鑳姐€?
### 鎵弿璇曞嵎涓€瀹氳兘璇嗗埆鍚楋紵

OCR 鏁堟灉鍙栧喅浜庡浘鐗囨竻鏅板害銆佽瑷€鏁版嵁銆佺増闈㈠鏉傚害鍜屾墍閫?Provider銆傛枃瀛楃増 PDF銆丳PTX銆丏OCX銆丮arkdown 閫氬父鏇寸ǔ瀹氥€?
### 杩欎釜椤圭洰浼氭壙璇烘彁鍒嗘垨鎶奸鍚楋紵

涓嶄細銆侲xamForge AI 鐨勭洰鏍囨槸甯姪鏁寸悊澶嶄範鏉愭枡鍜岀敓鎴愮粌涔犲唴瀹癸紝涓嶆壙璇鸿€冭瘯缁撴灉锛屼篃涓嶆彁渚涒€滃繀涓娂棰樷€濈被琛ㄨ堪銆?
### 涓婁紶鏂囦欢浼氫紶鍒颁簯绔悧锛?
榛樿鏈湴鏁寸悊妯″紡鍜屾湰鍦拌В鏋愬湪鏈満杩愯銆傚鏋滀綘涓诲姩閰嶇疆浜?OCR 鎴栧ぇ妯″瀷鏈嶅姟锛岀浉鍏虫枃鏈垨鍥剧墖鍙兘浼氬彂閫佺粰瀵瑰簲 Provider锛岃鑷纭鏈嶅姟鏉℃鍜岄殣绉佽姹傘€?
### Windows 棣栨鍚姩寰堟參鎬庝箞鍔烇紵

棣栨鍚姩鍙兘闇€瑕佸垵濮嬪寲渚濊禆銆丱CR 缁勪欢鎴栨湰鍦版湇鍔°€傚彲浠ヨ繍琛岃瘖鏂剼鏈煡鐪嬬幆澧冪姸鎬侊細

```powershell
.\scripts\doctor.ps1
```

## 璐＄尞 / Contributing

娆㈣繋鎻愪氦 Issue銆佸缓璁拰 Pull Request銆傚缓璁湪鎻愪氦鍓嶈繍琛岋細

```powershell
.\scripts\test-all.ps1
```

濡傛灉浣犵殑鏀瑰姩娑夊強 Windows 鎵撳寘锛岃鍚屾椂杩愯锛?
```powershell
.\scripts\build-windows.ps1
```

鎻愪氦鍐呭璇烽伩鍏嶅寘鍚細

- API Key銆乼oken銆乻ecret銆?- 鐪熷疄璇剧▼鏉愭枡銆佺湡瀹炶瘯鍗锋垨鐗堟潈鍙楅檺鏂囦欢銆?- 涓汉闅愮鏂囦欢銆佹湰鍦拌矾寰勫拰鏃ュ織銆?- `node_modules/`銆乣.venv/`銆乣dist/`銆乣build/` 绛夋瀯寤轰骇鐗┿€?
## 浣滆€呬俊鎭?/ Author

浣滆€咃細SiriZhao  
GitHub锛歔https://github.com/SiriZhao](https://github.com/SiriZhao)

ExamForge AI 淇濈暀鑻辨枃椤圭洰鍚嶏紝涓枃鍚嶄负鈥滄湡鏈涔犺祫鏂欑敓鎴愬櫒鈥濄€傞」鐩富瑕侀潰鍚戜腑鏂囧ぇ瀛︾敓鐢ㄦ埛锛屽悓鏃朵繚鐣欒嫳鏂囦粙缁嶏紝鏂逛究鍥介檯鐢ㄦ埛鐞嗚В鍜屾悳绱€?
## License

鏈」鐩噰鐢?MIT License锛岃瑙?[LICENSE](LICENSE)銆?

