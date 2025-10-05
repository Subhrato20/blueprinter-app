# Fetch History - Quick Start Guide

## 🚀 Getting Started

### 1. Apply Database Migration

```bash
cd supabase
supabase db push
```

### 2. Start the Application

```bash
# Terminal 1 - Backend
./run_backend.sh

# Terminal 2 - Frontend  
./run_frontend.sh
```

### 3. Access the Feature

Open http://localhost:5173 and click **"Fetch History"** in the header.

## 🔧 API Endpoints

### Get History (with pagination)
```bash
curl http://localhost:8000/api/fetch-history?page=1&page_size=50
```

### Get History (with filters)
```bash
curl "http://localhost:8000/api/fetch-history?endpoint=/api/plan&method=POST"
```

### Get Statistics
```bash
curl http://localhost:8000/api/fetch-history/stats
```

### Create Manual Entry
```bash
curl -X POST http://localhost:8000/api/fetch-history \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "/api/test",
    "method": "GET",
    "status_code": 200,
    "duration_ms": 150
  }'
```

### Delete Entry
```bash
curl -X DELETE http://localhost:8000/api/fetch-history/{history_id}
```

### Clear All History
```bash
curl -X DELETE http://localhost:8000/api/fetch-history
```

## 🎯 How It Works

1. **Automatic Tracking**: The `FetchTrackerMiddleware` automatically logs every API request
2. **Storage**: Data is stored in the `fetch_history` table in Supabase
3. **Visualization**: The `FetchHistoryViewer` component displays the data with rich filtering

## 📊 What Gets Tracked

- ✅ Endpoint path
- ✅ HTTP method (GET, POST, PUT, DELETE, PATCH)
- ✅ Request payload (JSON)
- ✅ Response data (JSON)
- ✅ Status code
- ✅ Duration (milliseconds)
- ✅ Error messages
- ✅ Timestamp

## 🔍 Using the UI

### Statistics Dashboard
Shows at the top of the history viewer:
- Total requests
- Success rate (%)
- Error count
- Average duration

### Filters
- **Endpoint**: Search by endpoint path
- **Method**: Filter by HTTP method (GET, POST, etc.)

### List View (Left Panel)
- Color-coded method badges
- Status code indicators (green=success, red=error)
- Duration timing
- Timestamp

### Detail View (Right Panel)
Click any item to see:
- Full request JSON
- Full response JSON
- Complete metadata
- Delete button

## 🎨 Color Coding

### HTTP Methods
- **GET**: Blue
- **POST**: Green
- **PUT**: Yellow
- **PATCH**: Purple
- **DELETE**: Red

### Status Codes
- **2xx**: Green (Success)
- **3xx**: Blue (Redirect)
- **4xx**: Yellow (Client Error)
- **5xx**: Red (Server Error)

## 💡 Tips

1. **Generate a Plan** - This creates several API requests to track
2. **Use Ask Copilot** - This adds more entries with request/response data
3. **Apply Filters** - Narrow down to specific endpoints or methods
4. **Check Stats** - See your API usage patterns
5. **Export Data** - Copy JSON from detail view for analysis

## 🐛 Troubleshooting

**No history showing up?**
- Check that migration was applied: `supabase db push`
- Verify backend is running: `curl http://localhost:8000/health`
- Check browser console for errors

**Middleware not tracking?**
- Verify middleware is registered in `backend/app/main.py`
- Check that request path starts with `/api/`
- Look for excluded paths in `fetch_tracker.py`

**Slow performance?**
- Check database indexes are created
- Limit page size to 20-50 items
- Clear old history entries

## 📖 More Information

- **Full Documentation**: See `FETCH_HISTORY_README.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **API Docs**: http://localhost:8000/docs (when backend is running)

## ✅ Verification Checklist

- [ ] Migration applied successfully
- [ ] Backend server running
- [ ] Frontend server running
- [ ] Can access http://localhost:5173
- [ ] "Fetch History" button visible in header
- [ ] Can generate a plan (creates history entries)
- [ ] History entries appear in viewer
- [ ] Statistics show correct data
- [ ] Filters work properly
- [ ] Can delete entries
- [ ] Detail view shows JSON data

---

**Need Help?** Check the main documentation files or open an issue on GitHub.
