# Fetch History Feature

## Overview

The Fetch History feature provides comprehensive tracking and visualization of all API requests and responses in the Blueprint Snap application. It automatically logs every API call with detailed metadata including request/response data, timing, and status codes.

## Architecture

### Backend Components

#### 1. Database Schema (`supabase/migrations/20241004_fetch_history.sql`)
- **Table**: `fetch_history`
- **Columns**:
  - `id`: UUID (Primary Key)
  - `user_id`: UUID (Foreign Key to auth.users)
  - `endpoint`: TEXT (API endpoint path)
  - `method`: TEXT (HTTP method: GET, POST, PUT, DELETE, PATCH)
  - `request_data`: JSONB (Request payload)
  - `response_data`: JSONB (Response data)
  - `status_code`: INTEGER (HTTP status code)
  - `duration_ms`: INTEGER (Request duration in milliseconds)
  - `error_message`: TEXT (Error message if request failed)
  - `created_at`: TIMESTAMP WITH TIME ZONE

#### 2. Models (`backend/app/models.py`)
- `FetchHistoryItem`: Represents a single history entry
- `FetchHistoryResponse`: Paginated response with history items
- `CreateFetchHistoryRequest`: Request model for creating history entries

#### 3. API Routes (`backend/app/api/routes/fetch_history.py`)

**Endpoints**:

- `GET /api/fetch-history` - Get paginated history with filters
  - Query params: `page`, `page_size`, `endpoint`, `method`, `status_code`
  - Returns: `FetchHistoryResponse`

- `GET /api/fetch-history/stats` - Get statistics about API usage
  - Returns: Aggregated stats including total requests, success rate, avg duration

- `POST /api/fetch-history` - Manually create a history entry
  - Body: `CreateFetchHistoryRequest`
  - Returns: Created entry ID

- `DELETE /api/fetch-history/{history_id}` - Delete a specific entry
  - Returns: Success status

- `DELETE /api/fetch-history` - Clear all history
  - Returns: Success status and deleted count

