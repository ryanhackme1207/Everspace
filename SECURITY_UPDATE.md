# Security Notice: API Keys Removed

## Important Security Update

The hardcoded Tenor API key has been removed from the codebase for security reasons. To enable GIF search functionality:

### Getting Your Own Tenor API Key (Free)

1. **Visit Tenor Developer Portal**
   - Go to: https://tenor.com/developer/keyregistration
   - Sign up for a free account (uses Google Sign-In)

2. **Register Your Application**
   - Fill in the application details
   - You'll receive an API key instantly

3. **Set Up the API Key**

   **For Local Development:**
   - Create a `.env` file in the project root (copy from `.env.example`)
   - Add your key: `TENOR_API_KEY=your_actual_api_key_here`
   
   **For Production (Render/Heroku):**
   - Add as environment variable in your hosting platform
   - Name: `TENOR_API_KEY`
   - Value: Your actual API key

4. **Restart Your Server**
   ```bash
   python manage.py runserver
   ```

### What Happens Without the Key?

- Emoji picker will still work perfectly ✅
- GIF search button will show a message: "GIF search not configured"
- All other chat features remain fully functional

### Why Was This Changed?

Hardcoded API keys in public repositories are a security risk:
- Anyone can use your key and exhaust your rate limits
- Keys can be revoked by the service provider
- It's against best practices for production applications

### Tenor API Free Tier

- **50 million requests per month** (more than enough!)
- No credit card required
- Perfect for personal/small projects

---

**Note:** The previously exposed API key has been rotated. If you forked this repo before this update, please update your code.
