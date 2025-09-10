# 🔒 Code Signing Guide for Looper

This guide explains how to code sign your Looper executable to prevent browsers and antivirus software from flagging it as a virus.

## 🎯 Why Code Sign?

- **Prevents false positives**: Stops Chrome, Firefox, and other browsers from blocking your download
- **Builds trust**: Users see a verified publisher instead of "Unknown Publisher"
- **Professional appearance**: Makes your software look legitimate and trustworthy
- **Windows SmartScreen**: Helps build reputation with Microsoft's security system

## 📋 Code Signing Options

### 1. Commercial Code Signing Certificate (Recommended)

**Best for:** Professional distribution, maximum trust

**Top Providers:**
- **DigiCert** (~$400-600/year) - Most trusted, works everywhere
- **Sectigo** (~$200-400/year) - Good reputation, more affordable  
- **GlobalSign** (~$300-500/year) - Reliable, good support
- **SSL.com** (~$200-300/year) - Budget-friendly option

**Requirements:**
- Business registration (LLC, Corporation, etc.)
- Identity verification documents
- Business address verification
- Phone verification

### 2. Self-Signed Certificate (Free but Limited)

**Best for:** Testing, internal distribution, learning

**Limitations:**
- Browsers will still show warnings
- Users need to manually trust the certificate
- Not suitable for public distribution

## 🛠️ Implementation

### Quick Start (No Signing)

```bash
# Build without code signing
python build_exe_with_signing.py
```

### With Code Signing

```bash
# Build with code signing
python build_exe_with_signing.py --cert "path/to/certificate.pfx" --password "your_password"
```

### Using the Batch File

```bash
# No signing
build_looper_signed.bat

# With certificate file
build_looper_signed.bat "C:\certs\mycert.pfx" "mypassword"

# With verification
build_looper_signed.bat "C:\certs\mycert.pfx" "mypassword" --verify
```

## 📜 Certificate Setup

### 1. Purchase a Certificate

1. Choose a Certificate Authority (CA) from the list above
2. Complete the business verification process
3. Download your certificate file (usually `.pfx` or `.p12` format)

### 2. Install Certificate (Optional)

You can either:
- **Use the certificate file directly** (recommended for CI/CD)
- **Install it in Windows Certificate Store** (for local development)

#### Install in Certificate Store:
1. Double-click your `.pfx` file
2. Follow the Certificate Import Wizard
3. Choose "Local Machine" or "Current User"
4. Enter your certificate password
5. Note the certificate's "Subject" name for use in scripts

### 3. Verify Installation

```bash
# List certificates in store
certlm.msc

# Or use PowerShell
Get-ChildItem -Path Cert:\LocalMachine\My
```

## 🔧 Advanced Configuration

### Custom Timestamp Server

```bash
python build_exe_with_signing.py --cert "cert.pfx" --password "pass" --timestamp "http://timestamp.sectigo.com"
```

### Verify Signature After Building

```bash
python build_exe_with_signing.py --cert "cert.pfx" --password "pass" --verify
```

### Manual Signing (if needed)

```bash
# Sign an existing executable
signtool.exe sign /f "certificate.pfx" /p "password" /fd SHA256 /tr "http://timestamp.digicert.com" /td SHA256 "Looper_v0.91_by_Ghosteam.exe"

# Verify signature
signtool.exe verify /pa "Looper_v0.91_by_Ghosteam.exe"
```

## 🏢 Business Setup for Certificate Purchase

### Required Documents:
- **Business Registration**: Articles of Incorporation, LLC filing, etc.
- **Business License**: If required in your jurisdiction
- **Proof of Address**: Utility bill, bank statement, etc.
- **Identity Verification**: Government-issued ID
- **Phone Verification**: Business phone number

### Business Structure Options:
- **Sole Proprietorship**: Easiest to set up, but may have limitations
- **LLC**: Good balance of simplicity and protection
- **Corporation**: Most professional, but more complex

### Cost Breakdown:
- **Certificate**: $200-600/year
- **Business Registration**: $50-500 (varies by state/country)
- **Total First Year**: $250-1100

## 🚀 Distribution Strategy

### 1. Immediate Benefits
- ✅ No more browser download warnings
- ✅ "Verified Publisher" instead of "Unknown Publisher"
- ✅ Professional appearance

### 2. Long-term Benefits
- ✅ Windows SmartScreen reputation building
- ✅ Reduced antivirus false positives
- ✅ Increased user trust and download rates

### 3. Best Practices
- **Always timestamp your signatures** (prevents expiration issues)
- **Use SHA-256 signing** (modern standard)
- **Test on clean Windows VMs** before distribution
- **Submit to antivirus vendors** for whitelisting if needed

## 🐛 Troubleshooting

### Common Issues

#### "signtool.exe not found"
```bash
# Install Windows SDK
# Or install Visual Studio Build Tools
# Or add to PATH: C:\Program Files (x86)\Windows Kits\10\bin\x64
```

#### "Certificate not found"
- Verify the certificate file path
- Check if the certificate is installed in the correct store
- Ensure you're using the correct certificate format (.pfx, .p12)

#### "Invalid certificate"
- Check certificate expiration date
- Verify the certificate is for code signing (not SSL)
- Ensure the certificate chain is complete

#### "Timestamp server error"
- Try a different timestamp server:
  - `http://timestamp.digicert.com`
  - `http://timestamp.sectigo.com`
  - `http://timestamp.globalsign.com/tsa/r6advanced1`

### Verification Commands

```bash
# Check certificate details
certutil -dump certificate.pfx

# Verify executable signature
signtool.exe verify /pa /v "Looper_v0.91_by_Ghosteam.exe"

# Check certificate store
certlm.msc
```

## 💡 Pro Tips

### 1. Automated Signing
Set up your build process to automatically sign:
```bash
# In your CI/CD pipeline
python build_exe_with_signing.py --cert "%CERT_PATH%" --password "%CERT_PASSWORD%"
```

### 2. Multiple Certificates
If you have multiple certificates, specify the exact one:
```bash
# Use certificate by subject name
python build_exe_with_signing.py --cert "CN=Your Company Name"
```

### 3. Certificate Backup
Always backup your certificate and private key securely:
- Store in encrypted password manager
- Use hardware security modules (HSM) for enterprise
- Never commit certificates to version control

### 4. Testing
Test your signed executable on:
- Clean Windows 10/11 VMs
- Different antivirus software
- Various browsers (Chrome, Firefox, Edge)
- Windows Defender SmartScreen

## 📊 Expected Results

| Scenario | Before Signing | After Signing |
|----------|----------------|---------------|
| Chrome Download | ⚠️ "This file is not commonly downloaded" | ✅ Clean download |
| Windows SmartScreen | ⚠️ "Windows protected your PC" | ✅ "Verified publisher" |
| Antivirus | ⚠️ May flag as suspicious | ✅ Generally trusted |
| User Trust | ❌ "Unknown Publisher" | ✅ "Verified Publisher" |

## 🎉 Success Checklist

- [ ] Certificate purchased and installed
- [ ] Build script configured with certificate
- [ ] Executable builds and signs successfully
- [ ] Signature verification passes
- [ ] Tested on clean Windows system
- [ ] No browser warnings on download
- [ ] Windows shows "Verified Publisher"

---

**Need Help?** Check the troubleshooting section above or consult your certificate provider's documentation.

**Looper v0.91 by Ghosteam** - Secure Distribution Made Simple
