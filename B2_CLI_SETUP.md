# Backblaze B2 CLI Setup

## Installation

The Backblaze CLI tool `b2` can be installed via Homebrew:

```bash
brew install b2-tools
```

## Authentication

To authenticate with the CLI, you need:

1. **Application Key ID** - From Backblaze dashboard → App Keys
2. **Application Key** - From Backblaze dashboard → App Keys (shown only once!)

### Authenticate via CLI:

```bash
b2 authorize-account <keyID> <applicationKey>
```

Or set environment variables:

```bash
export B2_APPLICATION_KEY_ID=your_key_id
export B2_APPLICATION_KEY=your_application_key
b2 authorize-account
```

### Verify Authentication:

```bash
b2 list-buckets
```

## Important Notes

⚠️ **Security**: The Application Key is shown only once when created. Store it securely!

⚠️ **Credentials**: You'll need to create an Application Key in the Backblaze web dashboard first.

## Common Commands

```bash
# List buckets
b2 list-buckets

# Upload a file
b2 upload-file <bucketName> <localFilePath> <b2FileName>

# Download a file
b2 download-file-by-name <bucketName> <b2FileName> <localFilePath>

# Sync directory
b2 sync <localDirectory> b2://<bucketName>/<remotePath>
```

## Next Steps

Once authenticated, we can:
1. Create a bucket (if not exists)
2. Upload your 36GB of images
3. Configure backend to use B2


