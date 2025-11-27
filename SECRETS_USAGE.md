# Secrets Manager Usage Guide

The Intelligent Research Agent includes a built-in encrypted secrets manager to securely store API keys on disk.

## How It Works

The secrets manager uses **Fernet symmetric encryption** (from the `cryptography` library) to:
1. Generate a master encryption key (`master.key`)
2. Encrypt secrets into a file (`secrets.enc`)
3. Decrypt secrets when needed

## Security Benefits

- **Encrypted Storage**: API keys are never stored in plain text
- **No Version Control Exposure**: `master.key` and `secrets.enc` are gitignored
- **Fallback Chain**: Secrets Manager → Environment Variables → Manual Input

## API Endpoints

### Store a Secret

**POST** `/api/secrets/set`

```json
{
  "key": "OPENAI_API_KEY",
  "value": "sk-your-actual-key-here"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Secret 'OPENAI_API_KEY' stored securely."
}
```

### Retrieve a Secret

**GET** `/api/secrets/get/{key}`

**Example:** `/api/secrets/get/OPENAI_API_KEY`

**Response:**
```json
{
  "key": "OPENAI_API_KEY",
  "value": "sk-your-actual-key-here"
}
```

## Using with cURL

### Store API Keys

```bash
# Store OpenAI key
curl -X POST http://localhost:8000/api/secrets/set \
  -H "Content-Type: application/json" \
  -d '{"key": "OPENAI_API_KEY", "value": "sk-your-key"}'

# Store Gemini key
curl -X POST http://localhost:8000/api/secrets/set \
  -H "Content-Type: application/json" \
  -d '{"key": "GEMINI_API_KEY", "value": "your-gemini-key"}'

# Store Serper key
curl -X POST http://localhost:8000/api/secrets/set \
  -H "Content-Type: application/json" \
  -d '{"key": "SERPER_API_KEY", "value": "your-serper-key"}'
```

### Retrieve a Key

```bash
curl http://localhost:8000/api/secrets/get/OPENAI_API_KEY
```

## Priority Chain

When the API needs an API key, it checks in this order:

1. **Request Parameter** - API key passed in the request
2. **Secrets Manager** - Encrypted storage (`secrets.enc`)
3. **Environment Variable** - `.env` file
4. **Error** - Returns 400 if not found

## Files Created

- `master.key` - Encryption key (keep this safe!)
- `secrets.enc` - Encrypted API keys

> ⚠️ **Important**: Never commit `master.key` or `secrets.enc` to version control!

## Best Practices

### For Development
- Use `.env` file for quick testing
- Or use secrets manager for better security

### For Production
1. **Use Secrets Manager** for API keys
2. **Backup `master.key`** securely (if lost, you can't decrypt secrets)
3. **Set restrictive file permissions**:
   ```bash
   chmod 600 master.key secrets.enc
   ```
4. **Rotate keys regularly**

## Example Workflow

1. **Start the server**:
   ```bash
   cd backend
   python main.py
   ```

2. **Store your API keys** (one-time setup):
   ```bash
   curl -X POST http://localhost:8000/api/secrets/set \
     -H "Content-Type: application/json" \
     -d '{"key": "OPENAI_API_KEY", "value": "sk-proj-..."}'
   ```

3. **Use the app** - Keys will be automatically retrieved from encrypted storage

4. **No need to input keys** in the frontend anymore!

## Troubleshooting

### "Error loading secrets"
- The `secrets.enc` file may be corrupted
- Delete both `master.key` and `secrets.enc` and re-add your secrets

### "Secret not found"
- The key hasn't been stored yet
- Use `/api/secrets/set` to add it

### Lost `master.key`
- You cannot recover encrypted secrets without the master key
- Delete `secrets.enc` and re-add all your secrets

## Migration from .env

If you're currently using a `.env` file:

1. **Keep your `.env`** as a backup
2. **Store secrets** via the API
3. **Test** that everything works
4. **(Optional)** Remove keys from `.env`

The app will continue to work with either method!
