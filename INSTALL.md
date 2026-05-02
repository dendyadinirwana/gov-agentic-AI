# Install Gov-Agentic AI from Terminal

## True Bootstrap Commands

### macOS / Linux

Interactive install:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/install.sh)
```

Default install:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/install.sh) --defaults
```

### Windows PowerShell

Interactive install:

```powershell
irm https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/install.ps1 | iex
```

### Windows PowerShell with defaults

Clone-style safest path:

```powershell
git clone https://github.com/dendyadinirwana/gov-agentic-AI.git
cd gov-agentic-AI
./install.ps1 -Defaults
```

## Supported Installer Options

- `--defaults`
- `--runtime <openclaw|hermes|codex|claude|antigravity|generic>`
- `--memory <local|mem9|hybrid>`
- `--governance <sandbox|production>`
- `--clusters <comma,separated,clusters>`

## Example

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/dendyadinirwana/gov-agentic-AI/main/install.sh) \
  --defaults \
  --runtime hermes \
  --memory hybrid \
  --governance production \
  --clusters tata-usaha,perencanaan-dan-anggaran,kebijakan-dan-hukum
```
