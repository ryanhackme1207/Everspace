# Tenor API Setup - EverSpace Project

## Status: ✅ CONFIGURED & TESTED

Your Tenor API key has been successfully integrated with the EverSpace chat application.

### API Key Information
- **Key Type**: Google Tenor API (v2)
- **API Endpoint**: `https://tenor.googleapis.com/v2/`
- **Authentication**: Requires Referer header (`https://everspace-izi3.onrender.com`)

### Configuration Files Updated

#### 1. `chat/views.py` - gif_search() endpoint
- Migrated from Tenor v1 API (`api.tenor.com/v1`) to **Google Tenor API v2** (`tenor.googleapis.com/v2`)
- Added Referer header requirement for API calls
- Updated error handling for 403 Forbidden (referer validation)
- Supports both:
  - **Trending**: Empty query or `?q=` with <2 characters
  - **Search**: `?q=search_term` with 2+ characters

#### 2. `start.sh` - Deployment Startup Script
- API key already configured: `AIzaSyA3iOLnafGrcexjOUxYOGtALbgEQ_258Gs`
- Environment variable: `TENOR_API_KEY`
- Can be overridden on Render dashboard if needed

### Testing Results

#### ✅ Trending GIFs (Featured)
```
Endpoint: https://tenor.googleapis.com/v2/featured
Status: 200 OK
Results: 20 GIFs returned
```

#### ✅ Search GIFs
```
Endpoint: https://tenor.googleapis.com/v2/search?q=cat
Status: 200 OK
Results: 20 GIFs for "cat" returned
```

### How It Works in Chat

1. **User clicks GIF button** in chat interface
2. **Frontend loads trending GIFs** by calling `/gif-search/` (no query parameter)
3. **User types search term** (minimum 2 characters)
4. **Frontend calls `/gif-search/?q=search_term`**
5. **Backend makes request** to Google Tenor API v2 with:
   - API key: `AIzaSyA3iOLnafGrcexjOUxYOGtALbgEQ_258Gs`
   - Referer: `https://everspace-izi3.onrender.com`
   - Media filter: `tinygif,gif` (prioritizes tiny GIF format)
6. **Response returned** to frontend with format:
   ```json
   {
     "results": [
       {"url": "https://media.tenor.com/...", "desc": "GIF description"},
       ...
     ]
   }
   ```
7. **User selects GIF** and it's sent in chat message

### Render Deployment

When deploying to Render:

1. API key is automatically set via `start.sh`
2. No additional environment variables needed (optional override possible)
3. Daphne server starts after migrations and static file collection
4. GIF search ready immediately upon deployment

### Local Development

To test locally:
```bash
# Ensure TENOR_API_KEY is set in .env or start.sh
python manage.py runserver

# Navigate to chat room
# Click GIF button
# Should load trending GIFs immediately
# Type search term to search for specific GIFs
```

### Response Format Details

Each GIF result includes:
- **url**: Direct link to GIF file (tinygif → gif → webm format priority)
- **desc**: Description/title truncated to 140 characters

Media format priority:
1. `tinygif` (smallest, ~10KB)
2. `gif` (standard)
3. `webm` (video format fallback)

### Error Handling

The endpoint gracefully handles:
- Missing API key: Returns error message
- Invalid key: 401 Unauthorized with error
- Referer denied: 403 Forbidden with error
- Network timeout: Timeout error message
- Rate limiting: Returns empty results safely

### Important Notes

⚠️ **For Development/Production**: 
- The API key is for **EverSpace project only**
- Do not share this key publicly
- Treat as sensitive configuration (like database passwords)
- The Referer header restriction limits usage to `everspace-izi3.onrender.com` domain

### Next Steps

1. ✅ Push changes to GitHub
2. ✅ Deploy to Render
3. ✅ Test GIF search in deployed chat
4. ✅ Verify trending GIFs load on open GIF picker
5. ✅ Verify search works with test queries

---

**Last Updated**: November 5, 2025
**API Version**: Google Tenor API v2
**Status**: Ready for Render Deployment