#### 4. Middleware (`backend/app/middleware/fetch_tracker.py`)
- **FetchTrackerMiddleware**: Automatically tracks all API requests
- Captures request/response data, timing, and errors
- Non-blocking logging (doesn't affect request performance)
- Skips tracking for health checks and static endpoints

### Frontend Components

#### 1. Types (`frontend/src/types.ts`)
- `FetchHistoryItem`: TypeScript interface for history items
- `FetchHistoryResponse`: Paginated response interface
- `FetchHistoryStats`: Statistics interface

#### 2. API Service (`frontend/src/services/fetchHistory.ts`)
- `fetchHistoryApi.getHistory()`: Fetch paginated history with filters
- `fetchHistoryApi.getStats()`: Get statistics
- `fetchHistoryApi.deleteItem()`: Delete a specific entry
- `fetchHistoryApi.clearHistory()`: Clear all history

#### 3. UI Component (`frontend/src/components/FetchHistoryViewer.tsx`)

**Features**:
- **Split View**: List view on left, detail view on right
- **Statistics Dashboard**: Shows total requests, success rate, errors, avg duration
- **Filtering**: Filter by endpoint, HTTP method, status code
- **Pagination**: Navigate through large history datasets
- **Color Coding**:
  - HTTP methods: Different colors for GET, POST, PUT, PATCH, DELETE
  - Status codes: Green (2xx), Blue (3xx), Yellow (4xx), Red (5xx)
- **Detail View**: 
  - Full request/response JSON
  - Timing information
  - Error messages
  - Formatted timestamps
- **Actions**:
  - Delete individual entries
  - Clear all history
  - Refresh data

#### 4. App Integration (`frontend/src/App.tsx`)
- Added "Fetch History" button in header
- Toggle between main view, preferences, and history
- Full-screen history viewer with proper height constraints

## Usage

### Accessing Fetch History

1. Click the "Fetch History" button in the application header
2. The history viewer will display all tracked API requests
3. Use filters to narrow down results by endpoint or method
4. Click on any item in the list to view full details

### Understanding the Data

**List View**:
- Shows HTTP method badge with color coding
- Displays endpoint path
- Shows status code with color coding
- Displays timestamp and duration
- Shows error messages if request failed

**Detail View**:
- Complete endpoint information
- HTTP method and status code
- Request duration
- Full request payload (formatted JSON)
- Full response data (formatted JSON)
- Error details if applicable

**Statistics Dashboard**:
- Total number of requests
- Success rate percentage
- Error count
- Average request duration
- Breakdown by HTTP method
- Breakdown by endpoint
- Breakdown by status code

### Managing History

**Delete Single Entry**:
1. Select an item from the list
2. Click "Delete" button in detail view

**Clear All History**:
1. Click "Clear History" button in stats bar
2. Confirm the action

## Implementation Details

### Automatic Tracking

The `FetchTrackerMiddleware` automatically tracks all requests to `/api/*` endpoints except:
- `/api/health`
- `/api/docs`
- `/api/openapi.json`
- `/api/fetch-history/*` (prevents recursive logging)

### Performance Considerations

- **Non-blocking**: History logging happens asynchronously
- **Error handling**: Logging failures don't affect API requests
- **Pagination**: Large datasets are paginated for efficient loading
- **Indexes**: Database indexes on commonly queried fields
- **Selective capture**: Response data capture is limited to prevent memory issues

### Data Retention

Currently, there's no automatic cleanup of old history entries. Consider implementing:
- Scheduled cleanup job for entries older than X days
- Max row limits with auto-deletion of oldest entries
- Data archival to separate storage

## Development

### Running Migrations

```bash
# Apply the fetch history migration
cd supabase
supabase db push
```

### Testing the Feature

1. **Backend**: 
   ```bash
   cd backend
   python -m pytest tests/test_fetch_history.py
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Manual Testing**:
   - Generate a plan
   - Use Ask Copilot
   - Check fetch history to see tracked requests

### Adding Custom Tracking

To manually track a custom event:

```typescript
// Frontend
import { fetchHistoryApi } from './services/fetchHistory'

await fetchHistoryApi.createEntry({
  endpoint: '/api/custom-action',
  method: 'POST',
  request_data: { action: 'custom' },
  status_code: 200,
  duration_ms: 150
})
```

## Future Enhancements

- [ ] Export history to CSV/JSON
- [ ] Advanced filtering (date ranges, duration thresholds)
- [ ] Request replay functionality
- [ ] Performance analytics and trends
- [ ] Request diffing (compare similar requests)
- [ ] User-specific history filtering
- [ ] Search functionality for request/response content
- [ ] Favorites/bookmarking important requests
- [ ] Request grouping by session or plan
- [ ] Real-time updates using WebSockets

## Troubleshooting

**History not showing up**:
- Check that the migration has been applied
- Verify middleware is registered in `backend/app/main.py`
- Check browser console for API errors
- Verify Supabase connection

**Performance issues**:
- Check database indexes are created
- Consider implementing pagination limits
- Review response data capture size
- Implement data retention policies

**Missing data**:
- Verify middleware isn't skipping the endpoint
- Check for errors in backend logs
- Ensure request body parsing is working

## Security Considerations

- **Sensitive Data**: Be careful about logging sensitive information (passwords, tokens, etc.)
- **Access Control**: Consider adding user-based filtering if multi-tenant
- **Data Privacy**: Implement data retention policies to comply with privacy regulations
- **Audit Trail**: History can serve as an audit log for compliance

## Related Documentation

- [Backend API Documentation](./README.md)
- [Frontend Components](./frontend/README.md)
- [Database Schema](./supabase/schema.sql)
- [Coding Preferences](./CODING_PREFERENCES_README.md)
